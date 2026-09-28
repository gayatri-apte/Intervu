from pathlib import Path
import json
import sys

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import SessionLocal
from app.db.models import Session
from app.db.repository import InterviewRepository
from app.prosody.extractor import ProsodyExtractor
from app.scoring.qa_extractor import (
    extract_question_answer_pairs,
)


AUDIO_PATH = (
    PROJECT_ROOT
    / "data"
    / "audio"
    / "interview.wav"
)

ALIGNED_TRANSCRIPT_PATH = (
    PROJECT_ROOT
    / "data"
    / "transcripts"
    / "aligned_transcript.json"
)

SESSION_ID = 2


def load_aligned_transcript():
    with open(
        ALIGNED_TRANSCRIPT_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():

    data = load_aligned_transcript()

    segments = data["segments"]

    # --------------------------------------------------
    # Extract the complete question/answer pairs.
    #
    # This gives us the actual candidate answer
    # boundaries:
    #
    # Q1 -> 5-15
    # Q2 -> 21-41
    # Q3 -> 48-61
    # Q4 -> 66-79
    # Q5 -> 84-98
    # Q6 -> 103-116
    # Q7 -> 121-129
    # --------------------------------------------------

    pairs = extract_question_answer_pairs(
        segments
    )

    db = SessionLocal()

    try:

        repository = InterviewRepository(db)
        extractor = ProsodyExtractor()

        session = (
            db.query(Session)
            .filter(
                Session.id == SESSION_ID
            )
            .first()
        )

        if session is None:
            raise ValueError(
                f"Session {SESSION_ID} was not found."
            )

        print("=" * 60)
        print("SAVING PROSODY METRICS")
        print("=" * 60)

        print(
            f"Session ID: {session.id}"
        )

        print(
            f"Question/Answer pairs: "
            f"{len(pairs)}"
        )

        # --------------------------------------------------
        # We are regenerating the prosody metrics.
        #
        # Delete the old records first so repeated runs
        # do not create duplicate prosody rows.
        # --------------------------------------------------

        db.execute(
            text(
                """
                DELETE FROM prosody_metrics
                WHERE session_id = :session_id
                """
            ),
            {
                "session_id": SESSION_ID
            },
        )

        db.commit()

        print(
            "Existing prosody records removed."
        )

        saved_count = 0

        # --------------------------------------------------
        # Process every complete candidate answer.
        # --------------------------------------------------

        for index, pair in enumerate(
            pairs,
            start=1,
        ):

            question_id = (
                f"session_{SESSION_ID}"
                f"_question_{index}"
            )

            answer = pair["answer"]

            answer_start = answer["start"]
            answer_end = answer["end"]
            answer_text = answer["text"]

            print()
            print("-" * 60)
            print(
                f"Question {index}"
            )
            print(
                f"Question ID: {question_id}"
            )
            print(
                f"Answer interval: "
                f"{answer_start:.2f} - "
                f"{answer_end:.2f}"
            )
            print(
                f"Answer: {answer_text}"
            )

            # --------------------------------------------------
            # Extract prosody over the COMPLETE answer.
            #
            # We deliberately do not check the diarization
            # speaker label here.
            # --------------------------------------------------

            result = extractor.extract(
                audio_path=str(AUDIO_PATH),
                text=answer_text,
                start_time=answer_start,
                end_time=answer_end,
            )

            # --------------------------------------------------
            # Save the prosody record directly with its
            # question ID.
            # --------------------------------------------------

            repository.save_prosody_metrics(
                session_id=session.id,
                question_id=question_id,
                wpm=result["wpm"],
                filler_word_count=result[
                    "filler_word_count"
                ],
                pause_count=result[
                    "pause_count"
                ],
                pause_duration=result[
                    "pause_duration"
                ],
                pitch_variance=result[
                    "pitch_variance"
                ],
            )

            saved_count += 1

            print(
                f"WPM: "
                f"{result['wpm']:.2f}"
            )

            print(
                f"Filler words: "
                f"{result['filler_word_count']}"
            )

            print(
                f"Pause count: "
                f"{result['pause_count']}"
            )

            print(
                f"Pause duration: "
                f"{result['pause_duration']:.2f} "
                f"seconds"
            )

            print(
                f"Pitch variance: "
                f"{result['pitch_variance']:.2f}"
            )

        print()
        print("=" * 60)
        print("PROSODY GENERATION COMPLETE")
        print("=" * 60)

        print(
            f"Prosody records saved: "
            f"{saved_count}"
        )

        # --------------------------------------------------
        # Verify that all expected question IDs now exist.
        # --------------------------------------------------

        saved_question_ids = db.execute(
            text(
                """
                SELECT question_id
                FROM prosody_metrics
                WHERE session_id = :session_id
                AND question_id IS NOT NULL
                ORDER BY id
                """
            ),
            {
                "session_id": SESSION_ID
            },
        ).fetchall()

        print()
        print(
            "Saved question IDs:"
        )

        for row in saved_question_ids:
            print(
                f"  {row[0]}"
            )

        if len(saved_question_ids) != len(pairs):
            raise ValueError(
                "Prosody verification failed: "
                f"expected {len(pairs)} records, "
                f"but found "
                f"{len(saved_question_ids)}."
            )

        print()
        print(
            "Verification successful."
        )

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()