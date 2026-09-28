from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(
    0,
    str(BACKEND_DIR),
)

from app.rag.question_retriever import (
    QuestionRetriever,
)


def main():
    question_bank_path = (
        PROJECT_ROOT
        / "data"
        / "questions"
        / "question_bank.json"
    )

    retriever = QuestionRetriever(
        question_bank_path=str(
            question_bank_path
        )
    )

    query = (
        "I want to evaluate a candidate's "
        "understanding of binary search "
        "and algorithm complexity."
    )

    results = retriever.retrieve(
        query=query,
        limit=3,
    )

    print("=" * 60)
    print("QUESTION RETRIEVAL TEST")
    print("=" * 60)

    print(f"\nQuery:\n{query}\n")

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"{index}. "
            f"{result.payload['question']}"
        )

        print(
            f"   Category: "
            f"{result.payload['category']}"
        )

        print(
            f"   Difficulty: "
            f"{result.payload['difficulty']}"
        )

        print(
            f"   Score: "
            f"{result.score:.4f}"
        )

        print()


if __name__ == "__main__":
    main()