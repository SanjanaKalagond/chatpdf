import time
from pathlib import Path

from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.db import transaction

from .models import Document, QueryLog
from llm.graph import build_qa_graph
from llm.retrieval_faiss import load_faiss_store, retrieve_context_from_faiss
from llm.embeddings import EmbeddingProvider
from llm.vectorstore import FAISSVectorStore
from llm.chunking import chunk_text

def get_user_document(user, document_id):
    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        raise PermissionDenied("Document does not exist")
    if document.owner != user:
        raise PermissionDenied("You do not own this document")

    return document

def log_query(document, question, answer="", latency_ms=None, tokens_used=None):
    return QueryLog.objects.create(
        document=document,
        question=question,
        answer=answer,
        latency_ms=latency_ms,
        tokens_used=tokens_used,
    )


def _get_index_dir(document_id: int) -> Path:
    return Path(settings.VECTOR_INDEX_ROOT) / f"document_{document_id}"


@transaction.atomic
def ingest_document_into_faiss(
    *,
    document: Document,
    embedding_provider: EmbeddingProvider,
):
    if not document.pdf_file:
        raise RuntimeError("Document has no file")

    document.pdf_file.open("rb")
    try:
        raw = document.pdf_file.read()
    finally:
        document.pdf_file.close()

    text = raw.decode("utf-8", errors="ignore")

    if not text.strip():
        raise RuntimeError("Empty document")

    chunks = chunk_text(text)
    if not chunks:
        raise RuntimeError("No chunks produced")

    texts = [c["chunk_text"] for c in chunks]
    embeddings = embedding_provider.embed(texts)

    if len(embeddings) != len(chunks):
        raise RuntimeError("Embedding mismatch")

    vector_store = FAISSVectorStore(dim=embedding_provider.dim)
    vector_store.add(embeddings, chunks)

    index_dir = _get_index_dir(document.id)

    if index_dir.exists():
        for f in index_dir.iterdir():
            f.unlink()
    else:
        index_dir.mkdir(parents=True, exist_ok=True)

    vector_store.save(index_dir)

    document.is_processed = True
    document.save(update_fields=["is_processed"])


def answer_document_question(
    *,
    user,
    document: Document,
    question: str,
    embedding_provider: EmbeddingProvider,
    llm,
):
    normalized = question.strip().lower()
    if normalized in {"hi", "hello", "hey", "thanks", "thank you"}:
        return QueryLog.objects.create(
            document=document,
            question=question,
            answer="Hi! Ask me a question about the document.",
            latency_ms=0,
            tokens_used=0,
        )

    if not document.is_processed:
        return QueryLog.objects.create(
            document=document,
            question=question,
            answer="I don't know based on the provided documents.",
            latency_ms=None,
            tokens_used=None,
        )

    index_dir = _get_index_dir(document.id)

    if not index_dir.exists():
        raise RuntimeError("FAISS index missing for processed document")

    start_time = time.time()

    vector_store = load_faiss_store(
        index_dir=index_dir,
        embedding_provider=embedding_provider,
    )

    context, citations = retrieve_context_from_faiss(
        question=question,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    graph = build_qa_graph(llm)

    result = graph.invoke(
        {
            "question": question,
            "context": context,
            "citations": citations,
            "answer": None,
            "error": None,
            "tokens_used": None,
        }
    )

    latency_ms = int((time.time() - start_time) * 1000)

    return QueryLog.objects.create(
        document=document,
        question=question,
        answer=result.get("answer"),
        latency_ms=latency_ms,
        tokens_used=result.get("tokens_used"),
    )
