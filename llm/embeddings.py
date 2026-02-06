from abc import ABC, abstractmethod
from typing import List
import os

class EmbeddingProvider(ABC):
    """
    Interface for embedding providers.
    """

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        pass

    @property
    @abstractmethod
    def dim(self) -> int:
        pass

# --------------------------------------------------
# Dummy embeddings (tests, determinism, safety)
# --------------------------------------------------

class DummyEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic, cheap embeddings for tests.
    """

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Generates a vector based on text length for test consistency
        return [[float(len(t))] * self.dim for t in texts]

    @property
    def dim(self) -> int:
        return 5

# --------------------------------------------------
# OpenAI embeddings (production)
# --------------------------------------------------

class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    Real semantic embeddings using OpenAI.
    Safe for Codespaces using Environment Variables.
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in Codespace Secrets")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    @property
    def dim(self) -> int:
        # text-embedding-3-small defaults to 1536
        return 1536

# --------------------------------------------------
# HuggingFace (local - free for development)
# --------------------------------------------------

class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """
    Local embeddings using SentenceTransformers.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    @property
    def dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()