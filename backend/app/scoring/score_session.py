from sqlalchemy.orm import Session as DBSession

from app.scoring.qa_extractor import (
    extract_question_answer_pairs,
)

from app.scoring.scoring_agent import (
    InterviewScoringAgent,
)

from app.db.repository import InterviewRepository

from app.db.models import QuestionResult


class SessionScorer:

    def __init__(self, db: DBSession):

        self.db = db

        self.repository = InterviewRepository(
            db
        )

        self.scoring_agent = InterviewScoringAgent()

    def score_session(
        self,
        session_id: int,
        segments: list[dict],
    ) -> list[dict]:

        # --------------------------------------------------
        # Extract question / answer pairs
        # --------------------------------------------------

        pairs = extract_question_answer_pairs(
            segments
        )

        # --------------------------------------------------
        # Display extracted pairs
        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("EXTRACTED QUESTION / ANSWER PAIRS")
        print("=" * 60)

        for index, pair in enumerate(
            pairs,
            start=1,
        ):

            question = pair["question"]
            answer = pair["answer"]

            print(f"\nQUESTION {index}")

            print(
                f"Q [{question['start']} - "
                f"{question['end']}] "
                f"{question['text']}"
            )

            print(
                f"A [{answer['start']} - "
                f"{answer['end']}] "
                f"{answer['text']}"
            )

        print("\n" + "=" * 60)

        # --------------------------------------------------
        # Remove previous scoring results for this session.
        #
        # This is necessary because the previous Question 4
        # result was generated using the incorrect Q/A
        # boundary.
        # --------------------------------------------------

        deleted_count = (
            self.db.query(QuestionResult)
            .filter(
                QuestionResult.session_id == session_id
            )
            .delete(
                synchronize_session=False
            )
        )

        self.db.commit()

        print(
            f"\nRemoved {deleted_count} existing "
            f"scoring results for session {session_id}."
        )

        # --------------------------------------------------
        # Score the newly extracted pairs
        # --------------------------------------------------

        results = []

        for index, pair in enumerate(
            pairs,
            start=1,
        ):

            question = pair["question"]
            answer = pair["answer"]

            question_id = (
                f"session_{session_id}_question_{index}"
            )

            print(
                f"\nScoring {question_id}..."
            )

            scoring_result = (
                self.scoring_agent.score(
                    question=question["text"],
                    answer=answer["text"],
                )
            )

            # --------------------------------------------------
            # Save scoring result
            # --------------------------------------------------

            saved_result = (
                self.repository.save_question_result(
                    session_id=session_id,
                    question_id=question_id,
                    relevance=scoring_result[
                        "relevance"
                    ],
                    star_structure=scoring_result[
                        "star_structure"
                    ],
                    completeness=scoring_result[
                        "completeness"
                    ],
                    feedback=scoring_result[
                        "feedback"
                    ],
                )
            )

            results.append(
                {
                    "id": saved_result.id,
                    "question_id": question_id,
                    "question": question["text"],
                    "answer": answer["text"],
                    "relevance": scoring_result[
                        "relevance"
                    ],
                    "star_structure": scoring_result[
                        "star_structure"
                    ],
                    "completeness": scoring_result[
                        "completeness"
                    ],
                    "feedback": scoring_result[
                        "feedback"
                    ],
                }
            )

        return results