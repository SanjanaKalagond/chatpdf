import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import Document
from .services import (
    get_user_document,
    answer_document_question,
    log_query
)

from llm.embeddings import DummyEmbeddingProvider
from documents.tests import DummyLLM

@login_required
@require_POST
<<<<<<< HEAD
def query_document(request, document_id):  
=======
def query_document(request, document_id):
>>>>>>> bc46b94 (Committing)
    document = get_user_document(request.user, document_id)
    question = request.POST.get("question", "")
    query = log_query(document=document, question=question)
    return JsonResponse(
        {
            "document_id": document.id,
            "question": query.question,
            "message": "Query accepted",
        }
    )

<<<<<<< HEAD
=======

>>>>>>> bc46b94 (Committing)
@csrf_exempt
@require_POST
@login_required
def upload_document(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "No file provided"}, status=400)

    document = Document.objects.create(
        owner=request.user,
        filename=uploaded_file.name,
        pdf_file=uploaded_file,
    )

    return JsonResponse(
        {
            "document_id": document.id,
            "filename": document.filename,
        },
        status=201,
    )

@csrf_exempt
@require_POST
@login_required
def query_document(request, document_id):
    try:
        payload = json.loads(request.body)
        question = payload.get("question", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not question:
        return JsonResponse({"error": "Question required"}, status=400)

    document = get_user_document(request.user, document_id)

    log = answer_document_question(
        user=request.user,
        document=document,
        question=question,
        embedding_provider=DummyEmbeddingProvider(),  
        llm=DummyLLM(),                              
    )

    return JsonResponse(
        {
            "answer": log.answer,
            "citations": log.citations,
            "latency_ms": log.latency_ms,
            "tokens_used": log.tokens_used,
        }
    )
