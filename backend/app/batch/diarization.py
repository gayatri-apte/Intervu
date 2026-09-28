import os

from dotenv import load_dotenv
from pyannote.audio import Pipeline


load_dotenv()


class SpeakerDiarizer:
    def __init__(self):
        hf_token = os.getenv("HF_TOKEN")

        if not hf_token:
            raise ValueError(
                "HF_TOKEN is not set. "
                "Add it to backend/.env"
            )

        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token,
        )

    def diarize(self, audio_path: str) -> list:
        output = self.pipeline(audio_path)

        # Newer Pyannote versions return DiarizeOutput.
        # The actual Annotation is stored here.
        diarization = output.speaker_diarization

        speaker_segments = []

        for turn, _, speaker in diarization.itertracks(
            yield_label=True
        ):
            speaker_segments.append({
                "start": round(turn.start, 2),
                "end": round(turn.end, 2),
                "speaker": speaker,
            })

        return speaker_segments