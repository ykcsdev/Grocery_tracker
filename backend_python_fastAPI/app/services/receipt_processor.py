import mimetypes
import json
from google.generativeai import GenerativeModel
from .gemini_client import MODEL_NAME
from .prompts import RECEIPT_PROMPT
import re

def extract_json(text: str) -> dict:
    """
    Extracts the first valid JSON object from LLM output.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in Gemini response")

    json_str = match.group(0)
    return json.loads(json_str)


def process_receipt_file(file_path: str) -> dict:
    model = GenerativeModel(MODEL_NAME)

    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type not in ["application/pdf", "image/jpeg", "image/png"]:
        raise ValueError(f"Unsupported file type: {mime_type}")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    response = model.generate_content(
        contents=[
            RECEIPT_PROMPT,
            {
                "mime_type": mime_type,
                "data": file_bytes
            }
        ],
        generation_config={
            "response_mime_type": "application/json"
        }
    )
    print("RAW GEMINI RESPONSE:\n", response.text)

    return extract_json(response.text)
