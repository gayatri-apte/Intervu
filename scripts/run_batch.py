import json
import os
import sys

from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BACKEND_PATH = os.path.join(
    PROJECT_ROOT,
    "backend",
)

sys.path.insert(
    0,
    BACKEND_PATH,
)


from app.batch.asr import ASRTranscriber
from app.batch.diarization import SpeakerDiarizer
from app.batch.der import calculate_der
from app.batch.report import ReportGenerator


AUDIO_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "audio",
    "interview.wav",
)

GROUND_TRUTH_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "audio",
    "interview_ground_truth.json",
)

TRANSCRIPT_OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "transcripts",
    "batch_transcript.json",
)

REPORT_OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "reports",
    "basic_report.txt",
)

def load_ground_truth(path: str) -> list:

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def save_json(
    path: str,
    data,
):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )



def main():

    # Load backend/.env
    env_path = os.path.join(
        PROJECT_ROOT,
        "backend",
        ".env",
    )

    load_dotenv(env_path)

    print()
    print("=" * 60)
    print("PHASE 2 - BATCH INTERVIEW PIPELINE")
    print("=" * 60)

    # --------------------------------------------------
    # Check files
    # --------------------------------------------------

    if not os.path.exists(AUDIO_PATH):

        raise FileNotFoundError(
            f"Audio file not found:\n{AUDIO_PATH}"
        )

    if not os.path.exists(GROUND_TRUTH_PATH):

        raise FileNotFoundError(
            f"Ground truth file not found:\n"
            f"{GROUND_TRUTH_PATH}"
        )

    print(
        f"\nAudio:\n{AUDIO_PATH}"
    )

    print(
        f"\nGround truth:\n{GROUND_TRUTH_PATH}"
    )

    print()
    print("-" * 60)
    print("STEP 12 - FASTER-WHISPER ASR")
    print("-" * 60)

    asr = ASRTranscriber()

    transcription = asr.transcribe(
        AUDIO_PATH
    )

    print("\nASR completed.")

    print(
        f"Language: "
        f"{transcription['language']}"
    )

    print(
        f"Duration: "
        f"{transcription['duration']:.2f} seconds"
    )

    print(
        f"Segments: "
        f"{len(transcription['segments'])}"
    )

    print()
    print("-" * 60)
    print("STEP 13 - PYANNOTE DIARIZATION")
    print("-" * 60)

    diarizer = SpeakerDiarizer()

    diarization = diarizer.diarize(
        AUDIO_PATH
    )

    speakers = sorted(
        set(
            segment["speaker"]
            for segment in diarization
        )
    )

    print("\nDiarization completed.")

    print(
        f"Detected speakers: {speakers}"
    )

    print(
        f"Diarization segments: "
        f"{len(diarization)}"
    )

    print()
    print("-" * 60)
    print("STEP 14 - DER EVALUATION")
    print("-" * 60)

    ground_truth = load_ground_truth(
        GROUND_TRUTH_PATH
    )

    der = calculate_der(
        reference_segments=ground_truth,
        hypothesis_segments=diarization,
    )

    der_percentage = der * 100

    print(
        f"\nDER: {der:.4f}"
    )

    print(
        f"DER percentage: "
        f"{der_percentage:.2f}%"
    )

    batch_result = {

        "audio_file": AUDIO_PATH,

        "transcription": transcription,

        "diarization": diarization,

        "der": der,

        "der_percentage": der_percentage,
    }

    save_json(
        TRANSCRIPT_OUTPUT_PATH,
        batch_result,
    )

    print(
        f"\nSaved batch results:"
        f"\n{TRANSCRIPT_OUTPUT_PATH}"
    )

    print()
    print("-" * 60)
    print("STEP 15 - BASIC LLM REPORT")
    print("-" * 60)

    report_generator = ReportGenerator()

    report = report_generator.generate_report(
        transcription["text"]
    )

    os.makedirs(
        os.path.dirname(REPORT_OUTPUT_PATH),
        exist_ok=True,
    )

    with open(
        REPORT_OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(report)

    print(
        f"\nReport saved:"
        f"\n{REPORT_OUTPUT_PATH}"
    )

    print()
    print("=" * 60)
    print("PHASE 2 BATCH PIPELINE COMPLETED")
    print("=" * 60)

    print(
        f"\nASR segments: "
        f"{len(transcription['segments'])}"
    )

    print(
        f"Diarization segments: "
        f"{len(diarization)}"
    )

    print(
        f"DER: "
        f"{der_percentage:.2f}%"
    )

    print(
        f"\nResults:"
        f"\n{TRANSCRIPT_OUTPUT_PATH}"
    )

    print(
        f"\nReport:"
        f"\n{REPORT_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()