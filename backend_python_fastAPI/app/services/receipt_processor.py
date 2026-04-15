import mimetypes
import json
from google.genai import types
from .gemini_client import MODEL_NAME, build_binary_part, get_client
from .prompts import RECEIPT_PROMPT

def process_receipt_file(file_path: str) -> dict:
    client = get_client()

    # 1. Determine Mime Type
    mime_type, _ = mimetypes.guess_type(file_path)
    supported_types = ["application/pdf", "image/jpeg", "image/png", "image/webp"]
    
    if not mime_type or mime_type not in supported_types:
        raise ValueError(f"Unsupported or unknown file type: {mime_type}")

    # 2. Read file
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # 3. Generate Content
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            build_binary_part(data=file_bytes, mime_type=mime_type),
            RECEIPT_PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            candidate_count=1 
        ),
    )

    # 4. Handle the Response
    if response.parsed:
        return response.parsed
    
    try:
        clean_text = response.text.strip().strip("```json").strip("```")
        return json.loads(clean_text)
    except (json.JSONDecodeError, AttributeError):
        raise ValueError("Gemini failed to return a valid JSON structure.")