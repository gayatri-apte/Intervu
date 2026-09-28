from app.scoring.qa_extractor import (
    extract_question_answer_pairs,
)


def test_extract_question_answer_pairs():

    segments = [
        {
            "start": 0.0,
            "end": 5.0,
            "text": "Tell me about yourself.",
            "speaker": "SPEAKER_00",
        },
        {
            "start": 5.0,
            "end": 10.0,
            "text": "I am a software engineer.",
            "speaker": "SPEAKER_01",
        },
        {
            "start": 10.0,
            "end": 15.0,
            "text": "What technologies do you use?",
            "speaker": "SPEAKER_00",
        },
        {
            "start": 15.0,
            "end": 20.0,
            "text": "I mainly use Python.",
            "speaker": "SPEAKER_01",
        },
    ]

    pairs = extract_question_answer_pairs(
        segments
    )

    assert len(pairs) == 2

    assert (
        pairs[0]["question"]["text"]
        == "Tell me about yourself."
    )

    assert (
        pairs[0]["answer"]["text"]
        == "I am a software engineer."
    )

    assert (
        pairs[1]["question"]["text"]
        == "What technologies do you use?"
    )

    assert (
        pairs[1]["answer"]["text"]
        == "I mainly use Python."
    )