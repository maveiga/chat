import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "vehicles.db")

MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY não configurada!\n"
        "Adicione no arquivo .env ou como variável de ambiente."
    )
