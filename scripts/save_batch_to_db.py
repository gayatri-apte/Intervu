from pathlib import Path
import json
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(
    0,
    str(BACKEND_DIR),
)


from app.db.database import SessionLocal
from app.db.repository import InterviewRepository
from app.batch.alignment import align_transcript


BATCH_RESULT_PATH = (
    PROJECT_ROOT
    / "data"
    / "transcripts"
    / "batch_transcript.json"
)


def load_batch_result() -> dict:
    with open(
        BATCH_RESULT_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():

    if not BATCH_RESULT_PATH.exists():
        raise FileNotFoundError(
            f"Batch result not found: "
            f"{BATCH_RESULT_PATH}"
        )

    batch_result = load_batch_result()


    transcription = batch_result.get(
        "transcription",
        {},
    )

    duration = transcription.get(
        "duration"
    )

    asr_segments = transcription.get(
        "segments",
        [],
    )


    diarization_segments = batch_result.get(
        "diarization",
        [],
    )

    aligned_segments = align_transcript(
        asr_segments=asr_segments,
        diarization_segments=diarization_segments,
    )


    db = SessionLocal()

    try:

        repository = InterviewRepository(db)

        session = repository.create_session(
            duration=duration,
            status="completed",
        )

        print("=" * 60)
        print("SAVING BATCH RESULT TO SQLITE")
        print("=" * 60)

        print(
            f"Session created: {session.id}"
        )

        print(
            f"ASR segments: "
            f"{len(asr_segments)}"
        )

        print(
            f"Diarization segments: "
            f"{len(diarization_segments)}"
        )

        print(
            f"Aligned segments: "
            f"{len(aligned_segments)}"
        )

        for segment in aligned_segments:

            repository.save_transcript(
                session_id=session.id,
                question_id=None,
                speaker=segment["speaker"],
                start_time=segment["start"],
                end_time=segment["end"],
                text=segment["text"],
            )

        print()
        print(
            f"Transcript segments saved: "
            f"{len(aligned_segments)}"
        )

        print()
        print(
            "Question scores: not calculated yet"
        )

        print(
            "Prosody metrics: not calculated yet"
        )

        print()
        print(
            f"SQLite session ID: {session.id}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()