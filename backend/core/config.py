import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # AWS Bedrock
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    # Pinecone
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "sostenibilidad-docs")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")

    # Document processing - search in multiple directories
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DOCS_PATHS: list = [
        os.path.join(PROJECT_ROOT, "documentos"),
        os.path.join(PROJECT_ROOT, "docs"),
        PROJECT_ROOT  # Search entire project
    ]
    # Backward compatibility
    DOCS_PATH: str = os.path.join(PROJECT_ROOT, "documentos")
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # API
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()