from abc import ABC, abstractmethod
from typing import List
import os
class EmbeddingProvider(ABC):

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        pass

    @property
    @abstractmethod
    def dim(self) -> int:
        pass

class DummyEmbeddingProvider(EmbeddingProvider):

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [[float(len(t))] * self.dim for t in texts]

    @property
    def dim(self) -> int:
        return 5

class OpenAIEmbeddingProvider(EmbeddingProvider):
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
        return 1536

class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    _model = None

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if HuggingFaceEmbeddingProvider._model is None:
            from sentence_transformers import SentenceTransformer
            HuggingFaceEmbeddingProvider._model = SentenceTransformer(model_name)

        self.model = HuggingFaceEmbeddingProvider._model

    def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    @property
    def dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()
