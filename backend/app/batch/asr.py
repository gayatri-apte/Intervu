from faster_whisper import WhisperModel


class ASRTranscriber:
    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(self, audio_path: str) -> dict:
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
        )

        transcript_segments = []

        for segment in segments:
            transcript_segments.append(
                {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip(),
                }
            )

        full_text = " ".join(
            segment["text"]
            for segment in transcript_segments
        )

        return {
            "language": info.language,
            "duration": info.duration,
            "segments": transcript_segments,
            "text": full_text,
        }