import os
import chromadb
import re
from typing import List, Dict, Any
from .interfaces import EmbeddingProvider

class VectorDB:
    def __init__(self, embedding_provider: EmbeddingProvider):
        self.host = os.environ.get("CHROMA_HOST", "localhost")
        self.port = os.environ.get("CHROMA_PORT", "8000")
        self.embedding_provider = embedding_provider
        
        # Connect to ChromaDB
        self.client = chromadb.HttpClient(host=self.host, port=self.port)
        self.collection = self.client.get_or_create_collection(name="receipts_collection")

    def sanitize_text(self, text: str) -> str:
        """Removes repeated noise or personal identifiers if necessary."""
        clean = re.sub(r'\s+', ' ', text)
        return clean.strip()

    def add_texts(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]] = None):
        """Chunks and sanitizes texts before embedding and storing."""
        sanitized_texts = [self.sanitize_text(t) for t in texts]
        embeddings = self.embedding_provider.embed_batch(sanitized_texts)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=sanitized_texts,
            metadatas=metadatas
        )

    def search(self, query: str, n_results: int = 5) -> str:
        """Searches the vector db and returns a concatenated context string."""
        sanitized_query = self.sanitize_text(query)
        query_embedding = self.embedding_provider.embed_text(sanitized_query)
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            documents = results.get('documents', [[]])[0]
            if not documents:
                return "No semantic results found."
            return "\n".join(documents)
        except Exception:
            return "No semantic results found."
