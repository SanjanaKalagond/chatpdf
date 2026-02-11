from pathlib import Path
from django.conf import settings
from django.db import transaction
from .models import Document
from llm.chunking import chunk_text
from llm.embeddings import EmbeddingProvider
from llm.vectorstore import FAISSVectorStore

class IngestionError(Exception):
    pass

def get_document_index_dir(document_id: int) -> Path:
    return Path(settings.VECTOR_INDEX_ROOT) / f"document_{document_id}"

@transaction.atomic
def ingest_document(
    *,
    document: Document,
    embedding_provider: EmbeddingProvider,
) -> None:

    if document.is_processed:
        return

    if not document.pdf_file:
        raise IngestionError("Document has no file attached")

    document.pdf_file.open("rb")
    try:
        raw_bytes = document.pdf_file.read()
    finally:
        document.pdf_file.close()

    try:
        text = raw_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        raise IngestionError(f"Failed to decode document: {e}")

    if not text.strip():
        raise IngestionError("Document text is empty")

    chunks = chunk_text(text)
    if not chunks:
        raise IngestionError("No chunks produced during ingestion")

    texts = [c["chunk_text"] for c in chunks]
    embeddings = embedding_provider.embed(texts)

    if len(embeddings) != len(chunks):
        raise IngestionError("Embedding count mismatch")

    vector_store = FAISSVectorStore(dim=embedding_provider.dim)
    vector_store.add(
        embeddings=embeddings,
        metadatas=chunks,
    )

    index_dir = get_document_index_dir(document.id)

    if index_dir.exists():
        for f in index_dir.iterdir():
            f.unlink()
    else:
        index_dir.mkdir(parents=True, exist_ok=True)

    vector_store.save(index_dir)

    document.is_processed = True
    document.save(update_fields=["is_processed"])
