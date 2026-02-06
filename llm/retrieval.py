from typing import List, Tuple
from .chunking import chunk_text
from .embeddings import EmbeddingProvider
from .vectorstore import VectorStore

def retrieve_context(
    *,
    document_text: str,
    question: str,
    embedding_provider: EmbeddingProvider,
    vector_store: VectorStore,
    k: int = 5,
) -> Tuple[str, List[dict]]:
    chunks = chunk_text(document_text)

    if not chunks:
        return "", []
    chunk_texts: List[str] = [c["chunk_text"] for c in chunks]
    chunk_embeddings = embedding_provider.embed(chunk_texts)
    vector_store.add(
        embeddings=chunk_embeddings,
        metadatas=chunks,
    )

    query_embedding = embedding_provider.embed([question])[0]

    citations: List[dict] = vector_store.search(
        query_embedding,
        k=k,
    )

    if not citations:
        return "", []

    context_text = "\n\n".join(
        c["chunk_text"] for c in citations
    )

    return context_text, citations
