from django.contrib import admin
from .models import Document, QueryLog


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "filename", "owner", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("filename",)


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "created_at", "latency_ms", "tokens_used")
    list_filter = ("created_at",)
    search_fields = ("question",)
