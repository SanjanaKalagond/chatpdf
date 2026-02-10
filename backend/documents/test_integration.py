from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from documents.models import Document
from documents.services import (
    answer_document_question,
    ingest_document_into_faiss,
)
from llm.embeddings import DummyEmbeddingProvider
from documents.tests import DummyLLM
from llm.prompts import REFUSAL_TEXT

User = get_user_model()


class EndToEndQATest(TestCase):
    def test_full_pipeline_after_ingestion(self):
        user = User.objects.create_user("alice", password="pass")

        doc = Document.objects.create(
            owner=user,
            filename="doc.txt",
        )

        doc.pdf_file.save(
            "doc.txt",
            ContentFile("LangChain is a framework for LLMs."),
        )

        ingest_document_into_faiss(
            document=doc,
            embedding_provider=DummyEmbeddingProvider(),
        )

        doc.refresh_from_db()
        self.assertTrue(doc.is_processed)

        log = answer_document_question(
            user=user,
            document=doc,
            question="What is LangChain?",
            embedding_provider=DummyEmbeddingProvider(),
            llm=DummyLLM(),
        )

        self.assertNotEqual(log.answer, REFUSAL_TEXT)
        self.assertIsNotNone(log.latency_ms)
