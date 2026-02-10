from typing import List
import numpy as np
from abc import ABC, abstractmethod
from pathlib import Path

class VectorStore(ABC):
    @abstractmethod
    def add(self, embeddings: List[List[float]], metadatas: List[dict]):
        pass
    @abstractmethod
    def search(self, query_embedding: List[float], k: int = 5) -> List[dict]:
        pass
        
class InMemoryVectorStore(VectorStore):

    def __init__(self):
        self.vectors = []
        self.metadatas = []

    def add(self, embeddings: List[List[float]], metadatas: List[dict]):
        if len(embeddings) != len(metadatas):
            raise ValueError("Embeddings and metadata length mismatch")
        self.vectors.extend(embeddings)
        self.metadatas.extend(metadatas)

    def search(self, query_embedding: List[float], k: int = 5) -> List[dict]:
        if not self.vectors:
            return []

        scores = []
        for vec, meta in zip(self.vectors, self.metadatas):
            score = np.dot(vec, query_embedding)
            scores.append((score, meta))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scores[:k]]

class FAISSVectorStore(VectorStore):
    def __init__(self, dim: int):
        import faiss
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.metadatas: List[dict] = []

    def add(self, embeddings: List[List[float]], metadatas: List[dict]):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.metadatas.extend(metadatas)

    def search(self, query_embedding: List[float], k: int = 5) -> List[dict]:
        if self.index.ntotal == 0:
            return []
        query = np.array([query_embedding]).astype("float32")
        _, indices = self.index.search(query, k)

        results = []
        for idx in indices[0]:
            if idx == -1:
                continue
            results.append(self.metadatas[idx])

        return results

    def save(self, path: Path) -> None:
        import faiss

        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(path / "index.faiss"))
        np.save(path / "metadatas.npy", np.array(self.metadatas, dtype=object))

    def load(self, index_path: Path) -> None:

        import faiss

        path = Path(path)

        self.index = faiss.read_index(str(path / "index.faiss"))
        self.metadatas = np.load(
            path / "metadatas.npy",
            allow_pickle=True,
        ).tolist()

