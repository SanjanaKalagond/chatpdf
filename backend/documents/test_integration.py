from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from documents.models import Document
from documents.services import answer_document_question

from llm.embeddings import DummyEmbeddingProvider
from documents.tests import DummyLLM
from llm.prompts import REFUSAL_TEXT

User = get_user_model()


class EndToEndQATest(TestCase):
    def test_full_pipeline_runs(self):
        # 1. Setup - Create a user and a document record
        user = User.objects.create_user("alice", password="pass")
        doc = Document.objects.create(
            owner=user,
            filename="doc.txt",
        )

        # 2. Simulate uploaded document content
        doc.pdf_file.save(
            "doc.txt",
            ContentFile("LangChain is a framework for LLMs."),
        )

        # 3. Execute full pipeline
        log = answer_document_question(
            user=user,
            document=doc,
            question="What is LangChain?",
            embedding_provider=DummyEmbeddingProvider(),
            llm=DummyLLM(),
        )

        # 4. Assertions
        # DummyLLM hallucinates → grounding layer must refuse
        self.assertEqual(log.answer, REFUSAL_TEXT)

        # Latency should always be recorded
        self.assertIsNotNone(log.latency_ms)
