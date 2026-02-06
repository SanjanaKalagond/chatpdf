import time
from pathlib import Path
from django.core.exceptions import PermissionDenied
from .models import Document, QueryLog

from llm.graph import build_qa_graph
from llm.retrieval_faiss import load_faiss_store, retrieve_context_from_faiss
from llm.embeddings import EmbeddingProvider
from llm.vectorstore import FAISSVectorStore
from llm.chunking import chunk_text


def get_user_document(user, document_id):
    """ Fetch a document owned by the given user.
    Raises PermissionDenied if access is invalid. """
    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        raise PermissionDenied("Document does not exist")

    if document.owner != user:
        raise PermissionDenied("You do not own this document")
    return document


def log_query(document, question, answer="", latency_ms=None, tokens_used=None):
    """Log a user query against a document."""
    return QueryLog.objects.create(
        document=document,
        question=question,
        answer=answer,
        latency_ms=latency_ms,
        tokens_used=tokens_used,
    )

def answer_document_question(
    *,
    user,
    document,
    question: str,
    embedding_provider: EmbeddingProvider,
    llm,
    index_dir: Path = Path("vector_index"),
):
    start_time = time.time()
    index_ready = (
        index_dir is not None
        and index_dir.exists()
        and (index_dir / "index.faiss").exists()
    )

    if index_ready:
        vector_store = load_faiss_store(
            embedding_provider=embedding_provider,
            index_dir=index_dir,
        )
    else:
        vector_store = FAISSVectorStore(dim=embedding_provider.dim)
        document.pdf_file.open("rb")
        try:
            text = document.pdf_file.read().decode("utf-8", errors="ignore")
        finally:
            document.pdf_file.close()

        chunks = chunk_text(text)
        if chunks:
            embeddings = embedding_provider.embed(
                [c["chunk_text"] for c in chunks]
            )
            vector_store.add(embeddings, chunks)

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
    log = QueryLog.objects.create(
        document=document,
        question=question,
        answer=result.get("answer", "No answer generated."),
        latency_ms=latency_ms,
        tokens_used=result.get("tokens_used"),
    )
    log.citations = result.get("citations", [])

    return log
