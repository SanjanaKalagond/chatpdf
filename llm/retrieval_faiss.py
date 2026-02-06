from pathlib import Path
from typing import Tuple, List

from llm.vectorstore import FAISSVectorStore
from llm.embeddings import EmbeddingProvider

DEFAULT_INDEX_DIR = Path("vector_index")


def load_faiss_store(
    *,
    embedding_provider: EmbeddingProvider,
    index_dir: Path = DEFAULT_INDEX_DIR,
) -> FAISSVectorStore:
    """
    Load a persisted FAISS vector store from disk.

    Expects:
      - index.faiss
      - metadatas.npy
    """
    store = FAISSVectorStore(dim=embedding_provider.dim)

    store.load(
        index_path=index_dir / "index.faiss",
        metadata_path=index_dir / "metadatas.npy",
    )

    return store


def retrieve_context_from_faiss(
    *,
    question: str,
    embedding_provider: EmbeddingProvider,
    vector_store: FAISSVectorStore,
    k: int = 3,
) -> Tuple[str, List[dict]]:
    """
    Retrieve grounded context + citations from FAISS.
    """

    query_embedding = embedding_provider.embed([question])[0]

    citations: List[dict] = vector_store.search(
        query_embedding=query_embedding,
        k=k,
    )

    if not citations:
        # No retrieved context → downstream refusal
        return "", []

    context = "\n\n".join(c["chunk_text"] for c in citations)

    return context, citations
