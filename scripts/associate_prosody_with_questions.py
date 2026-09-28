from pathlib import Path
import json
import sys

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import SessionLocal
from app.scoring.qa_extractor import (
    extract_question_answer_pairs,
)


SESSION_ID = 2

ALIGNED_TRANSCRIPT_PATH = (
    PROJECT_ROOT
    / "data"
    / "transcripts"
    / "aligned_transcript.json"
)


def load_transcript():
    with open(
        ALIGNED_TRANSCRIPT_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def overlaps(
    segment_start: float,
    segment_end: float,
    answer_start: float,
    answer_end: float,
) -> bool:
    """
    Return True when a transcript segment overlaps
    with the candidate's answer interval.
    """

    return (
        segment_start < answer_end
        and segment_end > answer_start
    )


def main():

    data = load_transcript()

    segments = data["segments"]

    pairs = extract_question_answer_pairs(
        segments
    )

    print("=" * 60)
    print("ASSOCIATING PROSODY WITH QUESTIONS")
    print("=" * 60)

    print(f"Session ID: {SESSION_ID}")
    print(
        f"Question/Answer pairs: {len(pairs)}"
    )

    db = SessionLocal()

    try:

        # --------------------------------------------------
        # Get all existing prosody records that have not
        # yet been associated with a question.
        # --------------------------------------------------

        rows = db.execute(
            text(
                """
                SELECT
                    id,
                    wpm,
                    filler_word_count,
                    pause_count,
                    pause_duration,
                    pitch_variance
                FROM prosody_metrics
                WHERE session_id = :session_id
                AND question_id IS NULL
                ORDER BY id
                """
            ),
            {
                "session_id": SESSION_ID
            },
        ).fetchall()

        print(
            f"Unassigned prosody records: {len(rows)}"
        )

        # --------------------------------------------------
        # Display the answer intervals detected from the
        # transcript.
        # --------------------------------------------------

        print()
        print("Detected answer intervals:")

        for index, pair in enumerate(
            pairs,
            start=1,
        ):

            answer = pair["answer"]

            print(
                f"Q{index}: "
                f"{answer['start']:.2f}-"
                f"{answer['end']:.2f}"
            )

        # --------------------------------------------------
        # We no longer use SPEAKER_00 here.
        #
        # The Q/A extractor already gives us the actual
        # candidate answer boundaries. Prosody records are
        # associated with questions using those boundaries.
        # --------------------------------------------------

        if not rows:
            raise ValueError(
                "No unassigned prosody records were found "
                f"for session {SESSION_ID}."
            )

        # --------------------------------------------------
        # Associate each existing prosody record with the
        # question whose answer interval it overlaps.
        #
        # We obtain the timing of each prosody record from
        # the transcript segments rather than assuming that
        # every SPEAKER_00 segment belongs to the candidate.
        # --------------------------------------------------

        updated_records = set()

        for segment in segments:

            segment_start = segment["start"]
            segment_end = segment["end"]

            # Find the unassigned prosody record that
            # corresponds to this transcript segment.
            matching_rows = [
                row
                for row in rows
                if row[0] not in updated_records
            ]

            if not matching_rows:
                break

            matched_row = None

            # Match based on the order in which the existing
            # prosody records were created.
            for row in matching_rows:

                prosody_id = row[0]

                matched_row = (
                    prosody_id,
                    row,
                )

                break

            if matched_row is None:
                continue

            prosody_id, row = matched_row

            matched_question_id = None

            # --------------------------------------------------
            # Check this segment against every candidate answer.
            # --------------------------------------------------

            for index, pair in enumerate(
                pairs,
                start=1,
            ):

                answer_start = (
                    pair["answer"]["start"]
                )

                answer_end = (
                    pair["answer"]["end"]
                )

                if overlaps(
                    segment_start,
                    segment_end,
                    answer_start,
                    answer_end,
                ):

                    matched_question_id = (
                        f"session_{SESSION_ID}"
                        f"_question_{index}"
                    )

                    break

            if matched_question_id is None:
                continue

            db.execute(
                text(
                    """
                    UPDATE prosody_metrics
                    SET question_id = :question_id
                    WHERE id = :prosody_id
                    """
                ),
                {
                    "question_id": matched_question_id,
                    "prosody_id": prosody_id,
                },
            )

            updated_records.add(
                prosody_id
            )

            print(
                f"Record {prosody_id}: "
                f"{segment_start:.2f}-"
                f"{segment_end:.2f} "
                f"→ {matched_question_id}"
            )

        # --------------------------------------------------
        # Commit the associations.
        # --------------------------------------------------

        db.commit()

        print()
        print("=" * 60)
        print("ASSOCIATION COMPLETE")
        print("=" * 60)

        print(
            f"Prosody records associated: "
            f"{len(updated_records)}"
        )

        print(
            f"Prosody records remaining: "
            f"{len(rows) - len(updated_records)}"
        )

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()