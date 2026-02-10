import json
import os

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.contrib.auth import get_user_model

from langchain_google_genai import ChatGoogleGenerativeAI

from .models import Document
from .services import get_user_document, answer_document_question
from llm.embeddings import DummyEmbeddingProvider

<<<<<<< Updated upstream
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
=======
User = get_user_model()


def api_auth(request):
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Bearer "):
        raise PermissionDenied("Missing token")
    token = auth.split(" ", 1)[1]
    if token != settings.STREAMLIT_API_KEY:
        raise PermissionDenied("Invalid token")
    user, _ = User.objects.get_or_create(
        username="streamlit_service_user",
        defaults={"is_active": True},
>>>>>>> Stashed changes
    )
    request.user = user


def get_llm():
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("LLM API key not set")
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=api_key,
        temperature=0,
    )


<<<<<<< HEAD
=======

>>>>>>> bc46b94 (Committing)
@csrf_exempt
@require_POST
def upload_document(request):
    api_auth(request)

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
def query_document(request, document_id):
    api_auth(request)

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
        llm=get_llm(),
    )

    return JsonResponse(
        {
            "answer": log.answer,
            "latency_ms": log.latency_ms,
            "tokens_used": log.tokens_used,
        }
    )
