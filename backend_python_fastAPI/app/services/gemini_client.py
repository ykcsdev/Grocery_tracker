import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
ROUTING_MODEL_NAME = os.getenv("GEMINI_ROUTING_MODEL", "gemini-2.5-flash")
PLANNING_MODEL_NAME = os.getenv("GEMINI_PLANNING_MODEL", "gemini-2.5-flash-lite")
SQL_MODEL_NAME = os.getenv("GEMINI_SQL_MODEL", "gemini-2.5-flash")
RESPONSE_MODEL_NAME = os.getenv("GEMINI_RESPONSE_MODEL", "gemini-2.5-flash-lite")
RECEIPT_MODEL_NAME = os.getenv("GEMINI_RECEIPT_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL_NAME = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
EMBEDDING_DIMENSIONALITY = int(os.getenv("GEMINI_EMBEDDING_DIMENSIONALITY", "768"))


def get_client() -> genai.Client:
    """Initializes and returns the Gemini API client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not found. Please check your .env file.")

    return genai.Client(api_key=api_key)


def build_binary_part(data: bytes, mime_type: str) -> types.Part:
    """
    Wraps raw bytes into a Part object for multi-modal requests.
    Example mime_types: 'image/jpeg', 'application/pdf', 'video/mp4'
    """
    return types.Part.from_bytes(data=data, mime_type=mime_type)
