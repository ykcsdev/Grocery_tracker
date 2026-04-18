from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, context: Optional[str] = None) -> str:
        """Generates a text response from the LLM."""
        pass

    @abstractmethod
    def classify_intent(self, user_query: str) -> dict:
        """
        Classifies the query intent.
        Returns a dictionary: {"needs_sql": bool, "needs_vector": bool}
        """
        pass

    @abstractmethod
    def plan_query(self, schema_context: str, user_query: str) -> Dict[str, object]:
        """Builds a lightweight execution plan for the query."""
        pass

    @abstractmethod
    def generate_sql(self, schema_context: str, user_query: str) -> str:
        """Generates a SELECT sql query based on schema and user query."""
        pass

    @abstractmethod
    def summarize_sql_result(self, user_query: str, sql_query: str, sql_result: str) -> Dict[str, object]:
        """Summarizes SQL output into reusable insight memory."""
        pass


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Converts a string into a list of floats for vector search."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Converts a batch of strings into embeddings."""
        pass
