import os
from dotenv import load_dotenv

agent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(agent_dir, ".env"))
load_dotenv()

# Automatically configure LangSmith Tracing V2 environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "Tracing Project")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")


class AgentConfig:
    LANGCHAIN_TRACING_V2: str = os.environ["LANGCHAIN_TRACING_V2"]
    LANGCHAIN_API_KEY: str = os.environ["LANGCHAIN_API_KEY"]
    LANGCHAIN_PROJECT: str = os.environ["LANGCHAIN_PROJECT"]
    LANGCHAIN_ENDPOINT: str = os.environ["LANGCHAIN_ENDPOINT"]

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "traceback_vectors")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/traceback_db")
    
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
    EXTRACTION_LLM_MODEL: str = os.getenv("EXTRACTION_LLM_MODEL", os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini"))
    REASONING_LLM_MODEL: str = os.getenv("REASONING_LLM_MODEL", os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini"))
    FALLBACK_LLM_MODEL: str = os.getenv("FALLBACK_LLM_MODEL", "gpt-4o-mini")
    VISION_LLM_MODEL: str = os.getenv("VISION_LLM_MODEL", os.getenv("EXTRACTION_LLM_MODEL", "gpt-4o-mini"))
    
    MAX_TOOL_ITERATIONS: int = int(os.getenv("MAX_TOOL_ITERATIONS", "5"))
    MAX_INVESTIGATION_ITERATIONS: int = int(os.getenv("MAX_INVESTIGATION_ITERATIONS", "3"))
    MAX_KNOWLEDGE_TOP_K: int = int(os.getenv("MAX_KNOWLEDGE_RETRIEVAL_TOP_K", "8"))
    MAX_PREVIOUS_INCIDENTS_TOP_K: int = int(os.getenv("MAX_PREVIOUS_INCIDENTS_TOP_K", "2"))
    MAX_DESCRIPTION_WORDS: int = 2000
    MAX_EVIDENCE_ATTACHMENTS: int = 10

config = AgentConfig()
