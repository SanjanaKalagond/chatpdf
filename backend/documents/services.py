import time
from django.core.exceptions import PermissionDenied

from .models import Document, QueryLog


def get_user_document(user, document_id):
    """
    Fetch a document owned by the given user.
    Raises PermissionDenied if access is invalid.
    """
    try:
        document = Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        raise PermissionDenied("Document does not exist")

    if document.owner != user:
        raise PermissionDenied("You do not own this document")

    return document


def log_query(document, question, answer="", latency_ms=None, tokens_used=None):
    """
    Log a user query against a document.
    """
    return QueryLog.objects.create(
        document=document,
        question=question,
        answer=answer,
        latency_ms=latency_ms,
        tokens_used=tokens_used,
    )


def run_qa(graph, *, document, question: str, context: str):
    """
    Execute a LangGraph QA flow and persist the result.

    - graph: compiled LangGraph
    - document: Document instance (already ownership-validated)
    - question: user question
    - context: retrieved context (can be empty)

    Returns:
        QueryLog instance
    """
    start_time = time.time()

    # Execute graph
    result = graph.invoke(
        {
            "question": question,
            "context": context,
            "answer": None,
            "error": None,
        }
    )

    latency_ms = int((time.time() - start_time) * 1000)

    answer = result.get("answer", "")
    tokens_used = result.get("tokens_used")  # optional, may be None

    return log_query(
        document=document,
        question=question,
        answer=answer,
        latency_ms=latency_ms,
        tokens_used=tokens_used,
    )
