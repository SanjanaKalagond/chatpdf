from django.urls import path
from .views import upload_document, query_document

urlpatterns = [
    path("documents/upload/", upload_document),
    path("documents/<int:document_id>/query/", query_document),
]
