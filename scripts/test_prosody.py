from pathlib import Path
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

from app.prosody.extractor import ProsodyExtractor


AUDIO_PATH = (
    PROJECT_ROOT
    / "data"
    / "audio"
    / "interview.wav"
)


def main():
    extractor = ProsodyExtractor()

    result = extractor.extract(
        audio_path=str(AUDIO_PATH),
        text=(
            "Sure. I'm a software engineer with "
            "about four years of experience."
        ),
        start_time=5.0,
        end_time=15.0,
    )

    print("=" * 60)
    print("PROSODY EXTRACTION")
    print("=" * 60)

    print(f"WPM: {result['wpm']:.2f}")
    print(
        "Filler words: "
        f"{result['filler_word_count']}"
    )
    print(
        "Pause count: "
        f"{result['pause_count']}"
    )
    print(
        "Pause duration: "
        f"{result['pause_duration']:.2f} seconds"
    )
    print(
        "Pitch variance: "
        f"{result['pitch_variance']:.2f}"
    )


if __name__ == "__main__":
    main()