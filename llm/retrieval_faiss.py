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
    store = FAISSVectorStore(dim=embedding_provider.dim)
    store.load(index_dir)

    if store.index.d != embedding_provider.dim:
        raise ValueError(
            f"Embedding dim mismatch: index={store.index.d}, provider={embedding_provider.dim}"
        )

    return store

def retrieve_context_from_faiss(
    *,
    question: str,
    embedding_provider: EmbeddingProvider,
    vector_store: FAISSVectorStore,
    k: int = 200,
) -> Tuple[str, List[dict]]:
    query_embedding = embedding_provider.embed([question])[0]

    citations: List[dict] = vector_store.search(
        query_embedding=query_embedding,
        k=k,
    )

    if not citations:
        return "", []

    context = "\n\n".join(
        c["chunk_text"]
        for c in citations
        if isinstance(c, dict) and "chunk_text" in c
    )

    return context, citations
