import asyncio
import os

import edge_tts

from interview_script import interview_script


CLIPS_DIR = "data/audio/clips"


VOICE_MAP = {
    "interviewer": "en-GB-SoniaNeural",
    "candidate": "en-US-JennyNeural",
}


async def generate_clip(text: str, voice: str, output_path: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
    )

    await communicate.save(output_path)


def generate_clips():
    os.makedirs(CLIPS_DIR, exist_ok=True)

    clip_paths = []

    for index, (speaker, text) in enumerate(interview_script):

        voice = VOICE_MAP[speaker]

        print(
            f"Generating clip {index + 1}/{len(interview_script)} "
            f"for {speaker}..."
        )

        filename = f"{index:02d}_{speaker}.mp3"
        path = os.path.join(CLIPS_DIR, filename)

        asyncio.run(
            generate_clip(
                text=text,
                voice=voice,
                output_path=path,
            )
        )

        clip_paths.append(
            {
                "speaker": speaker,
                "path": path,
                "text": text,
            }
        )

    return clip_paths


if __name__ == "__main__":
    generate_clips()    