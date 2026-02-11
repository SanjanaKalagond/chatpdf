import time
from pathlib import Path
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.db import transaction
from .models import Document, QueryLog
from llm.chains import build_rag_chain
from llm.retrieval_faiss import load_faiss_store, retrieve_context_from_faiss
from llm.embeddings import EmbeddingProvider
from llm.vectorstore import FAISSVectorStore
from llm.chunking import chunk_text
from llm.grounding import enforce_grounding

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

def _rebuild_index(document: Document, embedding_provider: EmbeddingProvider):
    document.pdf_file.open("rb")
    try:
        raw = document.pdf_file.read()
    finally:
        document.pdf_file.close()

    text = raw.decode("utf-8", errors="ignore")
    chunks = chunk_text(text)
    texts = [c["chunk_text"] for c in chunks]
    embeddings = embedding_provider.embed(texts)

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

@transaction.atomic
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

    index_dir = _get_index_dir(document.id)

    if not index_dir.exists() or not document.is_processed:
        _rebuild_index(document, embedding_provider)

    start_time = time.time()

    try:
        vector_store = load_faiss_store(
            index_dir=index_dir,
            embedding_provider=embedding_provider,
        )
    except Exception:
        _rebuild_index(document, embedding_provider)
        vector_store = load_faiss_store(
            index_dir=index_dir,
            embedding_provider=embedding_provider,
        )

    context, citations = retrieve_context_from_faiss(
        question=question,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    chain = build_rag_chain(llm)
    raw_answer = chain.invoke(
        {
            "question": question,
            "context": context,
        }
    )

    answer = enforce_grounding(
        answer=raw_answer,
        citations=citations,
    )

    latency_ms = int((time.time() - start_time) * 1000)

    return QueryLog.objects.create(
        document=document,
        question=question,
        answer=answer,
        latency_ms=latency_ms,
        tokens_used=0,
    )
