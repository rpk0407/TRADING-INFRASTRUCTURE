"""
Task Queue — Priority-based task scheduling for agent execution.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class TaskPriority(IntEnum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class TaskStatus(str):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(order=True)
class Task:
    priority: int
    task_id: str = field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}", compare=False)
    agent_id: str = field(default="", compare=False)
    workflow_id: str = field(default="", compare=False)
    task_type: str = field(default="", compare=False)
    params: dict = field(default_factory=dict, compare=False)
    status: str = field(default=TaskStatus.PENDING, compare=False)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc), compare=False
    )
    result: Optional[Any] = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)
    retry_count: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)


class TaskQueue:
    """
    Async priority queue for managing agent tasks.
    Supports priorities, retries, and task tracking.
    """

    def __init__(self, max_size: int = 1000):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_size)
        self._tasks: dict[str, Task] = {}
        self._completed: list[Task] = []

    async def enqueue(self, task: Task) -> str:
        """Add a task to the queue."""
        self._tasks[task.task_id] = task
        task.status = TaskStatus.QUEUED
        await self._queue.put(task)
        logger.debug(
            "task.enqueued",
            task_id=task.task_id,
            agent=task.agent_id,
            priority=task.priority,
        )
        return task.task_id

    async def dequeue(self) -> Task:
        """Get the highest priority task."""
        task = await self._queue.get()
        task.status = TaskStatus.RUNNING
        return task

    def complete(self, task_id: str, result: Any = None):
        """Mark a task as completed."""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.result = result
            self._completed.append(task)
            logger.debug("task.completed", task_id=task_id)

    def fail(self, task_id: str, error: str):
        """Mark a task as failed."""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.retry_count += 1
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.QUEUED
                task.error = error
                logger.warning(
                    "task.retry",
                    task_id=task_id,
                    retry=task.retry_count,
                    error=error,
                )
            else:
                task.status = TaskStatus.FAILED
                task.error = error
                logger.error(
                    "task.failed",
                    task_id=task_id,
                    error=error,
                    retries=task.retry_count,
                )

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def get_stats(self) -> dict:
        """Queue statistics."""
        statuses = {}
        for task in self._tasks.values():
            statuses[task.status] = statuses.get(task.status, 0) + 1
        return {
            "total": len(self._tasks),
            "queued": self._queue.qsize(),
            "completed": len(self._completed),
            "by_status": statuses,
        }

    @property
    def pending_count(self) -> int:
        return self._queue.qsize()
