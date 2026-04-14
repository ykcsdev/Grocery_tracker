from abc import ABC, abstractmethod
from typing import List, Optional

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
    def generate_sql(self, schema_context: str, user_query: str) -> str:
        """Generates a SELECT sql query based on schema and user query."""
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
