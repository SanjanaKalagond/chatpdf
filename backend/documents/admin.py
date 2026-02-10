from django.contrib import admin
from django.contrib import messages
from .models import Document, QueryLog
from .ingestion import ingest_document
from llm.embeddings import DummyEmbeddingProvider

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "filename",
        "owner",
        "uploaded_at",
        "is_processed",
    )
    list_filter = (
        "uploaded_at",
        "owner",
        "is_processed",
    )
    search_fields = (
        "filename",
        "owner__username",
    )
    ordering = ("-uploaded_at",)

    readonly_fields = ("uploaded_at", "is_processed")

    actions = ["rebuild_faiss_index"]

    @admin.action(description="Ingest (build FAISS index)")
    def rebuild_faiss_index(self, request, queryset):
        embedding_provider = DummyEmbeddingProvider()

        rebuilt = 0
        skipped = 0
        failed = 0

        for document in queryset:
            if not document.pdf_file:
                skipped += 1
                continue

            try:
                ingest_document(
                    document=document,
                    embedding_provider=embedding_provider,
                )
                rebuilt += 1
            except Exception as e:
                failed += 1
                self.message_user(
                    request,
                    f"Failed to ingest document {document.id}: {e}",
                    level=messages.ERROR,
                )

        self.message_user(
            request,
            f"Ingestion complete — rebuilt: {rebuilt}, skipped: {skipped}, failed: {failed}.",
            level=messages.SUCCESS,
        )


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "created_at", "latency_ms", "tokens_used")
    list_filter = ("created_at",)
    search_fields = ("question",)
