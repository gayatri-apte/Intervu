import json
import os

from pydub import AudioSegment

from interview_script import interview_script


CLIPS_DIR = "data/audio/clips"
OUTPUT_DIR = "data/audio"

PAUSE_MS = 600


def stitch_audio():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    final_audio = AudioSegment.empty()

    ground_truth = []

    current_time_ms = 0

    for index, (speaker, text) in enumerate(interview_script):

        filename = f"{index:02d}_{speaker}.mp3"

        path = os.path.join(
            CLIPS_DIR,
            filename,
        )

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Audio clip not found: {path}"
            )

        clip = AudioSegment.from_mp3(path)

        start = current_time_ms / 1000

        final_audio += clip

        current_time_ms += len(clip)

        end = current_time_ms / 1000

        ground_truth.append(
            {
                "start": round(start, 2),
                "end": round(end, 2),
                "speaker": speaker,
                "text": text,
            }
        )

        pause = AudioSegment.silent(
            duration=PAUSE_MS
        )

        final_audio += pause

        current_time_ms += PAUSE_MS

    # Convert to format suitable for speech processing
    final_audio = (
        final_audio
        .set_frame_rate(16000)
        .set_channels(1)
    )

    audio_path = os.path.join(
        OUTPUT_DIR,
        "interview.wav",
    )

    final_audio.export(
        audio_path,
        format="wav",
    )

    ground_truth_path = os.path.join(
        OUTPUT_DIR,
        "interview_ground_truth.json",
    )

    with open(
        ground_truth_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            ground_truth,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Saved audio: {audio_path}")
    print(
        f"Saved ground truth: {ground_truth_path}"
    )


if __name__ == "__main__":
    stitch_audio()