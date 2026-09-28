from app.batch.der import (
    calculate_der,
    create_annotation,
)


def test_create_annotation():

    segments = [
        {
            "start": 0.0,
            "end": 2.0,
            "speaker": "INTERVIEWER",
        },
        {
            "start": 2.0,
            "end": 5.0,
            "speaker": "CANDIDATE",
        },
    ]

    annotation = create_annotation(
        segments
    )

    assert annotation is not None


def test_identical_diarization_has_zero_der():

    segments = [
        {
            "start": 0.0,
            "end": 2.0,
            "speaker": "INTERVIEWER",
        },
        {
            "start": 2.0,
            "end": 5.0,
            "speaker": "CANDIDATE",
        },
    ]

    der = calculate_der(
        reference_segments=segments,
        hypothesis_segments=segments,
    )

    assert der == 0.0