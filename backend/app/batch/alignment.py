def calculate_overlap(
    start_a: float,
    end_a: float,
    start_b: float,
    end_b: float,
) -> float:
    overlap_start = max(start_a, start_b)
    overlap_end = min(end_a, end_b)

    if overlap_end <= overlap_start:
        return 0.0

    return overlap_end - overlap_start


def find_speaker(
    asr_segment: dict,
    diarization_segments: list[dict],
) -> str:
    asr_start = asr_segment["start"]
    asr_end = asr_segment["end"]

    best_speaker = "UNKNOWN"
    best_overlap = 0.0

    for diarization in diarization_segments:
        overlap = calculate_overlap(
            asr_start,
            asr_end,
            diarization["start"],
            diarization["end"],
        )

        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = diarization["speaker"]

    return best_speaker


def align_transcript(
    asr_segments: list[dict],
    diarization_segments: list[dict],
) -> list[dict]:
    aligned_segments = []

    for segment in asr_segments:
        speaker = find_speaker(
            segment,
            diarization_segments,
        )

        aligned_segments.append(
            {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"],
                "speaker": speaker,
            }
        )

    return aligned_segments