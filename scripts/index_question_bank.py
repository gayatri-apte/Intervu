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

    count = retriever.index_questions()

    print("=" * 60)
    print("QUESTION BANK INDEXING")
    print("=" * 60)

    print(f"Questions indexed: {count}")
    print(
        f"Qdrant vectors stored: "
        f"{retriever.store.count()}"
    )


if __name__ == "__main__":
    main()