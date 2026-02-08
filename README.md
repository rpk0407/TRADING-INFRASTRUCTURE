# NEXUS AI — Agentic Workflow Infrastructure

> **Not another chatbot wrapper.** NEXUS is a full-stack autonomous agent orchestration platform that builds, runs, and evolves entire business operations — websites, marketing, CRM, analytics, support — using locally-hosted LLMs to keep costs near zero.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT DASHBOARD                             │
│   Real-time agent monitoring · Growth projections · One-click ops   │
├─────────────────────────────────────────────────────────────────────┤
│                          API GATEWAY                                │
│          REST + WebSocket · Auth · Rate limiting · Webhooks         │
├─────────────────────────────────────────────────────────────────────┤
│                    NEXUS ORCHESTRATOR CORE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Agent Graph  │  │  Task Queue  │  │  Memory / State Manager  │  │
│  │  (DAG-based)  │  │  (Priority)  │  │  (Persistent Context)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                     INTELLIGENT LLM ROUTER                          │
│  Routes tasks to cheapest capable model · Fallback chains           │
│  ┌─────────┐  ┌──────────┐  ┌──────────────┐  ┌───────────────┐   │
│  │  Kimi   │  │ Ollama   │  │  AntiGravity │  │  Claude API   │   │
│  │  K2.5   │  │ (Local)  │  │  (Hybrid)    │  │  (Fallback)   │   │
│  │  LOCAL  │  │  Mixtral  │  │              │  │  Opus/Sonnet  │   │
│  └─────────┘  └──────────┘  └──────────────┘  └───────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                      AGENT FLEET                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Website  │ │Marketing │ │   CRM    │ │   SEO    │ │ Support  │ │
│  │ Builder  │ │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │ │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤ │
│  │ Content  │ │ Growth   │ │ Business │ │ Social   │ │ Workflow │ │
│  │ Engine   │ │Analytics │ │Automator │ │ Media    │ │ Builder  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                      SERVICES LAYER                                 │
│  Template Engine · Deployment Manager · Analytics Pipeline          │
│  Client Portal · Webhook Manager · Billing Integration              │
└─────────────────────────────────────────────────────────────────────┘
```

## What Makes NEXUS Different

| Feature | Basic AI Agents | NEXUS |
|---|---|---|
| LLM Usage | Single cloud API ($$$) | Smart routing across local + cloud models |
| Workflow | Linear chatbot flow | DAG-based multi-agent orchestration |
| Memory | Stateless / basic RAG | Persistent company context + learning |
| Output | Text responses | Full deployable artifacts (sites, campaigns, reports) |
| Growth | None | Predictive analytics + automated optimization |
| Cost | $500-5000/mo API fees | ~$20-50/mo (mostly local inference) |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp config/example.env .env

# Start local LLM services
python scripts/start_local_llms.py

# Launch the orchestrator
python -m core.orchestrator.nexus

# Start the API server
python -m api.server

# Open dashboard
python -m dashboard.server
```

## Agent Fleet

- **Website Builder** — Generates full websites from business descriptions (React, Next.js, static sites)
- **Content Engine** — Blog posts, product descriptions, email campaigns, social media content
- **Marketing Agent** — Campaign planning, A/B testing strategies, audience segmentation
- **CRM Agent** — Lead scoring, customer journey mapping, follow-up automation
- **SEO Agent** — Technical audits, keyword research, content optimization, link strategies
- **Growth Analytics** — Revenue forecasting, churn prediction, market opportunity analysis
- **Support Agent** — Customer support automation, FAQ generation, ticket routing
- **Business Automator** — Invoice generation, scheduling, inventory, custom workflows

## LLM Strategy (Cost Optimization)

1. **Kimi K2.5 (Local)** — Primary workhorse for reasoning, coding, and analysis
2. **Ollama Local Models** — Mixtral/Llama for simple tasks (content drafting, classification)
3. **AntiGravity** — Hybrid local/cloud for specialized agent tasks
4. **Claude API** — Fallback for complex reasoning requiring maximum capability

The intelligent router automatically selects the cheapest model that can handle each task.
