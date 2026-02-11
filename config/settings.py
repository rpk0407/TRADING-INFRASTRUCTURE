"""
NEXUS AI — Global Configuration
Loads from environment variables with smart defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LLMRouterStrategy(str, Enum):
    COST_OPTIMIZED = "cost_optimized"      # Cheapest model that can handle the task
    QUALITY_FIRST = "quality_first"        # Best model, fall back to cheaper
    ROUND_ROBIN = "round_robin"            # Distribute load evenly
    LATENCY_OPTIMIZED = "latency_optimized"  # Fastest response time


class Settings(BaseSettings):
    # ─── Core ───
    env: Environment = Field(default=Environment.DEVELOPMENT, alias="NEXUS_ENV")
    debug: bool = Field(default=True, alias="NEXUS_DEBUG")
    secret_key: str = Field(default="dev-secret-change-me", alias="NEXUS_SECRET_KEY")
    host: str = Field(default="0.0.0.0", alias="NEXUS_HOST")
    port: int = Field(default=8000, alias="NEXUS_PORT")
    workers: int = Field(default=4, alias="NEXUS_WORKERS")

    # ─── Database ───
    database_url: str = Field(
        default="sqlite+aiosqlite:///./nexus.db",
        alias="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # ─── Kimi K2.5 (Local) ───
    kimi_local_enabled: bool = Field(default=True, alias="KIMI_LOCAL_ENABLED")
    kimi_local_url: str = Field(
        default="http://localhost:8080/v1",
        alias="KIMI_LOCAL_URL"
    )
    kimi_model_name: str = Field(default="kimi-k2.5", alias="KIMI_MODEL_NAME")
    kimi_max_tokens: int = Field(default=8192, alias="KIMI_MAX_TOKENS")

    # ─── Ollama (Local) ───
    ollama_enabled: bool = Field(default=True, alias="OLLAMA_ENABLED")
    ollama_url: str = Field(default="http://localhost:11434", alias="OLLAMA_URL")
    ollama_default_model: str = Field(
        default="mixtral:8x7b", alias="OLLAMA_DEFAULT_MODEL"
    )
    ollama_coding_model: str = Field(
        default="deepseek-coder-v2:16b", alias="OLLAMA_CODING_MODEL"
    )
    ollama_fast_model: str = Field(default="llama3.1:8b", alias="OLLAMA_FAST_MODEL")

    # ─── AntiGravity ───
    antigravity_enabled: bool = Field(default=True, alias="ANTIGRAVITY_ENABLED")
    antigravity_api_key: Optional[str] = Field(default=None, alias="ANTIGRAVITY_API_KEY")
    antigravity_url: str = Field(
        default="http://localhost:9090", alias="ANTIGRAVITY_URL"
    )

    # ─── Gemini (FREE API) ───
    gemini_enabled: bool = Field(default=True, alias="GEMINI_ENABLED")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")
    gemini_max_tokens: int = Field(default=8192, alias="GEMINI_MAX_TOKENS")

    # ─── DeepSeek R1 (Local) ───
    deepseek_enabled: bool = Field(default=True, alias="DEEPSEEK_ENABLED")
    deepseek_model: str = Field(default="deepseek-r1:32b", alias="DEEPSEEK_MODEL")

    # ─── Groq (FREE tier) ───
    groq_enabled: bool = Field(default=True, alias="GROQ_ENABLED")
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")

    # ─── Claude API ───
    claude_api_key: Optional[str] = Field(default=None, alias="CLAUDE_API_KEY")
    claude_model: str = Field(
        default="claude-sonnet-4-5-20250929", alias="CLAUDE_MODEL"
    )
    claude_max_tokens: int = Field(default=4096, alias="CLAUDE_MAX_TOKENS")
    claude_monthly_budget_usd: float = Field(
        default=50.0, alias="CLAUDE_MONTHLY_BUDGET_USD"
    )

    # ─── LLM Router ───
    llm_router_strategy: LLMRouterStrategy = Field(
        default=LLMRouterStrategy.COST_OPTIMIZED,
        alias="LLM_ROUTER_STRATEGY"
    )
    llm_cost_threshold: float = Field(default=0.01, alias="LLM_COST_THRESHOLD")
    llm_fallback_chain: str = Field(
        default="kimi_local,ollama,deepseek,gemini,groq,antigravity,claude",
        alias="LLM_FALLBACK_CHAIN"
    )
    llm_cache_enabled: bool = Field(default=True, alias="LLM_CACHE_ENABLED")
    llm_cache_ttl: int = Field(default=3600, alias="LLM_CACHE_TTL")

    # ─── Agents ───
    agent_max_concurrent: int = Field(default=10, alias="AGENT_MAX_CONCURRENT")
    agent_timeout_seconds: int = Field(default=300, alias="AGENT_TIMEOUT_SECONDS")
    agent_retry_max: int = Field(default=3, alias="AGENT_RETRY_MAX")
    agent_memory_backend: str = Field(default="redis", alias="AGENT_MEMORY_BACKEND")

    # ─── Website Builder ───
    website_output_dir: str = Field(
        default="./output/websites", alias="WEBSITE_OUTPUT_DIR"
    )
    website_deploy_provider: str = Field(
        default="vercel", alias="WEBSITE_DEPLOY_PROVIDER"
    )
    vercel_token: Optional[str] = Field(default=None, alias="VERCEL_TOKEN")
    netlify_token: Optional[str] = Field(default=None, alias="NETLIFY_TOKEN")

    # ─── Storage ───
    storage_backend: str = Field(default="local", alias="STORAGE_BACKEND")
    storage_local_path: str = Field(default="./storage", alias="STORAGE_LOCAL_PATH")

    # ─── Monitoring ───
    prometheus_enabled: bool = Field(default=True, alias="PROMETHEUS_ENABLED")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def fallback_chain(self) -> list[str]:
        return [p.strip() for p in self.llm_fallback_chain.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
