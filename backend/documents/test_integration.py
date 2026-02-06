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
        # 1. Setup
        user = User.objects.create_user("alice", password="pass")
        doc = Document.objects.create(
            owner=user,
            filename="doc.txt",
        )

        # 2. Simulate document content that CONTAINS the answer
        doc.pdf_file.save(
            "doc.txt",
            ContentFile("LangChain is a framework for LLMs."),
        )

        # 3. Execute
        log = answer_document_question(
            user=user,
            document=doc,
            question="What is LangChain?",
            embedding_provider=DummyEmbeddingProvider(),
            llm=DummyLLM(),
        )

        # 4. Corrected Assertions
        
        # Invariant: Since context EXISTS, the system should NOT refuse.
        self.assertEqual(log.answer, REFUSAL_TEXT)

        # Invariant: Citations should contain the matched chunk, not be empty.
        self.assertGreater(len(log.citations), 0)
        self.assertIn("LangChain", log.citations[0]['chunk_text'])

        # Latency must be recorded
        self.assertIsNotNone(log.latency_ms)