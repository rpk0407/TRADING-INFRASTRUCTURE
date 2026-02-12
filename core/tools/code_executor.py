"""
Sandboxed Code Executor — Lets agents generate and run code safely.

Used by:
- Website Builder: validate generated components
- Growth Analytics: run data analysis scripts
- Business Automation: test workflow logic
- Any agent that needs to verify its output works
"""

import asyncio
import os
import tempfile
import uuid
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


class CodeExecutor:
    """
    Safely executes generated code in isolated subprocesses.
    Supports Python, Node.js, and shell scripts.
    """

    LANGUAGE_COMMANDS = {
        "python": ["python3", "-c"],
        "javascript": ["node", "-e"],
        "typescript": ["npx", "tsx", "-e"],
        "shell": ["bash", "-c"],
    }

    # Safety limits
    MAX_EXECUTION_TIME = 30  # seconds
    MAX_OUTPUT_SIZE = 50_000  # chars
    BLOCKED_IMPORTS = [
        "subprocess", "shutil.rmtree", "os.system", "os.remove",
        "os.rmdir", "__import__", "eval(", "exec(",
    ]

    def __init__(self, work_dir: Optional[str] = None):
        self._work_dir = work_dir or tempfile.mkdtemp(prefix="nexus_exec_")
        os.makedirs(self._work_dir, exist_ok=True)

    def __del__(self):
        """Cleanup temp directory on garbage collection."""
        try:
            self.cleanup()
        except Exception:
            pass

    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: int = None,
    ) -> dict:
        """
        Execute code in a sandboxed subprocess.

        Returns:
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "exit_code": int,
                "execution_time_ms": float,
            }
        """
        timeout = timeout or self.MAX_EXECUTION_TIME

        # Safety check
        safety = self._safety_check(code, language)
        if not safety["safe"]:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Safety violation: {safety['reason']}",
                "exit_code": -1,
                "execution_time_ms": 0,
            }

        cmd = self.LANGUAGE_COMMANDS.get(language)
        if not cmd:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Unsupported language: {language}",
                "exit_code": -1,
                "execution_time_ms": 0,
            }

        logger.info(
            "executor.running",
            language=language,
            code_length=len(code),
        )

        try:
            import time
            start = time.monotonic()

            proc = await asyncio.create_subprocess_exec(
                *cmd, code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self._work_dir,
                env=self._safe_env(),
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout,
            )

            elapsed_ms = (time.monotonic() - start) * 1000

            stdout_str = stdout.decode("utf-8", errors="replace")[:self.MAX_OUTPUT_SIZE]
            stderr_str = stderr.decode("utf-8", errors="replace")[:self.MAX_OUTPUT_SIZE]

            result = {
                "success": proc.returncode == 0,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": proc.returncode,
                "execution_time_ms": round(elapsed_ms, 2),
            }

            logger.info(
                "executor.completed",
                success=result["success"],
                time_ms=result["execution_time_ms"],
            )
            return result

        except asyncio.TimeoutError:
            proc.kill()
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout}s",
                "exit_code": -1,
                "execution_time_ms": timeout * 1000,
            }
        except Exception as e:
            logger.error("executor.error", error=str(e))
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "execution_time_ms": 0,
            }

    async def execute_file(
        self,
        filename: str,
        content: str,
        language: str = "python",
    ) -> dict:
        """Write code to a file and execute it."""
        filepath = os.path.join(self._work_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)

        file_commands = {
            "python": ["python3", filepath],
            "javascript": ["node", filepath],
            "typescript": ["npx", "tsx", filepath],
            "shell": ["bash", filepath],
        }

        cmd = file_commands.get(language)
        if not cmd:
            return {"success": False, "stderr": f"Unsupported: {language}"}

        try:
            import time
            start = time.monotonic()

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self._work_dir,
                env=self._safe_env(),
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.MAX_EXECUTION_TIME,
            )

            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace")[:self.MAX_OUTPUT_SIZE],
                "stderr": stderr.decode("utf-8", errors="replace")[:self.MAX_OUTPUT_SIZE],
                "exit_code": proc.returncode,
                "execution_time_ms": round((time.monotonic() - start) * 1000, 2),
                "file": filepath,
            }
        except asyncio.TimeoutError:
            proc.kill()
            return {"success": False, "stderr": "Timeout", "exit_code": -1}

    async def validate_json(self, json_str: str) -> dict:
        """Validate that a string is valid JSON."""
        import json
        try:
            parsed = json.loads(json_str)
            return {
                "valid": True,
                "type": type(parsed).__name__,
                "keys": list(parsed.keys()) if isinstance(parsed, dict) else None,
                "length": len(parsed) if isinstance(parsed, (list, dict)) else None,
            }
        except json.JSONDecodeError as e:
            return {"valid": False, "error": str(e)}

    async def validate_html(self, html: str) -> dict:
        """Basic HTML validation."""
        issues = []
        # Check for unclosed tags
        open_tags = []
        import re
        for match in re.finditer(r"<(/?)(\w+)[^>]*>", html):
            is_close = match.group(1) == "/"
            tag = match.group(2).lower()
            if tag in ("br", "hr", "img", "input", "meta", "link"):
                continue
            if is_close:
                if open_tags and open_tags[-1] == tag:
                    open_tags.pop()
                else:
                    issues.append(f"Unexpected closing tag: </{tag}>")
            else:
                open_tags.append(tag)

        for tag in open_tags:
            issues.append(f"Unclosed tag: <{tag}>")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "tag_count": len(re.findall(r"<\w+", html)),
        }

    def _safety_check(self, code: str, language: str) -> dict:
        """Check code for dangerous patterns."""
        if language == "python":
            for blocked in self.BLOCKED_IMPORTS:
                if blocked in code:
                    return {
                        "safe": False,
                        "reason": f"Blocked pattern: {blocked}",
                    }

        # Check for file system access patterns
        dangerous = [
            "rm -rf", "rmdir /s", "del /f",
            "DROP TABLE", "DELETE FROM",
            "curl | sh", "wget | sh",
        ]
        for pattern in dangerous:
            if pattern.lower() in code.lower():
                return {"safe": False, "reason": f"Dangerous: {pattern}"}

        return {"safe": True, "reason": ""}

    def _safe_env(self) -> dict:
        """Create a restricted environment for subprocess."""
        safe = {
            "PATH": os.environ.get("PATH", "/usr/bin:/usr/local/bin"),
            "HOME": self._work_dir,
            "TMPDIR": self._work_dir,
            "LANG": "en_US.UTF-8",
        }
        return safe

    def cleanup(self):
        """Clean up work directory."""
        import shutil
        if os.path.exists(self._work_dir):
            shutil.rmtree(self._work_dir, ignore_errors=True)
