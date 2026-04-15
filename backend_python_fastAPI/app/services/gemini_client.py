import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Initialize environment variables once at the module level
load_dotenv()

MODEL_NAME = "gemini-2.5-flash" 
EMBEDDING_MODEL_NAME = "gemini-embedding-001" 


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