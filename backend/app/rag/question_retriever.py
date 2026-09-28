from pathlib import Path
import json

from app.rag.embeddings import QuestionEmbedder
from app.rag.qdrant_store import QdrantQuestionStore


class QuestionRetriever:
    def __init__(
        self,
        question_bank_path: str,
    ):
        self.question_bank_path = Path(
            question_bank_path
        )

        self.embedder = QuestionEmbedder()

        self.store = QdrantQuestionStore(
            vector_size=self.embedder.dimension
        )

    def load_question_bank(self) -> list[dict]:
        with open(
            self.question_bank_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def index_questions(self):
        questions = self.load_question_bank()

        texts = [
            self._question_text(question)
            for question in questions
        ]

        embeddings = self.embedder.embed_many(
            texts
        )

        self.store.add_questions(
            questions,
            embeddings,
        )

        return len(questions)

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ):
        query_embedding = self.embedder.embed(
            query
        )

        return self.store.search(
            query_embedding,
            limit=limit,
        )

    @staticmethod
    def _question_text(
        question: dict,
    ) -> str:
        tags = ", ".join(
            question.get("tags", [])
        )

        return (
            f"Question: {question['question']}. "
            f"Category: {question['category']}. "
            f"Difficulty: {question['difficulty']}. "
            f"Tags: {tags}."
        )