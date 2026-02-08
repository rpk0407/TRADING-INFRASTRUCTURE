"""
WebSocket — Real-time workflow progress streaming.
Clients can subscribe to workflow updates and see agents working live.
"""

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections per workflow."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workflow_id: str):
        await websocket.accept()
        self.active_connections.setdefault(workflow_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, workflow_id: str):
        if workflow_id in self.active_connections:
            self.active_connections[workflow_id] = [
                ws for ws in self.active_connections[workflow_id]
                if ws != websocket
            ]

    async def broadcast(self, workflow_id: str, message: dict):
        if workflow_id in self.active_connections:
            dead = []
            for ws in self.active_connections[workflow_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.disconnect(ws, workflow_id)


manager = ConnectionManager()


@router.websocket("/workflow/{workflow_id}")
async def workflow_stream(websocket: WebSocket, workflow_id: str):
    """
    Stream real-time workflow progress.

    Events:
    - workflow.started: Workflow execution begins
    - workflow.stage: New execution stage starting
    - agent.started: Agent begins executing
    - agent.progress: Agent progress update
    - agent.completed: Agent finished
    - agent.error: Agent encountered an error
    - workflow.completed: All agents finished
    - workflow.error: Workflow-level error
    """
    await manager.connect(websocket, workflow_id)
    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, workflow_id)


@router.websocket("/dashboard/{client_id}")
async def dashboard_stream(websocket: WebSocket, client_id: str):
    """Stream real-time updates for a client's dashboard."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
