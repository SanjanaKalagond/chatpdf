from django.db import models
from django.conf import settings

class Document(models.Model):
    """
    Stores the uploaded PDF files and tracks their processing 
    status within the Databricks pipeline.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    # The actual PDF file saved to 'media/pdfs/'
    pdf_file = models.FileField(upload_to='pdfs/')
    
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Databricks Integration Fields
    # Set to True once the Databricks embedding job is finished
    is_processed = models.BooleanField(default=False)
    # Stores the Databricks job run ID for status tracking
    databricks_job_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.filename} ({self.owner.username})"


class QueryLog(models.Model):
    """
    Logs every interaction between the user and the LLM (LangGraph).
    Used for analytics and history.
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="queries",
    )
    question = models.TextField()
    answer = models.TextField(blank=True)
    
    # Performance and Cost Tracking
    latency_ms = models.IntegerField(null=True, blank=True)
    tokens_used = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query on {self.document.filename} at {self.created_at}"