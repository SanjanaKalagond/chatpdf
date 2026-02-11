import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.contrib.auth import get_user_model

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from .models import Document
from .services import get_user_document, answer_document_question
from llm.embeddings import HuggingFaceEmbeddingProvider

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
    )
    request.user = user


def get_llm_from_request(request):
    provider = request.META.get("HTTP_X_LLM_PROVIDER")
    api_key = request.META.get("HTTP_X_LLM_API_KEY")

    if not provider or not api_key:
        return None, "LLM provider or API key missing"

    provider = provider.lower().strip()

    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
            temperature=0,
        ), None

    if provider == "openai":
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=0,
        ), None

    return None, f"Unsupported LLM provider: {provider}"



@csrf_exempt
@require_POST
def upload_document(request):
    try:
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

    except PermissionDenied as e:
        return JsonResponse({"error": str(e)}, status=401)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
@require_POST
def query_document(request, document_id):
    try:
        api_auth(request)

        payload = json.loads(request.body or "{}")
        question = payload.get("question", "").strip()

        if not question:
            return JsonResponse({"error": "Question required"}, status=400)

        llm, error = get_llm_from_request(request)
        if error:
            return JsonResponse({"error": error}, status=400)

        document = get_user_document(request.user, document_id)

        log = answer_document_question(
            user=request.user,
            document=document,
            question=question,
            embedding_provider=HuggingFaceEmbeddingProvider(),
            llm=llm,
        )

        return JsonResponse(
            {
                "answer": log.answer,
                "latency_ms": log.latency_ms,
                "tokens_used": log.tokens_used,
            }
        )

    except PermissionDenied as e:
        return JsonResponse({"error": str(e)}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
