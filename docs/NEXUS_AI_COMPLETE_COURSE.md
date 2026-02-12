# NEXUS AI — The Complete Masterclass

> Everything you need to understand, run, and maximize every feature of your autonomous AI business platform.

---

## TABLE OF CONTENTS

1. [What is NEXUS AI?](#1-what-is-nexus-ai)
2. [The Big Picture — How Everything Connects](#2-the-big-picture)
3. [The 4 LLM Providers — Your AI Brain](#3-the-4-llm-providers)
4. [The Intelligent LLM Router — The Decision Maker](#4-the-intelligent-llm-router)
5. [The 8 AI Agents — Your Workforce](#5-the-8-ai-agents)
6. [The 4 Agent Tools — Real Actions, Not Just Words](#6-the-4-agent-tools)
7. [The Orchestrator — The Brain That Runs Everything](#7-the-orchestrator)
8. [The Client Lifecycle Engine — From Zero to Growth](#8-the-client-lifecycle-engine)
9. [The Feedback Loop — How NEXUS Gets Smarter](#9-the-feedback-loop)
10. [The Platform UI — Your Command Center](#10-the-platform-ui)
11. [The API Layer — Connecting Everything](#11-the-api-layer)
12. [Configuration Deep Dive](#12-configuration-deep-dive)
13. [How to Use NEXUS to Its Fullest Potential](#13-how-to-use-nexus-to-its-fullest)
14. [Pro Tips & Secret Weapons](#14-pro-tips-and-secret-weapons)
15. [Troubleshooting Guide](#15-troubleshooting-guide)

---

## 1. WHAT IS NEXUS AI?

NEXUS AI is not a chatbot. It's not a wrapper around ChatGPT. It is a **full autonomous business automation platform** that takes a company description and builds everything that company needs — a website, content strategy, marketing campaigns, CRM pipeline, SEO plan, growth analytics, customer support system, and automated business workflows.

### The Problem It Solves

Imagine a client comes to you and says: *"I just started a SaaS company. I need a website, blog content, marketing strategy, lead scoring, SEO, and analytics."*

Without NEXUS: You hire 6 different freelancers, spend weeks coordinating, pay thousands of dollars.

With NEXUS: You type in the business description, click "Full Business Setup", and 8 AI agents work together in parallel to deliver everything in 15-30 minutes. Cost: nearly $0 because it runs on local models.

### Who Is This For?

- **Agencies** that want to automate client delivery
- **Entrepreneurs** who want to launch businesses faster
- **Developers** who want to understand multi-agent AI systems
- **Anyone** who wants an AI workforce instead of an AI chatbot

---

## 2. THE BIG PICTURE — HOW EVERYTHING CONNECTS

Here's the flow of how NEXUS works, from start to finish:

```
CLIENT REQUEST
     │
     ▼
┌─────────────────────┐
│  FastAPI Server      │  ← Receives the request via REST API or WebSocket
│  (api/server.py)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  NEXUS Orchestrator  │  ← The brain — plans which agents to run and in what order
│  (core/orchestrator/ │
│   nexus.py)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Agent Graph (DAG)   │  ← Builds a dependency graph — who runs first, who runs in parallel
│  (agent_graph.py)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│  8 AGENTS EXECUTE (parallel where possible)      │
│                                                   │
│  Website Builder ──→ Content Engine ──→ SEO      │
│  Marketing ──→ CRM ──→ Support ──→ Automation    │
│  Growth Analytics (runs last, needs all data)     │
│                                                   │
│  Each agent calls:                                │
│    1. LLM Router (for AI thinking)                │
│    2. Tools (scraper, executor, browser, etc.)    │
└──────────┬──────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  LLM Router          │  ← Picks the cheapest model that can do the job
│  (core/llm_router/   │
│   router.py)         │
│                       │
│  Ollama (FREE) ──→ OpenCode (FREE) ──→ OpenGravity (~$0) ──→ Claude (paid)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Feedback Loop       │  ← Scores every output, learns which provider is best for what
│  (feedback_loop.py)  │
└──────────┬──────────┘
           │
           ▼
     DELIVERABLES
     (website code, content, strategies, reports)
```

### Key Insight: It's a Pipeline, Not a Chat

Traditional AI tools: User asks question → AI answers → done.

NEXUS: User describes business → Orchestrator plans → Agents execute in parallel → Tools validate → Feedback scores → Results delivered. **No human in the loop during execution.**

---

## 3. THE 4 LLM PROVIDERS — YOUR AI BRAIN

Every agent needs to "think" — that means calling an LLM (Large Language Model). NEXUS has 4 providers, ordered from cheapest to most expensive:

### Provider 1: Ollama (FREE — Local General Purpose)

**File:** `core/llm_router/router.py` → `_call_ollama()`

**What it is:** Ollama runs AI models directly on your computer. No API keys. No internet needed. No cost.

**Models:**
- `mixtral:8x7b` — For complex tasks (content writing, analysis, strategy). This is a "mixture of experts" model — 8 smaller models that work together.
- `llama3.1:8b` — For simple tasks (classification, tagging, summarization). Smaller but faster.

**How the router picks which model:**
```python
simple_tasks = {"classification", "summarization", "customer_support"}
model = settings.ollama_fast_model if task_type in simple_tasks else settings.ollama_default_model
```

If the task is simple → use the fast small model. If it's complex → use the big model. Both are FREE.

**When it's used:** Content drafting, summarization, SEO keyword analysis, customer support responses, general reasoning — basically 50%+ of all tasks.

**Setup:**
```bash
brew install ollama        # macOS
ollama serve               # Start the server
ollama pull mixtral:8x7b   # Download the complex model
ollama pull llama3.1:8b    # Download the fast model
```

---

### Provider 2: OpenCode (FREE — Local Coding Specialist)

**File:** `core/llm_router/router.py` → `_call_opencode()`
**Integration:** `integrations/opencode/client.py`

**What it is:** Three specialized coding models, all running locally via Ollama. When an agent needs to write code, review code, or complete code, it goes here instead of general Ollama.

**The 3 Coding Models:**

| Model | Purpose | When Used |
|-------|---------|-----------|
| `deepseek-coder-v2:16b` | Code generation & debugging | Website Builder generates pages, Growth Analytics writes validation scripts |
| `codellama:13b` | Code completion | Fill-in-the-middle, autocomplete-style tasks |
| `qwen2.5-coder:7b` | Code review | Reviewing generated code for quality, security, best practices |

**Smart routing by task type:**
```python
model_map = {
    "code_generation": settings.opencode_primary_model,    # DeepSeek
    "code_debugging": settings.opencode_primary_model,     # DeepSeek
    "code_completion": settings.opencode_completion_model,  # CodeLlama
    "code_review": settings.opencode_review_model,          # Qwen2.5
}
```

**Special behavior:** OpenCode automatically injects a coding system prompt if none exists:
```
"You are an expert software engineer. Write clean, production-ready code.
Follow best practices with proper error handling and types.
Return ONLY code unless asked for explanation."
```

It also uses lower temperature (0.2 minimum) for more deterministic code output.

**The OpenCode Client** (`integrations/opencode/client.py`) provides 6 specialized methods:
- `generate_code(prompt, language)` — Write new code from scratch
- `complete_code(code, cursor_position)` — Fill in missing parts
- `review_code(code, language)` — Get quality/security feedback
- `explain_code(code)` — Get plain-English explanation
- `debug_code(code, error)` — Find and fix bugs
- `refactor_code(code, goals)` — Improve existing code

**Setup:**
```bash
ollama pull deepseek-coder-v2:16b   # 9GB — primary code generation
ollama pull codellama:13b            # 7GB — code completion
ollama pull qwen2.5-coder:7b        # 4GB — code review
```

---

### Provider 3: OpenGravity (Near-Zero — Hybrid Local/Cloud)

**File:** `core/llm_router/router.py` → `_call_opengravity()`
**Integration:** `integrations/opengravity/client.py`

**What it is:** A hybrid platform that tries to run tasks locally first, and only uses cloud when necessary. Its specialty is **agent coordination** — making multiple AI agents work together.

**Key feature: `prefer_local` flag**
```python
body = {
    "messages": messages,
    "prefer_local": settings.opengravity_prefer_local,  # Default: True
}
```

When `prefer_local=True`, OpenGravity tries to handle the task on your machine. If it can't (too complex, needs specialized capabilities), it routes to cloud. This keeps costs near zero.

**The OpenGravity Client** provides:
- `chat(messages)` — General conversation
- `run_agent_task(task, agent_type)` — Run a specific agent task
- `coordinate_agents(agents, goal)` — Make multiple agents work together on a goal
- `execute_with_privacy(task, data)` — Run tasks without sending sensitive data to cloud
- `get_cost_report()` — See exactly what was local vs cloud and how much it cost

**When it's used:** Multi-agent coordination tasks, privacy-sensitive operations, complex planning that needs multiple model perspectives.

**Cost:** ~$0.0005/1K input tokens, ~$0.001/1K output tokens (only for cloud portion)

---

### Provider 4: Claude (Paid — Premium Fallback)

**File:** `core/llm_router/router.py` → `_call_claude()`

**What it is:** Anthropic's Claude API — the most capable model in the system. 200K context window, top-tier reasoning, tool use, vision.

**When it's used:** ONLY when local models can't handle the task. Complex multi-step planning, deep reasoning, critical decisions.

**Budget cap:** The system enforces a monthly spending limit:
```python
if self._monthly_spend >= settings.claude_monthly_budget_usd:
    logger.warning("llm_router.budget_exceeded")
    continue  # Skip Claude, try next provider
```

Default: $50/month. Once you hit the limit, Claude is disabled for the rest of the month and the system falls back to local models.

**Cost:** $0.003/1K input, $0.015/1K output

**Pro tip:** In practice, Claude should handle less than 10% of requests. If it's handling more, your local models need tuning.

---

## 4. THE INTELLIGENT LLM ROUTER — THE DECISION MAKER

**File:** `core/llm_router/router.py`

The router is the most important piece of the system. It decides which provider handles each request. Here's exactly how it works:

### Step 1: Check Cache

```python
if settings.llm_cache_enabled and not skip_cache:
    cache_key = self._cache_key(prompt, task_type, system_prompt)
    if cache_key in self._cache:
        return cached_response  # Instant, free
```

If someone asked the same question before, return the cached answer. Free and instant.

### Step 2: Select Providers (The Smart Part)

The router uses 3 strategies in order:

**Strategy A — Feedback Loop Preference:**
If the feedback loop has learned that Provider X is best for task type Y, use that first.
```python
if task_type in self._task_preferences:
    preferred = LLMProvider(self._task_preferences[task_type])
    return [preferred] + fallback_chain
```

**Strategy B — Capability Scoring:**
Every provider has capability scores. Every task type has requirements. The router matches them:

```
Provider Capabilities:
  Ollama:      reasoning=7, coding=5, creative=7, analysis=7
  OpenCode:    reasoning=6, coding=9, creative=4, analysis=6
  OpenGravity: reasoning=7, coding=7, creative=7, analysis=7
  Claude:      reasoning=10, coding=10, creative=9, analysis=10

Task Requirements:
  code_generation:    coding >= 8     → OpenCode wins (coding=9)
  code_review:        coding >= 7     → OpenCode wins (coding=9)
  content_creation:   creative >= 6   → Ollama wins (creative=7, cheapest)
  agent_coordination: planning >= 8   → OpenGravity wins
  complex_planning:   reasoning >= 9  → Claude wins (only one that qualifies)
```

**Strategy C — Cost Optimization:**
When multiple providers qualify, the router picks the cheapest one:
```python
if strategy == "cost_optimized":
    score = -cost * 1000 + capability_score  # Heavy penalty for cost
elif strategy == "quality_first":
    score = capability_score * 1000 - cost   # Quality matters most
else:
    score = capability_score - cost * 100    # Balanced
```

### Step 3: Try Providers in Order (Fallback Chain)

```
Attempt 1: Best match (usually Ollama or OpenCode) → SUCCESS? Done.
Attempt 2: Second best → SUCCESS? Done.
Attempt 3: Third option → SUCCESS? Done.
Attempt 4: Claude (premium fallback) → SUCCESS? Done.
All failed: Raise error.
```

### Step 4: Track Cost

After every response:
```python
costs = PROVIDER_COSTS[provider_id]
response.cost_usd = (tokens_in / 1000) * costs["input"] + (tokens_out / 1000) * costs["output"]
self._monthly_spend += response.cost_usd
```

Every single token is tracked. You always know exactly what you're spending.

### Health Checks

The router continuously monitors provider health:
- **Ollama:** Pings `http://localhost:11434/api/tags` — are models loaded?
- **OpenCode:** Checks if coding models exist in Ollama's model list
- **OpenGravity:** Pings `/health` endpoint, falls back to checking API key
- **Claude:** Checks if API key is configured

If a provider fails 5 times in a row, it's marked unavailable:
```python
if health.consecutive_failures >= 5:
    return False  # Skip this provider
```

---

## 5. THE 8 AI AGENTS — YOUR WORKFORCE

Every agent inherits from `BaseAgent` (`core/agents/base_agent.py`). Here's what that gives them:

### BaseAgent — The Foundation

```python
class BaseAgent:
    def __init__(self, agent_id, name, llm_router, memory_manager):
        self.llm_router = llm_router        # Access to all 4 providers
        self.memory = memory_manager          # Persistent memory
        self._scraper = None                  # Lazy-loaded tools
        self._executor = None
        self._reflection = None
        self._browser = None
```

**Key methods every agent has:**

| Method | What it does |
|--------|-------------|
| `think(prompt, task_type)` | Send a prompt to the LLM router — uses the best available model |
| `think_code(prompt)` | Force the request to OpenCode — for code-specific tasks |
| `think_with_reflection(prompt, task_type)` | Think, then use the reflection engine to improve the output |
| `scrape_url(url)` | Fetch and extract content from a webpage |
| `run_code(code, language)` | Execute code in a sandboxed environment |
| `execute(context)` | Main entry point — each agent overrides this |

**Lazy-loaded tools:** Tools are only created when first needed:
```python
@property
def scraper(self):
    if self._scraper is None:
        from core.tools.web_scraper import WebScraper
        self._scraper = WebScraper()
    return self._scraper
```

This means if an agent never needs the browser, it's never loaded. Saves memory.

---

### Agent 1: Website Builder

**File:** `core/agents/website_builder/agent.py`
**UI Page:** `/websites`

**What it does:** Takes a business description and generates a complete, deployable website.

**The execution flow:**
1. `_analyze_business()` — Understands what the business needs
2. `_plan_site_structure()` — Decides pages, navigation, layout
3. `_generate_pages()` — Writes actual HTML/React/Next.js code using `think_code()`
4. `_generate_components()` — Creates reusable UI components using `think_code()`
5. `_generate_styles()` — Creates Tailwind/CSS styling
6. `_validate_code()` — **Runs the generated code through CodeExecutor** to check for errors
7. `_create_config()` — Generates package.json, next.config.js, etc.

**What makes it special:** After generating code, it actually **validates** it:
```python
result = await self.executor.execute(check_script, language="javascript")
```
This catches syntax errors, missing imports, and broken components BEFORE delivering to the client.

**Output:** Complete website codebase — React/Next.js, Tailwind, components, config files, ready to `npm install && npm run dev`.

---

### Agent 2: Content Engine

**File:** `core/agents/content_engine/agent.py`
**UI Page:** `/content`

**What it does:** Creates a full content strategy with actual content pieces.

**The execution flow:**
1. `_develop_brand_voice()` — Creates a brand style guide (tone, vocabulary, personality)
2. `_research_topics()` — **Scrapes competitor websites** to find what content performs
3. `_create_content_calendar()` — 30-day content plan with topics, formats, channels
4. `_write_blog_posts()` — Full blog articles with SEO optimization
5. `_create_email_sequences()` — Nurture sequences for different customer stages
6. `_generate_social_content()` — Platform-specific social media posts
7. `_write_ad_copy()` — Google, Meta, LinkedIn ad variations

**What makes it special:** It uses `think_with_reflection()` for final content:
```python
result = await self.reflection.reflect_and_improve(draft_content, criteria)
```
The reflection engine reads the content, identifies weaknesses, and improves it. This means every piece of content goes through a quality check.

It also **scrapes real competitor URLs** before writing:
```python
fetched = await self.scraper.fetch_multiple(research_urls, extract_mode="text")
```
So the content is informed by real market data, not just LLM imagination.

---

### Agent 3: Marketing Strategist

**File:** `core/agents/marketing_agent/agent.py`
**UI Page:** `/marketing`

**What it does:** Creates comprehensive marketing strategy with competitive intelligence.

**The execution flow:**
1. `_analyze_competitors()` — **Scrapes competitor websites** for real intelligence
2. `_segment_audience()` — Creates detailed audience personas
3. `_plan_campaigns()` — Multi-channel campaign strategies
4. `_design_ab_tests()` — A/B testing frameworks
5. `_allocate_budget()` — Budget distribution across channels
6. `_create_kpi_framework()` — Measurable success metrics

**What makes it special:** Real competitor scraping:
```python
pages = await self.scraper.fetch_multiple(competitor_urls, extract_mode="full")
```
Instead of guessing what competitors do, it actually reads their websites and builds strategy from real data.

---

### Agent 4: CRM Automator

**File:** `core/agents/crm_agent/agent.py`
**UI Page:** `/crm`

**What it does:** Designs complete CRM systems with lead scoring and automation.

**The execution flow:**
1. `_score_leads()` — Creates scoring models (demographic + behavioral)
2. `_map_customer_journey()` — Full journey from awareness to advocacy
3. `_design_pipeline()` — Sales pipeline stages with `think_with_reflection()`
4. `_create_automations()` — Trigger-based automation workflows
5. `_prevent_churn()` — Early warning system for at-risk customers
6. `_plan_integrations()` — CRM tool recommendations and integration plan

**What makes it special:** Pipeline design uses reflection:
```python
pipeline = await self.think_with_reflection(prompt, task_type="analysis")
```
The reflection engine ensures the pipeline makes logical sense and covers edge cases.

---

### Agent 5: SEO Optimizer

**File:** `core/agents/seo_agent/agent.py`
**UI Page:** `/seo`

**What it does:** Comprehensive SEO strategy with real competitor data and performance metrics.

**The execution flow:**
1. `_keyword_research()` — **Scrapes competitor pages** to find their keywords
2. `_technical_audit()` — Checks site structure, meta tags, schema markup
3. `_optimize_pages()` — Page-by-page optimization recommendations
4. `_build_link_strategy()` — Backlink acquisition plan
5. `_measure_performance()` — **Uses browser automation** to get real Core Web Vitals

**What makes it special:** Two real-world tools:

Competitor scraping for keyword research:
```python
pages = await self.scraper.fetch_multiple(competitor_urls, extract_mode="full")
```

Browser automation for real performance metrics:
```python
browser_metrics = await self.browser.get_performance_metrics(site_url)
```
This gives you actual Lighthouse-style scores (LCP, FID, CLS) — not estimates.

---

### Agent 6: Growth Analytics

**File:** `core/agents/growth_analytics/agent.py`
**UI Page:** `/analytics`

**What it does:** Revenue forecasting, market sizing, and actionable growth playbooks.

**The execution flow:**
1. `_size_market()` — TAM/SAM/SOM analysis
2. `_model_unit_economics()` — ARPU, CAC, LTV, payback period
3. `_forecast_revenue()` — 12-month projections (3 scenarios)
4. `_design_experiments()` — ICE-scored growth experiments
5. `_design_dashboard()` — KPI dashboard blueprint
6. `_validate_forecasts()` — **Runs Python code to verify math**
7. `_create_playbook()` — Week-by-week growth action plan

**What makes it special:** It validates its own math by running Python:
```python
validation = await self.executor.execute(validation_code, language="python")
```
The agent generates revenue projections, then writes Python code to verify the numbers add up correctly. If they don't, it recalculates. This is what makes it trustworthy — it doesn't just guess numbers.

---

### Agent 7: Support Agent

**File:** `core/agents/support_agent/agent.py`
**UI Page:** `/support`

**What it does:** Creates complete customer support infrastructure.

**The execution flow:**
1. `_generate_faq()` — 15-20 industry-relevant FAQs
2. `_design_chatbot()` — Conversation flow with decision trees
3. `_create_templates()` — Response templates for common scenarios
4. `_design_routing()` — Ticket routing rules (urgency, department, skill)
5. `_build_knowledge_base()` — Structured KB with categories and articles
6. `_test_chatbot()` — **Uses browser to test the chatbot URL**

**What makes it special:** Browser testing of the chatbot:
```python
screenshot = await self.browser.take_screenshot(chatbot_url)
metrics = await self.browser.get_performance_metrics(chatbot_url)
```
After designing the chatbot, it actually opens a browser, takes a screenshot, and checks if it loads properly.

---

### Agent 8: Business Automator

**File:** `core/agents/business_automation/agent.py`
**UI Page:** `/automation`

**What it does:** Audits business processes and designs automation workflows.

**The execution flow:**
1. `_audit_processes()` — Identifies inefficiencies and automation opportunities
2. `_design_workflows()` — Creates trigger→action automation flows with `think_with_reflection()`
3. `_create_templates()` — Document templates (invoices, proposals, reports)
4. `_plan_integrations()` — Tool integration architecture
5. `_automate_reporting()` — Scheduled report generation
6. `_calculate_roi()` — Time and cost savings analysis

**What makes it special:** Workflow design uses reflection to ensure logic is sound:
```python
workflows = await self.think_with_reflection(prompt, task_type="analysis")
```

---

## 6. THE 4 AGENT TOOLS — REAL ACTIONS, NOT JUST WORDS

This is what separates NEXUS from chatbot wrappers. Agents don't just generate text — they take real actions.

### Tool 1: Web Scraper

**File:** `core/tools/web_scraper.py`

**What it does:** Fetches web pages and extracts useful content.

**Methods:**
- `fetch_page(url, extract_mode)` — Fetch a single page
- `fetch_multiple(urls, extract_mode)` — Fetch multiple pages in parallel

**Extract modes:**
- `"text"` — Just the text content (for research)
- `"full"` — Complete HTML structure (for competitor analysis)
- `"links"` — All links on the page (for link building)

**Which agents use it:**
- SEO Agent — scrapes competitor pages for keywords
- Content Engine — researches topics before writing
- Marketing Agent — analyzes competitor websites

---

### Tool 2: Code Executor

**File:** `core/tools/code_executor.py`

**What it does:** Runs code in a sandboxed environment and returns the output.

**Method:** `execute(code, language="python")`

**Supported languages:** Python, JavaScript, TypeScript

**Which agents use it:**
- Website Builder — validates generated code for syntax errors
- Growth Analytics — runs Python to verify revenue calculations

**Why it matters:** Without this, agents would generate code that might have bugs. With the executor, code is tested before delivery.

---

### Tool 3: Reflection Engine

**File:** `core/tools/reflection_engine.py`

**What it does:** Takes a piece of AI-generated content, evaluates it against quality criteria, and improves it.

**Method:** `reflect_and_improve(content, criteria)`

**How it works:**
1. Reads the generated content
2. Scores it on: completeness, accuracy, clarity, actionability
3. Identifies weaknesses
4. Rewrites the weak parts
5. Returns improved version

**Which agents use it:**
- Content Engine — improves blog posts and content pieces
- CRM Agent — validates pipeline design logic
- Business Automator — ensures workflow designs are practical

**Why it matters:** First-draft AI output is okay. Reflected output is significantly better. It's like having an editor review every piece of work.

---

### Tool 4: Browser Automation

**File:** `core/tools/browser_automation.py`

**What it does:** Controls a real web browser (via Playwright) to interact with websites.

**Methods:**
- `take_screenshot(url)` — Capture visual screenshot of a page
- `get_performance_metrics(url)` — Get Core Web Vitals (LCP, FID, CLS)
- `click(selector)` — Click elements on a page
- `fill(selector, value)` — Fill form fields
- `navigate(url)` — Go to a URL

**Which agents use it:**
- SEO Agent — measures real Core Web Vitals performance
- Support Agent — tests chatbot pages visually

**Setup:** Requires Playwright:
```bash
pip install playwright
playwright install chromium
```

---

## 7. THE ORCHESTRATOR — THE BRAIN THAT RUNS EVERYTHING

**File:** `core/orchestrator/nexus.py`

The NexusOrchestrator is the central coordinator. Here's exactly what it does:

### What Happens When You Run a Workflow

```python
orchestrator = NexusOrchestrator()
await orchestrator.initialize()  # Starts LLM router, loads agents
result = await orchestrator.run_workflow(client_context)
```

**Step 1: Initialize**
- Creates LLMRouter and calls `router.initialize()` (registers all 4 providers, health checks)
- Creates MemoryManager (persistent context across sessions)
- Creates FeedbackLoop (quality tracking)
- Loads all 8 agents
- Creates AgentGraph (DAG for execution order)

**Step 2: Plan Execution (Agent Graph)**

**File:** `core/orchestrator/agent_graph.py`

The orchestrator builds a DAG (Directed Acyclic Graph) — a dependency tree:

```
Level 1 (run first):       Website Builder
Level 2 (run in parallel): Content Engine + SEO Agent
Level 3 (run in parallel): Marketing + CRM
Level 4 (run in parallel): Support + Automation
Level 5 (run last):        Growth Analytics (needs data from all others)
```

Agents at the same level run **simultaneously** — this is why a full business setup takes 15-30 minutes instead of 2 hours.

**Step 3: Execute with Memory**

**File:** `core/orchestrator/memory_manager.py`

Each agent execution gets context from previous agents:
```python
# Website Builder's output becomes context for Content Engine
context["website_structure"] = website_builder_result
content_result = await content_engine.execute(context)
```

The MemoryManager persists this across sessions — so if a client comes back next month, the system remembers everything about their business.

**Step 4: Score with Feedback Loop**

After every agent execution, the FeedbackLoop scores the output:
```python
score = quality_scorer.score(result)  # 0-100
feedback_loop.record(provider, task_type, score)
```

If a provider consistently scores low for a task type, the router automatically switches to a better one.

### Task Queue

**File:** `core/orchestrator/task_queue.py`

Tasks are prioritized:
```
Priority 1: Critical (website generation for launch deadline)
Priority 2: High (content for marketing campaign)
Priority 3: Normal (monthly analytics report)
Priority 4: Low (knowledge base updates)
```

Higher priority tasks get executed first and get access to premium providers (Claude) if needed.

---

## 8. THE CLIENT LIFECYCLE ENGINE — FROM ZERO TO GROWTH

**File:** `core/lifecycle/client_engine.py`
**UI Page:** `/lifecycle`

This is the automation layer that handles the entire client journey automatically.

### The 5 Phases

```
ONBOARD ──→ SETUP ──→ LAUNCH ──→ GROW ──→ RETAIN
  │           │         │          │         │
  │           │         │          │         └─ Health monitoring, proactive improvements
  │           │         │          └─ Growth analytics, SEO optimization, campaign scaling
  │           │         └─ Go-live audit, campaigns launch, content calendar starts
  │           └─ Build website, content, CRM, SEO, support, automation
  └─ Discovery, competitor research, brand strategy
```

### Phase 1: Onboard
**Agents involved:** Growth Analytics, Marketing, SEO, Content Engine

What happens:
- Client fills intake form (business name, industry, goals, competitors)
- Growth Analytics sizes the market opportunity
- Marketing analyzes competitors (with real scraping)
- Content Engine develops brand voice
- Result: Complete business profile + competitive intelligence

### Phase 2: Setup
**Agents involved:** All 8 agents

What happens:
- Website Builder generates the full website
- Content Engine creates initial content library
- SEO optimizes the site structure
- CRM designs the sales pipeline
- Support creates FAQ and chatbot
- Automation builds workflow automations
- Result: Complete business infrastructure ready to launch

### Phase 3: Launch
**Agents involved:** SEO, Website Builder, Marketing, Content Engine, Growth Analytics

What happens:
- Pre-launch audit checks everything is ready
- Marketing campaigns go live
- Content calendar starts publishing
- Analytics baseline is established
- Result: Business is live and marketing is active

### Phase 4: Grow
**Agents involved:** Growth Analytics, SEO, Marketing, Content Engine, CRM

What happens:
- Growth Analytics identifies new opportunities
- SEO improves search rankings based on real data
- Marketing scales successful campaigns
- Content Engine produces more content
- CRM refines lead scoring based on real conversions
- Result: Measurable growth in traffic, leads, and revenue

### Phase 5: Retain
**Agents involved:** Growth Analytics, SEO, Website Builder, Content Engine, Marketing

What happens:
- Monthly health monitoring (automated)
- Proactive improvement recommendations
- Expansion opportunity identification
- Result: Client stays happy, churns less, grows more

### Auto-Advancement
The lifecycle engine automatically advances phases when deliverables are complete. No manual intervention needed.

---

## 9. THE FEEDBACK LOOP — HOW NEXUS GETS SMARTER

**File:** `core/orchestrator/feedback_loop.py`

This is the self-improving mechanism. Here's exactly how it works:

### Quality Scoring

Every agent output gets scored on 4 dimensions:
- **Completeness** (0-25): Did it deliver everything requested?
- **Format** (0-25): Is it well-structured and professional?
- **Relevance** (0-25): Is it specific to this business/industry?
- **Error-free** (0-25): No hallucinations, no broken code, no logical errors?

Total score: 0-100.

### Quality Thresholds by Task Type

```python
TASK_THRESHOLDS = {
    "website_structure":   70,
    "content_creation":    65,
    "seo_optimization":    70,
    "code_generation":     75,  # Higher bar for code
    "code_debugging":      80,  # Even higher for debugging
    "code_review":         75,
    "analysis":            65,
    "agent_coordination":  70,
}
```

If a provider scores below the threshold for a task type, the system remembers this.

### Auto-Tuning

```python
# After recording many scores:
best_provider = feedback_loop.get_best_provider("code_generation")
# Returns: "opencode" (because it consistently scores 85+ on code tasks)

# This preference is set in the router:
router.set_preference("code_generation", "opencode")
```

Over time, the system learns:
- "OpenCode is best for code generation" (score: 85 avg)
- "Ollama is best for content creation" (score: 78 avg)
- "Claude is best for complex planning" (score: 92 avg)

And it automatically routes accordingly. **The system literally gets smarter with every execution.**

---

## 10. THE PLATFORM UI — YOUR COMMAND CENTER

**Directory:** `platform/` (Next.js 14 + TypeScript + Tailwind CSS)

### Page Overview

| Page | URL | Purpose |
|------|-----|---------|
| Dashboard | `/dashboard` | Command center — all stats, agents, LLM status, quick-launch workflows |
| Agent Fleet | `/agents` | All 8 agents with capabilities, outputs, and status |
| Workflows | `/workflows` | Launch pre-built or custom workflows |
| Website Builder | `/websites` | Configure and generate websites |
| Content Engine | `/content` | Content strategy and creation studio |
| Marketing | `/marketing` | Marketing strategy and campaigns |
| CRM | `/crm` | CRM pipeline design and automation |
| SEO | `/seo` | SEO analysis and optimization |
| Support | `/support` | Customer support setup |
| Automation | `/automation` | Business process automation |
| Growth Analytics | `/analytics` | Revenue forecasting and growth playbooks |
| LLM Router | `/llm-router` | Provider status, routing rules, cost tracking |
| Client Lifecycle | `/lifecycle` | 5-phase client journey management |
| Settings | `/settings` | Provider config, deployment targets, system settings |
| API Docs | `/api-docs` | REST API documentation |

### UI Architecture

```
layout.tsx
├── Sidebar.tsx (left navigation — collapsible)
├── TopBar.tsx (top bar — search, notifications)
└── {page}/page.tsx (main content area)
```

The sidebar has 4 sections:
1. **COMMAND CENTER** — Dashboard, Agents, Workflows, Clients
2. **AGENT STUDIOS** — Individual agent pages (7 agents)
3. **INTELLIGENCE** — Analytics, LLM Router, Lifecycle
4. **SYSTEM** — Settings, API Docs

### Shared Components

- `StatCard` — Metric card with icon, value, trend indicator
- `SectionHeader` — Section title with subtitle and action button
- `ProgressBar` — Visual progress indicator

### Dark Theme

The entire UI uses a dark theme with these design tokens:
- `surface-0` — Darkest background
- `surface-1` — Sidebar/card background
- `surface-2` — Hover states
- `surface-3` — Borders
- `nexus-400/500/600` — Brand accent color (indigo/purple gradient)

---

## 11. THE API LAYER — CONNECTING EVERYTHING

**File:** `api/server.py`

### REST Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| GET | `/health` | System health check |
| POST | `/api/v1/workflows/run` | Launch a workflow |
| GET | `/api/v1/workflows/{id}` | Get workflow status |
| GET | `/api/v1/agents` | List all agents with status |
| POST | `/api/v1/agents/{id}/execute` | Run a specific agent |
| GET | `/api/v1/clients` | List all clients |
| POST | `/api/v1/clients` | Create a new client |
| GET | `/api/v1/analytics/stats` | Get system analytics |
| POST | `/api/v1/lifecycle/advance` | Advance a client's lifecycle phase |
| GET | `/api/v1/lifecycle/{client_id}` | Get client lifecycle status |

### WebSocket

**Endpoint:** `ws://localhost:8000/ws`

Real-time updates during workflow execution:
```json
{"event": "agent_started", "agent": "website_builder", "timestamp": "..."}
{"event": "agent_progress", "agent": "website_builder", "progress": 45}
{"event": "agent_completed", "agent": "website_builder", "score": 87}
{"event": "workflow_completed", "total_cost": 0.00, "duration": "12m 34s"}
```

### CORS

The server allows all origins in development:
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

In production, restrict this to your frontend domain.

---

## 12. CONFIGURATION DEEP DIVE

**File:** `config/settings.py` + `config/example.env`

### Environment Variables — The Complete Reference

#### Core Settings
| Variable | Default | Purpose |
|----------|---------|---------|
| `NEXUS_ENV` | `development` | Environment (development/staging/production) |
| `NEXUS_DEBUG` | `true` | Enable debug mode and hot reload |
| `NEXUS_HOST` | `0.0.0.0` | Server bind address |
| `NEXUS_PORT` | `8000` | Server port |
| `NEXUS_WORKERS` | `4` | Uvicorn worker processes |

#### Ollama (FREE)
| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_ENABLED` | `true` | Enable Ollama provider |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_DEFAULT_MODEL` | `mixtral:8x7b` | Complex task model |
| `OLLAMA_FAST_MODEL` | `llama3.1:8b` | Simple task model |

#### OpenCode (FREE)
| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENCODE_ENABLED` | `true` | Enable OpenCode provider |
| `OPENCODE_PRIMARY_MODEL` | `deepseek-coder-v2:16b` | Code generation model |
| `OPENCODE_COMPLETION_MODEL` | `codellama:13b` | Code completion model |
| `OPENCODE_REVIEW_MODEL` | `qwen2.5-coder:7b` | Code review model |

#### OpenGravity
| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENGRAVITY_ENABLED` | `true` | Enable OpenGravity |
| `OPENGRAVITY_API_KEY` | (empty) | Optional API key |
| `OPENGRAVITY_URL` | `http://localhost:9090` | OpenGravity server |
| `OPENGRAVITY_PREFER_LOCAL` | `true` | Try local before cloud |

#### Claude (PAID)
| Variable | Default | Purpose |
|----------|---------|---------|
| `CLAUDE_API_KEY` | (empty) | Your Anthropic API key |
| `CLAUDE_MODEL` | `claude-sonnet-4-5-20250929` | Which Claude model |
| `CLAUDE_MAX_TOKENS` | `4096` | Max response length |
| `CLAUDE_MONTHLY_BUDGET_USD` | `50.00` | Monthly spending cap |

#### Router Settings
| Variable | Default | Purpose |
|----------|---------|---------|
| `LLM_ROUTER_STRATEGY` | `cost_optimized` | Routing strategy |
| `LLM_FALLBACK_CHAIN` | `ollama,opencode,opengravity,claude` | Fallback order |
| `LLM_CACHE_ENABLED` | `true` | Enable response caching |
| `LLM_CACHE_TTL` | `3600` | Cache lifetime (seconds) |

---

## 13. HOW TO USE NEXUS TO ITS FULLEST POTENTIAL

### Use Case 1: Launch a Complete Business in 30 Minutes

1. Open the Dashboard (`/dashboard`)
2. Click "New Workflow"
3. Select "Full Business Setup" template
4. Fill in:
   - Client ID: `client_001`
   - Business Name: `CloudPeak Analytics`
   - Industry: `SaaS`
   - Description: `B2B analytics platform for e-commerce companies. We help online stores understand their customer behavior, optimize pricing, and predict demand.`
   - Goals: `Launch website, generate 100 leads/month, establish thought leadership in e-commerce analytics`
5. Click "Launch Workflow"
6. Watch 8 agents work in parallel
7. In ~20 minutes you get: website, content library, marketing strategy, CRM pipeline, SEO plan, analytics playbook, support system, automation workflows

### Use Case 2: Scale Content for an Existing Client

1. Go to Content Engine (`/content`)
2. Enter the client's business details
3. Run "Content Blitz" workflow
4. Get: 30-day content calendar, 5 blog posts, email sequences, social media posts, ad copy
5. All researched from real competitor data

### Use Case 3: Fix a Client's SEO

1. Go to SEO Optimizer (`/seo`)
2. Enter the client's URL and competitor URLs
3. The agent will:
   - Scrape competitor sites for keywords
   - Run browser automation for Core Web Vitals
   - Generate technical audit checklist
   - Create page-by-page optimization plan
   - Design link building strategy

### Use Case 4: Monthly Growth Reports

1. Go to Growth Analytics (`/analytics`)
2. Enter current MRR, customer count, business model
3. Get: Market sizing, unit economics, 12-month forecast (validated with real Python calculations), 5 growth experiments, action playbook

### Use Case 5: Automate Client Lifecycle

1. Go to Client Lifecycle (`/lifecycle`)
2. Select a template (e.g., "Complete Company Setup")
3. The system will automatically:
   - Onboard the client (discovery + competitive research)
   - Set up all systems (website + content + CRM + everything)
   - Launch (campaigns + content calendar)
   - Grow (optimize based on real performance data)
   - Retain (proactive monitoring + improvements)
4. Each phase advances automatically when deliverables are complete

---

## 14. PRO TIPS AND SECRET WEAPONS

### Tip 1: Use the Right Strategy for the Right Client

In Settings, change `LLM_ROUTER_STRATEGY`:
- **`cost_optimized`** (default) — Best for high-volume work. Maximizes local model usage.
- **`quality_first`** — Use for premium clients. Will use Claude more often.
- **`balanced`** — Middle ground.

### Tip 2: Pre-warm Your Cache

Run workflows for common industries first (SaaS, E-commerce, Consulting). The cache will store common responses, making subsequent workflows faster and free.

### Tip 3: Use force_provider for Critical Tasks

When you absolutely need the best output:
```python
response = await router.generate(prompt, force_provider=LLMProvider.CLAUDE)
```
This bypasses the cost optimization and goes straight to Claude.

### Tip 4: Monitor Your Feedback Loop

Check `/llm-router` regularly. The feedback data tells you:
- Which providers are performing best for which tasks
- Where quality is dropping (indicates model needs changing)
- How much you're spending and on what

### Tip 5: Start with Smaller Models, Scale Up

If you're on a machine with limited RAM:
```env
OLLAMA_DEFAULT_MODEL=llama3.1:8b       # Instead of mixtral
OPENCODE_PRIMARY_MODEL=qwen2.5-coder:7b # Instead of deepseek-coder-v2:16b
```
These are smaller but still capable. Upgrade to bigger models as needed.

### Tip 6: Use the Lifecycle Engine for Recurring Revenue

The lifecycle engine is designed to create ongoing client relationships:
- Phase 1-3: One-time setup (charge a setup fee)
- Phase 4-5: Ongoing optimization (charge monthly retainer)
- The system does the work automatically — you collect the revenue

### Tip 7: Parallel Agent Execution

The DAG-based orchestrator runs agents in parallel when possible. To maximize this:
- Provide complete business descriptions upfront (don't drip-feed information)
- Let the orchestrator plan the execution graph
- Don't interrupt mid-workflow unless necessary

### Tip 8: Leverage Real Data from Tools

The most powerful feature is tools. When filing client information:
- Provide real competitor URLs → Scraper gets real data
- Provide real website URLs → Browser gets real metrics
- Let the executor validate code → No broken deliverables

### Tip 9: Customize Agent Prompts

Each agent has a system prompt that defines its personality and expertise. To customize:
1. Read the agent file (e.g., `core/agents/content_engine/agent.py`)
2. Find the `_system_prompt` or system message
3. Adjust tone, expertise level, or output format

### Tip 10: The $0 Stack

If you want to spend literally nothing:
1. Disable Claude (`CLAUDE_API_KEY=` — leave empty)
2. Disable OpenGravity cloud (`OPENGRAVITY_PREFER_LOCAL=true`)
3. Use only Ollama + OpenCode (both 100% free)
4. You lose some quality on complex reasoning tasks, but everything still works

---

## 15. TROUBLESHOOTING GUIDE

### "Ollama connection refused"
```bash
# Make sure Ollama is running:
ollama serve

# Check if it's up:
curl http://localhost:11434/api/tags
```

### "Model not found"
```bash
# List installed models:
ollama list

# Pull missing model:
ollama pull mixtral:8x7b
```

### "Claude budget exceeded"
The router skips Claude when the monthly budget is hit. This is by design. Options:
- Increase `CLAUDE_MONTHLY_BUDGET_USD` in .env
- Wait until next month (budget resets)
- Local models will handle everything (just slightly lower quality)

### "npm: command not found"
```bash
# macOS:
brew install node

# If no Homebrew:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install node
```

### "pip: command not found"
```bash
# Use pip3 on macOS:
pip3 install -r requirements.txt
```

### "networkx version error / Python 3.9 too old"
Some packages need Python 3.10+. Options:
```bash
# Install Python 3.12:
brew install python@3.12
python3.12 -m pip install -r requirements.txt

# Or just install core packages:
pip3 install fastapi uvicorn pydantic pydantic-settings python-dotenv httpx structlog anthropic
```

### "Frontend won't build"
```bash
cd platform
rm -rf node_modules .next
npm install
npm run dev
```

### "Agent returns low quality output"
1. Check which provider handled it (`response.provider`)
2. If it was Ollama for a complex task, try `force_provider=LLMProvider.CLAUDE`
3. Check the feedback loop scores to see if the provider is consistently low
4. Consider upgrading the Ollama model to a larger variant

---

## ARCHITECTURE CHEAT SHEET

```
/home/user/TRADING-INFRASTRUCTURE/
│
├── api/                          # FastAPI server
│   ├── server.py                 # Main app + CORS + routes
│   ├── routes/                   # REST endpoints
│   │   ├── health.py             # GET /health
│   │   ├── workflows.py          # CRUD workflows
│   │   ├── agents.py             # Agent management
│   │   ├── clients.py            # Client CRUD
│   │   ├── analytics.py          # Stats + metrics
│   │   └── lifecycle.py          # Lifecycle management
│   └── websockets/
│       └── events.py             # Real-time WS events
│
├── config/
│   ├── settings.py               # Pydantic settings (ALL env vars)
│   └── example.env               # Template env file
│
├── core/
│   ├── agents/
│   │   ├── base_agent.py         # BaseAgent (tools, think, reflect)
│   │   ├── website_builder/      # Website generation + code validation
│   │   ├── content_engine/       # Content + research scraping
│   │   ├── marketing_agent/      # Strategy + competitor scraping
│   │   ├── crm_agent/            # CRM + reflection-based design
│   │   ├── seo_agent/            # SEO + scraping + browser metrics
│   │   ├── growth_analytics/     # Forecasting + Python validation
│   │   ├── support_agent/        # Support + browser testing
│   │   └── business_automation/  # Workflows + reflection design
│   │
│   ├── llm_router/
│   │   ├── models.py             # 4 providers + costs + capabilities
│   │   └── router.py             # Smart routing engine
│   │
│   ├── orchestrator/
│   │   ├── nexus.py              # Central orchestrator
│   │   ├── agent_graph.py        # DAG execution planner
│   │   ├── task_queue.py         # Priority task queue
│   │   ├── memory_manager.py     # Persistent agent memory
│   │   └── feedback_loop.py      # Quality scoring + auto-tuning
│   │
│   ├── lifecycle/
│   │   └── client_engine.py      # 5-phase lifecycle automation
│   │
│   └── tools/
│       ├── web_scraper.py        # HTTP content extraction
│       ├── code_executor.py      # Sandboxed code execution
│       ├── reflection_engine.py  # Output quality improvement
│       └── browser_automation.py # Playwright browser control
│
├── integrations/
│   ├── opencode/
│   │   └── client.py             # 6 coding methods via Ollama
│   └── opengravity/
│       └── client.py             # Hybrid local/cloud coordination
│
├── platform/                     # Next.js 14 frontend
│   ├── app/
│   │   ├── layout.tsx            # Root layout (Sidebar + TopBar)
│   │   ├── dashboard/page.tsx    # Command center
│   │   ├── agents/page.tsx       # Agent fleet overview
│   │   ├── workflows/page.tsx    # Workflow builder
│   │   ├── websites/page.tsx     # Website generation studio
│   │   ├── content/page.tsx      # Content engine studio
│   │   ├── marketing/page.tsx    # Marketing strategy
│   │   ├── crm/page.tsx          # CRM automation
│   │   ├── seo/page.tsx          # SEO optimization
│   │   ├── support/page.tsx      # Support setup
│   │   ├── automation/page.tsx   # Business automation
│   │   ├── analytics/page.tsx    # Growth analytics
│   │   ├── llm-router/page.tsx   # LLM provider status
│   │   ├── lifecycle/page.tsx    # Client lifecycle
│   │   └── settings/page.tsx     # Configuration
│   └── components/
│       ├── layout/Sidebar.tsx    # Collapsible navigation
│       └── ui/                   # StatCard, SectionHeader, etc.
│
├── requirements.txt              # Python dependencies
└── docker-compose.yml            # Container setup
```

---

## FINAL WORDS

NEXUS AI is designed around one principle: **local first, premium never (unless absolutely necessary).**

The system is built so that 90%+ of work happens on your own machine at zero cost. Claude is the safety net, not the workhorse. The feedback loop ensures the system gets better over time without any manual tuning.

The real power isn't in any single agent — it's in how they work together. The orchestrator builds a dependency graph, runs agents in parallel, shares context between them, and scores every output. Each client workflow makes the next one better.

Start with one workflow. Watch the agents work. Check the LLM Router to see where requests went. Look at the feedback scores. Then scale up.

**Your AI workforce is ready. Put it to work.**
