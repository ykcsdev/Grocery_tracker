import json
from typing import List, Optional
from google.genai import types
from .interfaces import LLMProvider, EmbeddingProvider
from ..gemini_client import EMBEDDING_MODEL_NAME, get_client


class GeminiProvider(LLMProvider, EmbeddingProvider):
    def __init__(self, model_name="gemini-3-flash", embedding_model_name=EMBEDDING_MODEL_NAME):
        self.client = get_client()
        self.model_name = model_name
        self.embedding_model = embedding_model_name

    def generate_response(self, system_prompt: str, user_prompt: str, context: Optional[str] = None) -> str:
        # Using the dedicated system_instruction parameter is more effective
        user_content = ""
        if context:
            user_content += f"Context Data:\n<DATA>\n{context}\n</DATA>\n\n"
        
        user_content += f"User Query: {user_prompt}"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        return response.text

    def classify_intent(self, user_query: str) -> dict:
        """Determines if the query needs SQL, Vector search, or both."""
        
        # Define the schema for a guaranteed JSON response
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "needs_sql": {"type": "BOOLEAN"},
                "needs_vector": {"type": "BOOLEAN"}
            },
            "required": ["needs_sql", "needs_vector"]
        }

        prompt = f"Analyze if this query needs exact math/aggregation (SQL) or semantic search (Vector): '{user_query}'"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a query router. Categorize user queries for a grocery tracker.",
                response_mime_type="application/json",
                response_schema=response_schema
            ),
        )
        
        # With response_schema, response.parsed contains a typed object or dict
        try:
            return response.parsed
        except Exception:
            return {"needs_sql": True, "needs_vector": True}

    def generate_sql(self, schema_context: str, user_query: str) -> str:
        """Generates a read-only PostgreSQL query."""
        system_msg = (
            "You are a PostgreSQL expert. Write ONLY the raw SQL SELECT statement. "
            "No markdown formatting, no explanations. Strictly read-only."
        )
        
        prompt = f"Schema:\n{schema_context}\n\nUser Query: {user_query}"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_msg)
        )
        
        # Strip potential markdown if the model still includes it
        return response.text.strip().strip("`").replace("sql\n", "")

    def embed_text(self, text: str) -> List[float]:
        result = self.client.models.embed_content(
            model=self.embedding_model,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        return result.embeddings[0].values

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        result = self.client.models.embed_content(
            model=self.embedding_model,
            contents=texts,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        return [embedding.values for embedding in result.embeddings]