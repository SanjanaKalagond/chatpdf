from django.db import models
from django.conf import settings
class Document(models.Model):
<<<<<<< HEAD
    """ Stores the uploaded PDF files and tracks their processing status """
=======
>>>>>>> bc46b94 (Committing)
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
<<<<<<< HEAD

class QueryLog(models.Model):
    """ Logs every interaction between the user and the LLM """
=======
class QueryLog(models.Model):
>>>>>>> bc46b94 (Committing)
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
