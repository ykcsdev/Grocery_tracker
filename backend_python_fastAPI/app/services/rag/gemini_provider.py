from typing import Dict, List, Optional
from google.genai import types
from .interfaces import LLMProvider, EmbeddingProvider
from ..gemini_client import (
    EMBEDDING_DIMENSIONALITY,
    EMBEDDING_MODEL_NAME,
    PLANNING_MODEL_NAME,
    RESPONSE_MODEL_NAME,
    ROUTING_MODEL_NAME,
    SQL_MODEL_NAME,
    get_client,
)


class GeminiProvider(LLMProvider, EmbeddingProvider):
    def __init__(
        self,
        routing_model_name: str = ROUTING_MODEL_NAME,
        planning_model_name: str = PLANNING_MODEL_NAME,
        sql_model_name: str = SQL_MODEL_NAME,
        response_model_name: str = RESPONSE_MODEL_NAME,
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
        embedding_output_dimensionality: int = EMBEDDING_DIMENSIONALITY,
    ):
        self.client = get_client()
        self.routing_model_name = routing_model_name
        self.planning_model_name = planning_model_name
        self.sql_model_name = sql_model_name
        self.response_model_name = response_model_name
        self.embedding_model = embedding_model_name
        self.embedding_output_dimensionality = embedding_output_dimensionality

    def _extract_parsed(self, response, fallback: Dict[str, object]) -> Dict[str, object]:
        try:
            parsed = response.parsed
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
        return fallback

    def generate_response(self, system_prompt: str, user_prompt: str, context: Optional[str] = None) -> str:
        user_content = ""
        if context:
            user_content += f"Context Data:\n<DATA>\n{context}\n</DATA>\n\n"

        user_content += f"User Query: {user_prompt}"

        response = self.client.models.generate_content(
            model=self.response_model_name,
            contents=user_content,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
        return response.text

    def classify_intent(self, user_query: str) -> dict:
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "needs_sql": {"type": "BOOLEAN"},
                "needs_vector": {"type": "BOOLEAN"},
            },
            "required": ["needs_sql", "needs_vector"],
        }

        prompt = f"Analyze if this query needs exact math/aggregation (SQL) or semantic search (Vector): '{user_query}'"

        response = self.client.models.generate_content(
            model=self.routing_model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a query router. Categorize user queries for a grocery tracker.",
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
        return self._extract_parsed(response, {"needs_sql": True, "needs_vector": True})

    def plan_query(self, schema_context: str, user_query: str) -> Dict[str, object]:
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "needs_sql": {"type": "BOOLEAN"},
                "needs_vector": {"type": "BOOLEAN"},
                "should_store_memory": {"type": "BOOLEAN"},
                "requires_financial_validation": {"type": "BOOLEAN"},
                "sql_strategy": {"type": "STRING"},
                "analysis_steps": {"type": "ARRAY", "items": {"type": "STRING"}},
                "vector_k": {"type": "INTEGER"},
            },
            "required": [
                "needs_sql",
                "needs_vector",
                "should_store_memory",
                "requires_financial_validation",
                "sql_strategy",
                "analysis_steps",
                "vector_k",
            ],
        }

        response = self.client.models.generate_content(
            model=self.planning_model_name,
            contents=f"Schema:\n{schema_context}\n\nUser Query:\n{user_query}",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are the planning brain for a financial chatbot over grocery receipts. "
                    "Decide whether the request needs structured SQL, semantic memory lookup, or both. "
                    "Prefer SQL for exact totals, VAT/tax, trends, and rankings. "
                    "Prefer vector search for prior insights or semantic merchant/category recall."
                ),
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
        return self._extract_parsed(
            response,
            {
                "needs_sql": True,
                "needs_vector": True,
                "should_store_memory": True,
                "requires_financial_validation": True,
                "sql_strategy": "Aggregate receipts and taxes using the available analytics views.",
                "analysis_steps": ["Generate SQL", "Validate financial math", "Retrieve vector memory", "Compose answer"],
                "vector_k": 5,
            },
        )

    def generate_sql(self, schema_context: str, user_query: str) -> str:
        response = self.client.models.generate_content(
            model=self.sql_model_name,
            contents=f"Schema:\n{schema_context}\n\nUser Query: {user_query}",
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a PostgreSQL expert. Write ONLY the raw SQL SELECT statement. "
                    "No markdown formatting, no explanations. Strictly read-only. "
                    "Prefer the financial summary views when they answer the question. "
                    "Add ORDER BY when ranking. Add LIMIT for non-aggregate listing queries."
                )
            ),
        )
        return response.text.strip().strip("`").replace("sql\n", "")

    def summarize_sql_result(self, user_query: str, sql_query: str, sql_result: str) -> Dict[str, object]:
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "summary": {"type": "STRING"},
                "insights": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["summary", "insights"],
        }

        response = self.client.models.generate_content(
            model=self.response_model_name,
            contents=(
                f"User Query:\n{user_query}\n\n"
                f"SQL Query:\n{sql_query}\n\n"
                f"SQL Result:\n{sql_result}"
            ),
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You turn SQL output into compact financial memory. "
                    "Produce a short summary plus up to 5 reusable insight sentences for later semantic retrieval. "
                    "Be faithful to the data and avoid speculation."
                ),
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )
        return self._extract_parsed(
            response,
            {"summary": "SQL results were generated for the financial query.", "insights": []},
        )

    def _format_document_for_embedding(self, text: str) -> str:
        if "embedding-2" in self.embedding_model:
            return f"title: financial insight | text: {text}"
        return text

    def _format_query_for_embedding(self, text: str) -> str:
        if "embedding-2" in self.embedding_model:
            return f"task: search result | query: {text}"
        return text

    def embed_text(self, text: str) -> List[float]:
        config_kwargs = {"output_dimensionality": self.embedding_output_dimensionality}
        if "embedding-2" not in self.embedding_model:
            config_kwargs["task_type"] = "RETRIEVAL_QUERY"

        result = self.client.models.embed_content(
            model=self.embedding_model,
            contents=self._format_query_for_embedding(text),
            config=types.EmbedContentConfig(**config_kwargs),
        )
        return result.embeddings[0].values

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        config_kwargs = {"output_dimensionality": self.embedding_output_dimensionality}
        if "embedding-2" not in self.embedding_model:
            config_kwargs["task_type"] = "RETRIEVAL_DOCUMENT"

        result = self.client.models.embed_content(
            model=self.embedding_model,
            contents=[self._format_document_for_embedding(text) for text in texts],
            config=types.EmbedContentConfig(**config_kwargs),
        )
        return [embedding.values for embedding in result.embeddings]
