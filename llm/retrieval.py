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
    """
    End-to-end retrieval pipeline.

    Returns:
        context_text: str
        citations: List[chunk_metadata]

    Each chunk_metadata dict contains at least:
        - chunk_text
        - chunk_index
    """

    # -------------------------
    # 1. Chunk the document
    # -------------------------
    chunks = chunk_text(document_text)

    if not chunks:
        return "", []

    # -------------------------
    # 2. Embed chunks
    # -------------------------
    chunk_texts: List[str] = [c["chunk_text"] for c in chunks]
    chunk_embeddings = embedding_provider.embed(chunk_texts)

    # -------------------------
    # 3. Store embeddings + metadata
    # -------------------------
    vector_store.add(
        embeddings=chunk_embeddings,
        metadatas=chunks,
    )

    # -------------------------
    # 4. Embed the question
    # -------------------------
    query_embedding = embedding_provider.embed([question])[0]

    # -------------------------
    # 5. Retrieve top-k chunks
    # -------------------------
    citations: List[dict] = vector_store.search(
        query_embedding,
        k=k,
    )

    if not citations:
        # No retrieved context → downstream refusal
        return "", []

    # -------------------------
    # 6. Build context string
    # -------------------------
    context_text = "\n\n".join(
        c["chunk_text"] for c in citations
    )

    return context_text, citations
