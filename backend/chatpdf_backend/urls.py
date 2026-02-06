from django.contrib import admin
from django.urls import path
from documents.views import query_document

urlpatterns = [
    path("admin/", admin.site.urls),
    path("documents/<int:document_id>/query/", query_document),
]
