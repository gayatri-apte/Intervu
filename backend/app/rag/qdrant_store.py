from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)


class QdrantQuestionStore:
    COLLECTION_NAME = "question_bank"

    def __init__(
        self,
        vector_size: int,
        path: str = "data/qdrant",
    ):
        self.client = QdrantClient(
            path=path
        )

        self.vector_size = vector_size

        self._create_collection()

    def _create_collection(self):
        collections = self.client.get_collections()

        existing_names = {
            collection.name
            for collection in collections.collections
        }

        if self.COLLECTION_NAME not in existing_names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def add_questions(
        self,
        questions: list[dict],
        embeddings: list[list[float]],
    ):
        points = []

        for index, (
            question,
            embedding,
        ) in enumerate(
            zip(questions, embeddings)
        ):
            payload = {
                "question_id": question["id"],
                "question": question["question"],
                "category": question["category"],
                "difficulty": question["difficulty"],
                "tags": question.get("tags", []),
            }

            points.append(
                PointStruct(
                    id=index,
                    vector=embedding,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ):

        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            limit=limit,
        )

        return results.points

    def count(self) -> int:
        result = self.client.count(
            collection_name=self.COLLECTION_NAME,
        )

        return result.count