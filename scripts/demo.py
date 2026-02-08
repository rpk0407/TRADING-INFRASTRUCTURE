#!/usr/bin/env python3
"""
NEXUS AI — Demo Script
Demonstrates a full business setup workflow.
"""

import asyncio
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


async def run_demo():
    console.print(Panel.fit(
        "[bold green]NEXUS AI — Full Business Setup Demo[/bold green]\n"
        "Watch as 8 AI agents build an entire business infrastructure",
        border_style="green",
    ))

    # Example client configuration
    demo_client = {
        "client_id": "demo_001",
        "workflow_type": "full_setup",
        "params": {
            "business_name": "CloudPeak Analytics",
            "industry": "SaaS / Data Analytics",
            "description": (
                "AI-powered business analytics platform that helps "
                "mid-market companies make data-driven decisions. "
                "Features include real-time dashboards, predictive "
                "analytics, and automated reporting."
            ),
            "target_audience": "CTOs and VPs of Data at companies with 50-500 employees",
            "goals": [
                "Launch website and establish web presence",
                "Generate 100 qualified leads in first 3 months",
                "Achieve 5% trial-to-paid conversion rate",
                "Reduce customer support tickets by 40%",
            ],
            "products": [
                "CloudPeak Pro - $99/mo",
                "CloudPeak Enterprise - $499/mo",
                "CloudPeak API - Usage-based pricing",
            ],
            "colors": "#2563eb, #1e40af, #f59e0b",
            "style": "modern professional tech",
            "competitors": ["Tableau", "Looker", "Mode Analytics"],
            "current_revenue": "$50K MRR",
            "current_customers": 120,
            "team_size": 15,
            "marketing_budget": "$10,000/month",
            "features": [
                "contact_form", "blog", "pricing_page",
                "demo_booking", "customer_portal", "api_docs",
            ],
        },
    }

    console.print("\n[bold]Client Configuration:[/bold]")
    config_table = Table(show_header=False, border_style="dim")
    config_table.add_column("Field", style="cyan")
    config_table.add_column("Value")
    for key, value in demo_client["params"].items():
        display_val = str(value)
        if len(display_val) > 80:
            display_val = display_val[:80] + "..."
        config_table.add_row(key, display_val)
    console.print(config_table)

    console.print("\n[bold yellow]Workflow Execution Plan:[/bold yellow]")
    console.print("""
  Stage 1: [cyan]Website Builder[/cyan]
           → Generate complete Next.js website with all pages

  Stage 2: [cyan]Content Engine[/cyan] + [cyan]SEO Agent[/cyan] (parallel)
           → Brand voice, blog posts, email sequences
           → Keyword research, technical SEO, schema markup

  Stage 3: [cyan]Marketing Agent[/cyan] + [cyan]CRM Agent[/cyan] (parallel)
           → Marketing strategy, campaigns, budget allocation
           → Lead scoring, customer journeys, automation

  Stage 4: [cyan]Support Agent[/cyan] + [cyan]Business Automator[/cyan] (parallel)
           → FAQ, chatbot flows, knowledge base
           → Workflow automation, document templates

  Stage 5: [cyan]Growth Analytics[/cyan]
           → Revenue forecast, market analysis, growth playbook
    """)

    console.print("[bold green]To execute this demo, start the NEXUS server:[/bold green]")
    console.print("""
  1. Configure .env with at least one LLM provider
  2. python -m api.server
  3. POST to /api/v1/workflows/ with the above configuration
  4. Watch agents work in real-time via WebSocket

  Or use the CLI:
    python -m core.orchestrator.nexus --demo
    """)

    # Show expected outputs
    console.print("\n[bold]Expected Deliverables:[/bold]")
    deliverables = Table(border_style="dim")
    deliverables.add_column("Agent", style="cyan")
    deliverables.add_column("Deliverables")
    deliverables.add_column("Est. Cost")

    deliverables.add_row(
        "Website Builder",
        "Complete Next.js site (6+ pages, components, styles)",
        "$0.00",
    )
    deliverables.add_row(
        "Content Engine",
        "Brand voice guide, 30-day calendar, 3 blogs, email sequence, social posts, ad copy",
        "$0.00",
    )
    deliverables.add_row(
        "SEO Agent",
        "20+ keywords, technical audit, on-page optimization, schema markup, link strategy",
        "$0.00",
    )
    deliverables.add_row(
        "Marketing Agent",
        "Competitor analysis, audience segments, strategy, 3 campaigns, budget plan",
        "$0.00",
    )
    deliverables.add_row(
        "CRM Agent",
        "Lead scoring model, customer journeys, 5 automations, pipeline, churn prevention",
        "$0.00",
    )
    deliverables.add_row(
        "Support Agent",
        "15-20 FAQs, chatbot flows, response templates, routing rules, knowledge base",
        "$0.00",
    )
    deliverables.add_row(
        "Business Automator",
        "Process audit, workflow automations, document templates, integration plan, ROI",
        "$0.00",
    )
    deliverables.add_row(
        "Growth Analytics",
        "Market analysis, unit economics, 12-month forecast (3 scenarios), experiments, playbook",
        "$0.00*",
    )

    console.print(deliverables)
    console.print(
        "\n[dim]* $0.00 when using local models (Kimi K2.5 + Ollama). "
        "Claude API fallback costs ~$0.50-2.00 per full workflow.[/dim]"
    )


if __name__ == "__main__":
    asyncio.run(run_demo())
