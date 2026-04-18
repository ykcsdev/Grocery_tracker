import os
import re
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

import chromadb

from .interfaces import EmbeddingProvider


class VectorDB:
    def __init__(self, embedding_provider: EmbeddingProvider):
        self.embedding_provider = embedding_provider
        self.collection_name = os.environ.get("CHROMA_COLLECTION", "financial_insights")
        self.client = self._build_client()
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def _build_client(self):
        mode = os.environ.get("CHROMA_MODE", "persistent").lower()
        if mode == "http":
            host = os.environ.get("CHROMA_HOST", "localhost")
            port = int(os.environ.get("CHROMA_PORT", "8000"))
            return chromadb.HttpClient(host=host, port=port)

        persist_dir = Path(os.environ.get("CHROMA_PERSIST_DIR", "backend_python_fastAPI/chroma_data"))
        persist_dir.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(persist_dir))

    def sanitize_text(self, text: str) -> str:
        clean = re.sub(r"\s+", " ", text or "")
        return clean.strip()

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        sanitized: Dict[str, Any] = {}
        for key, value in (metadata or {}).items():
            if value is None:
                continue
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = str(value)
        return sanitized

    def add_texts(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]] = None):
        if not ids or not texts:
            return

        sanitized_texts = [self.sanitize_text(text) for text in texts if self.sanitize_text(text)]
        if not sanitized_texts:
            return

        sanitized_metadatas = [self._sanitize_metadata(metadata) for metadata in (metadatas or [{} for _ in sanitized_texts])]
        embeddings = self.embedding_provider.embed_batch(sanitized_texts)

        self.collection.add(
            ids=ids[: len(sanitized_texts)],
            embeddings=embeddings,
            documents=sanitized_texts,
            metadatas=sanitized_metadatas[: len(sanitized_texts)],
        )

    def store_financial_insights(self, insights: List[str], metadata: Dict[str, Any]) -> int:
        if not insights:
            return 0

        ids = [f"insight-{uuid4()}" for _ in insights]
        metadatas = [metadata for _ in insights]
        self.add_texts(ids=ids, texts=insights, metadatas=metadatas)
        return len(insights)

    def search(self, query: str, n_results: int = 5) -> str:
        sanitized_query = self.sanitize_text(query)
        if not sanitized_query:
            return "No semantic results found."

        query_embedding = self.embedding_provider.embed_text(sanitized_query)

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            if not documents:
                return "No semantic results found."

            rendered = []
            for index, document in enumerate(documents):
                metadata = metadatas[index] if index < len(metadatas) else {}
                source_type = metadata.get("source_type", "memory")
                rendered.append(f"[{source_type}] {document}")
            return "\n".join(rendered)
        except Exception:
            return "No semantic results found."
