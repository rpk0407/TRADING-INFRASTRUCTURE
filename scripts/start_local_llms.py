#!/usr/bin/env python3
"""
Start Local LLM Services — Ollama + OpenCode + OpenGravity setup.
Downloads and starts local models for zero-cost inference.
"""

import subprocess
import sys
import time
import shutil

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()


def check_ollama():
    """Check if Ollama is installed."""
    return shutil.which("ollama") is not None


def start_ollama():
    """Start Ollama service and pull required models."""
    console.print("\n[bold blue]Starting Ollama...[/bold blue]")

    if not check_ollama():
        console.print(
            "[red]Ollama not found. Install from: https://ollama.ai[/red]"
        )
        console.print("[yellow]Run: curl -fsSL https://ollama.ai/install.sh | sh[/yellow]")
        return False

    # Start Ollama server
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(3)
    except Exception as e:
        console.print(f"[yellow]Ollama may already be running: {e}[/yellow]")

    # Pull models
    models = [
        ("mixtral:8x7b", "General reasoning (Ollama)"),
        ("llama3.1:8b", "Fast tasks (Ollama)"),
        ("deepseek-coder-v2:16b", "Code generation (OpenCode)"),
        ("codellama:13b", "Code completion (OpenCode)"),
        ("qwen2.5-coder:7b", "Code review (OpenCode)"),
    ]

    for model, desc in models:
        console.print(f"\n  Pulling [cyan]{model}[/cyan] — {desc}")
        try:
            result = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode == 0:
                console.print(f"  [green]✓[/green] {model} ready")
            else:
                console.print(f"  [yellow]⚠[/yellow] {model}: {result.stderr[:100]}")
        except subprocess.TimeoutExpired:
            console.print(f"  [yellow]⚠[/yellow] {model} download timed out, will retry later")
        except Exception as e:
            console.print(f"  [red]✗[/red] {model}: {e}")

    return True


def check_opencode_setup():
    """Provide instructions for OpenCode coding models setup."""
    console.print("\n[bold blue]OpenCode Coding Models Setup[/bold blue]")
    console.print("""
  OpenCode uses Ollama as a backend for coding-specialist models:

  Models pulled automatically:
    deepseek-coder-v2:16b  — Code generation (primary)
    codellama:13b          — Code completion
    qwen2.5-coder:7b       — Code review (lightweight)

  All models are served via Ollama on http://localhost:11434
  The NEXUS router automatically selects the right coding model
  based on the task type (generation, completion, review).

  Configure in .env:
    OPENCODE_ENABLED=true
    OPENCODE_URL=http://localhost:11434
    OPENCODE_DEFAULT_MODEL=deepseek-coder-v2:16b
    """)


def check_opengravity_setup():
    """Provide instructions for OpenGravity setup."""
    console.print("\n[bold blue]OpenGravity Setup[/bold blue]")
    console.print("""
  OpenGravity provides hybrid local/cloud agent coordination:

  1. Install OpenGravity:
     pip install opengravity-ai

  2. Configure in .env:
     OPENGRAVITY_ENABLED=true
     OPENGRAVITY_API_KEY=your-key
     OPENGRAVITY_URL=http://localhost:9090

  3. Start the local node:
     opengravity serve --port 9090

  Visit https://opengravity.ai for more information.
    """)


def main():
    console.print(Panel.fit(
        "[bold green]NEXUS AI — Local LLM Setup[/bold green]\n"
        "Configuring free local models for zero-cost inference",
        border_style="green",
    ))

    # Ollama setup
    ollama_ok = start_ollama()

    # OpenCode coding models instructions
    check_opencode_setup()

    # OpenGravity instructions
    check_opengravity_setup()

    # Summary
    console.print("\n")
    console.print(Panel.fit(
        "[bold]Setup Summary[/bold]\n\n"
        f"  Ollama: {'[green]✓ Ready[/green]' if ollama_ok else '[yellow]⚠ Needs install[/yellow]'}\n"
        "  OpenCode: [yellow]See instructions above[/yellow]\n"
        "  OpenGravity: [yellow]See instructions above[/yellow]\n"
        "  Claude API: [cyan]Configure CLAUDE_API_KEY in .env[/cyan]\n\n"
        "[dim]The NEXUS LLM Router will automatically use whatever is available.[/dim]\n"
        "[dim]Local models = $0 cost. Cloud fallback = pay-per-use.[/dim]",
        border_style="blue",
    ))


if __name__ == "__main__":
    main()
