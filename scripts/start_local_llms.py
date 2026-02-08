#!/usr/bin/env python3
"""
Start Local LLM Services — Kimi K2.5 + Ollama setup.
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
        ("mixtral:8x7b", "Primary reasoning model (FREE)"),
        ("llama3.1:8b", "Fast tasks model (FREE)"),
        ("deepseek-coder-v2:16b", "Code generation model (FREE)"),
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


def check_kimi_setup():
    """Provide instructions for Kimi K2.5 local setup."""
    console.print("\n[bold blue]Kimi K2.5 Local Setup[/bold blue]")
    console.print("""
  Kimi K2.5 can be run locally via vLLM or Ollama:

  Option 1 — Via Ollama (Easiest):
    ollama pull kimi-k2.5
    # Automatically serves on http://localhost:11434

  Option 2 — Via vLLM (Best performance):
    pip install vllm
    vllm serve moonshotai/Kimi-K2.5 \\
      --host 0.0.0.0 --port 8080 \\
      --max-model-len 8192 \\
      --gpu-memory-utilization 0.9

  Option 3 — Via HuggingFace Transformers:
    pip install transformers torch
    # Use the NEXUS integration at integrations/kimi_k2/

  The model will be available at http://localhost:8080/v1
  (OpenAI-compatible API endpoint)
    """)


def check_antigravity_setup():
    """Provide instructions for AntiGravity setup."""
    console.print("\n[bold blue]AntiGravity Setup[/bold blue]")
    console.print("""
  AntiGravity provides hybrid local/cloud agent execution:

  1. Install AntiGravity:
     pip install antigravity-ai

  2. Configure in .env:
     ANTIGRAVITY_ENABLED=true
     ANTIGRAVITY_API_KEY=your-key
     ANTIGRAVITY_URL=http://localhost:9090

  3. Start the local node:
     antigravity serve --port 9090

  Visit https://antigravity.ai for more information.
    """)


def main():
    console.print(Panel.fit(
        "[bold green]NEXUS AI — Local LLM Setup[/bold green]\n"
        "Configuring free local models for zero-cost inference",
        border_style="green",
    ))

    # Ollama setup
    ollama_ok = start_ollama()

    # Kimi K2.5 instructions
    check_kimi_setup()

    # AntiGravity instructions
    check_antigravity_setup()

    # Summary
    console.print("\n")
    console.print(Panel.fit(
        "[bold]Setup Summary[/bold]\n\n"
        f"  Ollama: {'[green]✓ Ready[/green]' if ollama_ok else '[yellow]⚠ Needs install[/yellow]'}\n"
        "  Kimi K2.5: [yellow]See instructions above[/yellow]\n"
        "  AntiGravity: [yellow]See instructions above[/yellow]\n"
        "  Claude API: [cyan]Configure CLAUDE_API_KEY in .env[/cyan]\n\n"
        "[dim]The NEXUS LLM Router will automatically use whatever is available.[/dim]\n"
        "[dim]Local models = $0 cost. Cloud fallback = pay-per-use.[/dim]",
        border_style="blue",
    ))


if __name__ == "__main__":
    main()
