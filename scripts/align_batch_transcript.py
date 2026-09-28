from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.batch.alignment import align_transcript


BATCH_RESULT_PATH = (
    PROJECT_ROOT
    / "data"
    / "transcripts"
    / "batch_transcript.json"
)

ALIGNED_RESULT_PATH = (
    PROJECT_ROOT
    / "data"
    / "transcripts"
    / "aligned_transcript.json"
)


def load_batch_result() -> dict:
    with open(
        BATCH_RESULT_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    batch_result = load_batch_result()

    transcription = batch_result["transcription"]
    asr_segments = transcription["segments"]
    diarization_segments = batch_result["diarization"]

    aligned_segments = align_transcript(
        asr_segments=asr_segments,
        diarization_segments=diarization_segments,
    )

    result = {
        "audio_file": batch_result["audio_file"],
        "language": transcription["language"],
        "duration": transcription["duration"],
        "segments": aligned_segments,
        "text": transcription["text"],
        "der": batch_result["der"],
        "der_percentage": batch_result["der_percentage"],
    }

    with open(
        ALIGNED_RESULT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
        )

    print("=" * 60)
    print("TRANSCRIPT ALIGNMENT")
    print("=" * 60)
    print(f"ASR segments: {len(asr_segments)}")
    print(f"Diarization segments: {len(diarization_segments)}")
    print(f"Aligned segments: {len(aligned_segments)}")
    print()
    print(f"Saved to: {ALIGNED_RESULT_PATH}")


if __name__ == "__main__":
    main()