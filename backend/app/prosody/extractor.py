import librosa
import numpy as np


class ProsodyExtractor:
    FILLER_WORDS = {
        "um",
        "uh",
        "erm",
        "hmm",
        "like",
        "you know",
    }

    def load_audio(self, audio_path: str):
        audio, sample_rate = librosa.load(
            audio_path,
            sr=None,
            mono=True,
        )

        return audio, sample_rate

    def calculate_wpm(
        self,
        text: str,
        duration_seconds: float,
    ) -> float:
        if duration_seconds <= 0:
            return 0.0

        words = text.split()

        if not words:
            return 0.0

        duration_minutes = duration_seconds / 60.0

        return len(words) / duration_minutes

    def count_filler_words(self, text: str) -> int:
        words = text.lower().split()

        return sum(
            1
            for word in words
            if word.strip(".,!?;:") in self.FILLER_WORDS
        )

    def detect_pauses(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> tuple[int, float]:
        intervals = librosa.effects.split(
            audio,
            top_db=30,
        )

        if len(intervals) <= 1:
            return 0, 0.0

        pause_count = 0
        pause_duration = 0.0

        for index in range(1, len(intervals)):
            previous_end = intervals[index - 1][1]
            current_start = intervals[index][0]

            pause = (
                current_start - previous_end
            ) / sample_rate

            if pause > 0:
                pause_count += 1
                pause_duration += pause

        return pause_count, pause_duration

    def calculate_pitch_variance(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> float:
        f0, _, _ = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
        )

        valid_pitch = f0[~np.isnan(f0)]

        if len(valid_pitch) == 0:
            return 0.0

        return float(np.var(valid_pitch))

    def extract(
        self,
        audio_path: str,
        text: str,
        start_time: float,
        end_time: float,
    ) -> dict:
        audio, sample_rate = self.load_audio(audio_path)

        start_sample = int(
            start_time * sample_rate
        )

        end_sample = int(
            end_time * sample_rate
        )

        segment_audio = audio[
            start_sample:end_sample
        ]

        duration = end_time - start_time

        wpm = self.calculate_wpm(
            text=text,
            duration_seconds=duration,
        )

        filler_word_count = self.count_filler_words(
            text
        )

        pause_count, pause_duration = (
            self.detect_pauses(
                segment_audio,
                sample_rate,
            )
        )

        pitch_variance = (
            self.calculate_pitch_variance(
                segment_audio,
                sample_rate,
            )
        )

        return {
            "wpm": wpm,
            "filler_word_count": filler_word_count,
            "pause_count": pause_count,
            "pause_duration": pause_duration,
            "pitch_variance": pitch_variance,
        }