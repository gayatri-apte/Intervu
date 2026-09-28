from pathlib import Path
import json
import sys

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(
    PROJECT_ROOT / "backend" / ".env"
)

BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(
    0,
    str(BACKEND_DIR),
)


from app.db.database import SessionLocal
from app.scoring.score_session import SessionScorer


ALIGNED_TRANSCRIPT_PATH = (
    PROJECT_ROOT
    / "data"
    / "transcripts"
    / "aligned_transcript.json"
)


def load_aligned_transcript():

    with open(
        ALIGNED_TRANSCRIPT_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():

    data = load_aligned_transcript()

    db = SessionLocal()

    try:

        # Use the most recent session for now.
        from app.db.models import Session

        session = (
            db.query(Session)
            .order_by(Session.id.desc())
            .first()
        )

        if session is None:
            raise ValueError(
                "No interview session exists in SQLite."
            )

        scorer = SessionScorer(db)

        results = scorer.score_session(
            session_id=session.id,
            segments=data["segments"],
        )

        print("=" * 60)
        print("SESSION SCORING")
        print("=" * 60)

        print(
            f"Session ID: {session.id}"
        )

        print(
            f"Questions scored: {len(results)}"
        )

        for index, result in enumerate(
            results,
            start=1,
        ):

            print()
            print(
                f"Question {index}: "
                f"{result['question']}"
            )

            print(
                f"Relevance: "
                f"{result['relevance']}/5"
            )

            print(
                f"STAR Structure: "
                f"{result['star_structure']}/5"
            )

            print(
                f"Completeness: "
                f"{result['completeness']}/5"
            )

            print(
                f"Feedback: "
                f"{result['feedback']}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()