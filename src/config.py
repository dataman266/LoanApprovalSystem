import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/loan_system.db")
    database_echo: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"

    # API Server
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_workers: int = int(os.getenv("API_WORKERS", "1"))

    # MCP Servers
    mcp_applicant_db_port: int = int(os.getenv("MCP_APPLICANT_DB_PORT", "8001"))
    mcp_risk_rules_port: int = int(os.getenv("MCP_RISK_RULES_PORT", "8002"))
    mcp_decision_synthesis_port: int = int(os.getenv("MCP_DECISION_SYNTHESIS_PORT", "8003"))
    mcp_notification_port: int = int(os.getenv("MCP_NOTIFICATION_PORT", "8004"))

    # Streamlit UI
    streamlit_port: int = int(os.getenv("STREAMLIT_PORT", "8501"))

    # Decision Engine
    decision_timeout_seconds: int = int(os.getenv("DECISION_TIMEOUT_SECONDS", "30"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "2"))

    # Anthropic
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
