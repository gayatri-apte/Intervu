from app.batch.alignment import (
    calculate_overlap,
    find_speaker,
    align_transcript,
)


def test_calculate_overlap():
    overlap = calculate_overlap(
        0.0,
        3.0,
        2.0,
        5.0,
    )

    assert overlap == 1.0


def test_find_speaker():
    asr_segment = {
        "start": 2.0,
        "end": 4.0,
        "text": "Hello",
    }

    diarization_segments = [
        {
            "start": 0.0,
            "end": 1.5,
            "speaker": "SPEAKER_00",
        },
        {
            "start": 1.5,
            "end": 5.0,
            "speaker": "SPEAKER_01",
        },
    ]

    speaker = find_speaker(
        asr_segment,
        diarization_segments,
    )

    assert speaker == "SPEAKER_01"


def test_align_transcript():
    asr_segments = [
        {
            "start": 0.0,
            "end": 2.0,
            "text": "Hello",
        },
        {
            "start": 2.0,
            "end": 5.0,
            "text": "Tell me about yourself",
        },
    ]

    diarization_segments = [
        {
            "start": 0.0,
            "end": 2.0,
            "speaker": "SPEAKER_00",
        },
        {
            "start": 2.0,
            "end": 5.0,
            "speaker": "SPEAKER_01",
        },
    ]

    result = align_transcript(
        asr_segments,
        diarization_segments,
    )

    assert len(result) == 2
    assert result[0]["speaker"] == "SPEAKER_00"
    assert result[1]["speaker"] == "SPEAKER_01"