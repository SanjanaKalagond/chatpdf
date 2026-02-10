from django.db import models
from django.conf import settings
class Document(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    pdf_file = models.FileField(upload_to='pdfs/')    
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    databricks_job_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.filename} ({self.owner.username})"
class QueryLog(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="queries",
    )
    question = models.TextField()
    answer = models.TextField(blank=True)
    
    latency_ms = models.IntegerField(null=True, blank=True)
    tokens_used = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query on {self.document.filename} at {self.created_at}"
