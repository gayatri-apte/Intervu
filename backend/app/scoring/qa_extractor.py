from typing import List, Dict


def _is_question(segment: Dict) -> bool:
    """
    Determine whether a transcript segment represents
    an interviewer question.

    For the current transcript, interviewer questions
    are represented as segments containing a question mark.
    """

    text = segment.get("text", "").strip()

    if not text:
        return False

    return "?" in text


def _build_pair(
    question: Dict,
    answer_parts: List[Dict],
) -> Dict:
    """
    Build one question-answer pair.
    """

    return {
        "question": {
            "start": question["start"],
            "end": question["end"],
            "text": question["text"],
            "speaker": question["speaker"],
        },
        "answer": {
            "start": answer_parts[0]["start"],
            "end": answer_parts[-1]["end"],
            "text": " ".join(
                item["text"]
                for item in answer_parts
            ),
            "speaker": answer_parts[0]["speaker"],
        },
    }


def extract_question_answer_pairs(
    segments: List[Dict],
) -> List[Dict]:
    """
    Extract interviewer-question / candidate-answer pairs.

    A new question starts a new pair regardless of whether
    diarization assigns the same speaker label to the
    interviewer and candidate.

    This is important because speaker diarization can
    occasionally switch or confuse speaker labels.

    Example:

        Interviewer question
            ↓
        Candidate answer
            ↓
        Candidate answer
            ↓
        Next interviewer question
            ↓
        Candidate answer

    The next question always terminates the previous answer.
    """

    pairs = []

    current_question = None
    current_answer_parts = []

    for segment in segments:

        text = segment.get("text", "").strip()

        if not text:
            continue

        segment = {
            **segment,
            "text": text,
        }

        # --------------------------------------------------
        # Detect a new question.
        # --------------------------------------------------

        if _is_question(segment):

            # If we already have a question and answer,
            # finish that pair before starting the new one.
            if (
                current_question is not None
                and current_answer_parts
            ):
                pairs.append(
                    _build_pair(
                        current_question,
                        current_answer_parts,
                    )
                )

            # Start the new question.
            current_question = segment
            current_answer_parts = []

            continue

        # --------------------------------------------------
        # Non-question segment.
        #
        # If a question has already been found, this segment
        # belongs to its answer.
        # --------------------------------------------------

        if current_question is not None:
            current_answer_parts.append(segment)

    # ------------------------------------------------------
    # Save the final question-answer pair.
    # ------------------------------------------------------

    if (
        current_question is not None
        and current_answer_parts
    ):
        pairs.append(
            _build_pair(
                current_question,
                current_answer_parts,
            )
        )

    return pairs