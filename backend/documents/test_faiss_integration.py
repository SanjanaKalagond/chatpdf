from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from documents.models import Document
from documents.services import answer_document_question
from llm.embeddings import DummyEmbeddingProvider
from documents.tests import DummyLLM

User = get_user_model()

class DjangoFAISSIntegrationTests(TestCase):
    def test_django_answers_using_faiss_index(self):
        user = User.objects.create_user("alice", password="pass")
        doc = Document.objects.create(
            owner=user,
            filename="doc.txt",
        )
        doc.pdf_file.save(
            "doc.txt",
            ContentFile("LangChain is a framework for LLMs."),
        )
        log = answer_document_question(
            user=user,
            document=doc,
            question="What is LangChain?",
            embedding_provider=DummyEmbeddingProvider(),
            llm=DummyLLM(),
        )
        self.assertIsNotNone(log.answer)
        self.assertGreater(log.latency_ms, 0)
