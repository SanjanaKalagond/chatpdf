from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .services import get_user_document, log_query


@login_required
@require_POST
def query_document(request, document_id):
    """
    Dummy endpoint to test ownership enforcement.
    """
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

