import json
import os
import time

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class ReportGenerator:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add it to backend/.env"
            )

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )

        self.client = Groq(
            api_key=api_key,
            max_retries=0,
        )

    # =========================================================
    # MAIN REPORT GENERATION
    # =========================================================

    def generate_report(
        self,
        session_data: dict,
    ) -> dict:

        print(
            "Preparing session data..."
        )

        prepared_data = self._prepare_data(
            session_data
        )

        print(
            "Generating narrative feedback with Groq..."
        )

        narrative = self._generate_narrative(
            prepared_data
        )

        print(
            "Building final structured report..."
        )

        report = self._build_final_report(
            prepared_data,
            narrative,
        )

        self._validate_report(
            report
        )

        print(
            "Report generated successfully."
        )

        return report

    # =========================================================
    # PREPARE DATA
    # =========================================================

    def _prepare_data(
        self,
        session_data: dict,
    ) -> dict:

        session = session_data.get(
            "session",
            {},
        )

        transcripts = session_data.get(
            "transcripts",
            [],
        )

        question_results = session_data.get(
            "question_results",
            [],
        )

        prosody_metrics = session_data.get(
            "prosody_metrics",
            [],
        )

        # -----------------------------------------------------
        # Sort transcript chronologically
        # -----------------------------------------------------

        transcripts = sorted(
            transcripts,
            key=lambda item: item.get(
                "start_time",
                0,
            ),
        )

        # -----------------------------------------------------
        # Build prosody lookup
        # -----------------------------------------------------

        prosody_by_question = {}

        for metric in prosody_metrics:

            question_id = metric.get(
                "question_id"
            )

            if question_id is None:
                continue

            question_id = str(
                question_id
            )

            prosody_by_question[
                question_id
            ] = {
                "wpm": self._number_or_zero(
                    metric.get("wpm")
                ),
                "filler_word_count": (
                    self._number_or_zero(
                        metric.get(
                            "filler_word_count"
                        )
                    )
                ),
                "pause_count": (
                    self._number_or_zero(
                        metric.get(
                            "pause_count"
                        )
                    )
                ),
                "pause_duration": (
                    self._number_or_zero(
                        metric.get(
                            "pause_duration"
                        )
                    )
                ),
                "pitch_variance": (
                    self._number_or_zero(
                        metric.get(
                            "pitch_variance"
                        )
                    )
                ),
            }

        # -----------------------------------------------------
        # Build score lookup
        # -----------------------------------------------------

        score_by_question = {}

        for result in question_results:

            question_id = str(
                result.get(
                    "question_id"
                )
            )

            score_by_question[
                question_id
            ] = {
                "relevance": self._number_or_zero(
                    result.get(
                        "relevance"
                    )
                ),
                "star_structure": (
                    self._number_or_zero(
                        result.get(
                            "star_structure"
                        )
                    )
                ),
                "completeness": (
                    self._number_or_zero(
                        result.get(
                            "completeness"
                        )
                    )
                ),
                "feedback": result.get(
                    "feedback",
                    "",
                ),
            }

        # -----------------------------------------------------
        # Extract question/answer pairs
        #
        # Important:
        # We identify questions from their text rather than
        # assuming specific speaker labels.
        # -----------------------------------------------------

        pairs = self._extract_question_answer_pairs(
            transcripts
        )

        questions = []

        for index, pair in enumerate(
            pairs,
            start=1,
        ):

            question_id = (
                f"session_"
                f"{session.get('id')}"
                f"_question_"
                f"{index}"
            )

            score = score_by_question.get(
                question_id,
                {
                    "relevance": 0,
                    "star_structure": 0,
                    "completeness": 0,
                    "feedback": "",
                },
            )

            prosody = prosody_by_question.get(
                question_id,
                {
                    "wpm": 0,
                    "filler_word_count": 0,
                    "pause_count": 0,
                    "pause_duration": 0,
                    "pitch_variance": 0,
                },
            )

            questions.append(
                {
                    "question_id": question_id,

                    "question": pair[
                        "question"
                    ],

                    "answer": pair[
                        "answer"
                    ],

                    "relevance": score[
                        "relevance"
                    ],

                    "star_structure": score[
                        "star_structure"
                    ],

                    "completeness": score[
                        "completeness"
                    ],

                    "feedback": score[
                        "feedback"
                    ],

                    "prosody": prosody,

                    "question_start": pair[
                        "question_start"
                    ],

                    "question_end": pair[
                        "question_end"
                    ],

                    "answer_start": pair[
                        "answer_start"
                    ],

                    "answer_end": pair[
                        "answer_end"
                    ],
                }
            )

        return {
            "session": {
                "id": session.get(
                    "id"
                ),
                "created_at": session.get(
                    "created_at"
                ),
                "duration": session.get(
                    "duration"
                ),
                "status": session.get(
                    "status"
                ),
            },
            "questions": questions,
        }

    # =========================================================
    # QUESTION / ANSWER EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_question_answer_pairs(
        transcripts: list,
    ) -> list:

        pairs = []

        current_question = None
        current_answer = []

        for segment in transcripts:

            text = segment.get(
                "text",
                "",
            ).strip()

            if not text:
                continue

            # -------------------------------------------------
            # A segment containing ? is treated as a question.
            # -------------------------------------------------

            if "?" in text:

                # Save previous Q/A pair
                if (
                    current_question is not None
                    and current_answer
                ):

                    pairs.append(
                        ReportGenerator
                        ._build_pair(
                            current_question,
                            current_answer,
                        )
                    )

                current_question = segment
                current_answer = []

                continue

            # -------------------------------------------------
            # Anything after the current question belongs to
            # its answer until the next question.
            # -------------------------------------------------

            if current_question is not None:

                current_answer.append(
                    segment
                )

        # -----------------------------------------------------
        # Save final pair
        # -----------------------------------------------------

        if (
            current_question is not None
            and current_answer
        ):

            pairs.append(
                ReportGenerator
                ._build_pair(
                    current_question,
                    current_answer,
                )
            )

        return pairs

    # =========================================================
    # BUILD QUESTION / ANSWER PAIR
    # =========================================================

    @staticmethod
    def _build_pair(
        question: dict,
        answer_parts: list,
    ) -> dict:

        question_text = question.get(
            "text",
            "",
        ).strip()

        answer_text = " ".join(
            segment.get(
                "text",
                "",
            ).strip()
            for segment in answer_parts
        ).strip()

        return {
            "question": question_text,

            "answer": answer_text,

            "question_start": question.get(
                "start_time",
                0,
            ),

            "question_end": question.get(
                "end_time",
                0,
            ),

            "answer_start": answer_parts[
                0
            ].get(
                "start_time",
                0,
            ),

            "answer_end": answer_parts[
                -1
            ].get(
                "end_time",
                0,
            ),
        }

    # =========================================================
    # GROQ NARRATIVE GENERATION
    # =========================================================

    def _generate_narrative(
        self,
        prepared_data: dict,
    ) -> dict:

        compact_questions = []

        for question in prepared_data[
            "questions"
        ]:

            compact_questions.append(
                {
                    "question_id": question[
                        "question_id"
                    ],

                    "question": question[
                        "question"
                    ],

                    "answer": question[
                        "answer"
                    ],

                    "relevance": question[
                        "relevance"
                    ],

                    "star_structure": question[
                        "star_structure"
                    ],

                    "completeness": question[
                        "completeness"
                    ],

                    "question_start": question[
                        "question_start"
                    ],

                    "question_end": question[
                        "question_end"
                    ],

                    "answer_start": question[
                        "answer_start"
                    ],

                    "answer_end": question[
                        "answer_end"
                    ],
                }
            )

        prompt_data = {
            "session_id": prepared_data[
                "session"
            ].get("id"),

            "questions": compact_questions,
        }

        prompt = f"""
You are an interview feedback report writer.

Analyze the interview session below.

Generate ONLY narrative feedback.

Do NOT generate scores.
Do NOT generate prosody values.
Do NOT change numeric values.
Do NOT reproduce the complete answers in your response.

For each question, generate concise feedback and
timestamped examples.

The timestamps supplied in the input are the ONLY
timestamps you may use.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "overall_summary": "2-4 sentence summary",
    "main_topics": [
        "topic 1",
        "topic 2"
    ],
    "candidate_points": [
        "specific observation 1",
        "specific observation 2"
    ],
    "question_feedback": [
        {{
            "question_id": "same question id",
            "feedback": "concise feedback",
            "timestamped_examples": [
                "[start-end] concise example"
            ]
        }}
    ],
    "overall_observation": "concise overall observation"
}}

Rules:

1. Preserve every question_id.
2. Create exactly one question_feedback object
   for every question.
3. Do not invent questions.
4. Do not invent candidate experiences.
5. Do not invent timestamps.
6. Keep feedback concise.
7. Use the supplied scores when discussing performance.
8. Use the actual question and answer content.
9. The final response must be valid JSON.
10. Do not include Markdown.
11. Do not include code fences.
12. Do not include text outside JSON.

SESSION DATA:

{json.dumps(
    prompt_data,
    indent=2,
)}
"""

        max_attempts = 2

        for attempt in range(
            max_attempts
        ):

            print(
                f"Sending narrative request to Groq "
                f"({attempt + 1}/{max_attempts})..."
            )

            try:

                response = (
                    self.client
                    .chat
                    .completions
                    .create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are an interview "
                                    "feedback report writer. "
                                    "Return only valid JSON."
                                ),
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],
                        temperature=0,
                        max_completion_tokens=3000,
                        response_format={
                            "type": "json_object"
                        },
                    )
                )

                print(
                    "Groq narrative response received."
                )

                if not response.choices:

                    raise ValueError(
                        "Groq returned no choices."
                    )

                response_text = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                if not response_text:

                    raise ValueError(
                        "Groq returned an empty response."
                    )

                response_text = (
                    response_text.strip()
                )

                try:

                    narrative = json.loads(
                        response_text
                    )

                except json.JSONDecodeError as exc:

                    print(
                        "\nGroq returned invalid JSON:"
                    )

                    print(
                        response_text
                    )

                    raise ValueError(
                        "Groq narrative response "
                        "was not valid JSON."
                    ) from exc

                self._validate_narrative(
                    narrative
                )

                return narrative

            except Exception as exc:

                error_message = str(
                    exc
                ).lower()

                print(
                    f"\nGroq request failed: {exc}"
                )

                if "429" in error_message:

                    if attempt == (
                        max_attempts - 1
                    ):
                        raise

                    print(
                        "Retrying after 5 seconds..."
                    )

                    time.sleep(5)

                    continue

                if any(
                    keyword in error_message
                    for keyword in (
                        "500",
                        "502",
                        "503",
                        "timeout",
                        "connection",
                        "service unavailable",
                    )
                ):

                    if attempt == (
                        max_attempts - 1
                    ):
                        raise

                    print(
                        "Retrying after 3 seconds..."
                    )

                    time.sleep(3)

                    continue

                raise

        raise RuntimeError(
            "Narrative generation failed."
        )

    # =========================================================
    # BUILD FINAL REPORT
    # =========================================================

    def _build_final_report(
        self,
        prepared_data: dict,
        narrative: dict,
    ) -> dict:

        narrative_feedback = {}

        for item in narrative.get(
            "question_feedback",
            [],
        ):

            question_id = str(
                item.get(
                    "question_id"
                )
            )

            narrative_feedback[
                question_id
            ] = item

        final_questions = []

        for question in prepared_data[
            "questions"
        ]:

            question_id = str(
                question[
                    "question_id"
                ]
            )

            feedback_data = (
                narrative_feedback.get(
                    question_id,
                    {}
                )
            )

            final_questions.append(
                {
                    "question_id": question_id,

                    "question": question[
                        "question"
                    ],

                    "answer": question[
                        "answer"
                    ],

                    # Scores come from SQLite.
                    "relevance": question[
                        "relevance"
                    ],

                    "star_structure": question[
                        "star_structure"
                    ],

                    "completeness": question[
                        "completeness"
                    ],

                    "feedback": feedback_data.get(
                        "feedback",
                        question.get(
                            "feedback",
                            ""
                        ),
                    ),

                    # Prosody comes from SQLite.
                    "prosody": question[
                        "prosody"
                    ],

                    "timestamped_examples": (
                        feedback_data.get(
                            "timestamped_examples",
                            []
                        )
                    ),
                }
            )

        return {
            "session_id": prepared_data[
                "session"
            ].get("id"),

            "overall_summary": narrative.get(
                "overall_summary",
                ""
            ),

            "main_topics": narrative.get(
                "main_topics",
                []
            ),

            "candidate_points": narrative.get(
                "candidate_points",
                []
            ),

            "questions": final_questions,

            "overall_observation": narrative.get(
                "overall_observation",
                ""
            ),
        }

    # =========================================================
    # VALIDATE NARRATIVE
    # =========================================================

    @staticmethod
    def _validate_narrative(
        narrative: dict,
    ):

        required_fields = {
            "overall_summary",
            "main_topics",
            "candidate_points",
            "question_feedback",
            "overall_observation",
        }

        missing = (
            required_fields
            - narrative.keys()
        )

        if missing:

            raise ValueError(
                "Narrative response is missing "
                f"fields: {missing}"
            )

        if not isinstance(
            narrative[
                "overall_summary"
            ],
            str,
        ):

            raise ValueError(
                "overall_summary must be a string."
            )

        if not isinstance(
            narrative[
                "main_topics"
            ],
            list,
        ):

            raise ValueError(
                "main_topics must be a list."
            )

        if not isinstance(
            narrative[
                "candidate_points"
            ],
            list,
        ):

            raise ValueError(
                "candidate_points must be a list."
            )

        if not isinstance(
            narrative[
                "question_feedback"
            ],
            list,
        ):

            raise ValueError(
                "question_feedback must be a list."
            )

        if not isinstance(
            narrative[
                "overall_observation"
            ],
            str,
        ):

            raise ValueError(
                "overall_observation must be a string."
            )

        for item in narrative[
            "question_feedback"
        ]:

            if not isinstance(
                item,
                dict,
            ):

                raise ValueError(
                    "Each question feedback "
                    "must be an object."
                )

            if "question_id" not in item:

                raise ValueError(
                    "question_feedback item "
                    "is missing question_id."
                )

            if "feedback" not in item:

                raise ValueError(
                    "question_feedback item "
                    "is missing feedback."
                )

            if (
                "timestamped_examples"
                not in item
            ):

                raise ValueError(
                    "question_feedback item "
                    "is missing "
                    "timestamped_examples."
                )

            if not isinstance(
                item[
                    "timestamped_examples"
                ],
                list,
            ):

                raise ValueError(
                    "timestamped_examples "
                    "must be a list."
                )

    # =========================================================
    # VALIDATE FINAL REPORT
    # =========================================================

    @staticmethod
    def _validate_report(
        report: dict,
    ):

        required_fields = {
            "session_id",
            "overall_summary",
            "main_topics",
            "candidate_points",
            "questions",
            "overall_observation",
        }

        missing = (
            required_fields
            - report.keys()
        )

        if missing:

            raise ValueError(
                f"Final report is missing "
                f"fields: {missing}"
            )

        if not isinstance(
            report["questions"],
            list,
        ):

            raise ValueError(
                "questions must be a list."
            )

        required_question_fields = {
            "question_id",
            "question",
            "answer",
            "relevance",
            "star_structure",
            "completeness",
            "feedback",
            "prosody",
            "timestamped_examples",
        }

        required_prosody_fields = {
            "wpm",
            "filler_word_count",
            "pause_count",
            "pause_duration",
            "pitch_variance",
        }

        for index, question in enumerate(
            report["questions"],
            start=1,
        ):

            missing_question_fields = (
                required_question_fields
                - question.keys()
            )

            if missing_question_fields:

                raise ValueError(
                    f"Question {index} is missing "
                    f"fields: "
                    f"{missing_question_fields}"
                )

            for field in (
                "relevance",
                "star_structure",
                "completeness",
            ):

                if not isinstance(
                    question[field],
                    (int, float),
                ):

                    raise ValueError(
                        f"Question {index} "
                        f"{field} must be numeric."
                    )

            if not isinstance(
                question["question"],
                str,
            ):

                raise ValueError(
                    f"Question {index} "
                    "question must be a string."
                )

            if not isinstance(
                question["answer"],
                str,
            ):

                raise ValueError(
                    f"Question {index} "
                    "answer must be a string."
                )

            prosody = question[
                "prosody"
            ]

            if not isinstance(
                prosody,
                dict,
            ):

                raise ValueError(
                    f"Question {index} "
                    "prosody must be an object."
                )

            missing_prosody_fields = (
                required_prosody_fields
                - prosody.keys()
            )

            if missing_prosody_fields:

                raise ValueError(
                    f"Question {index} "
                    "prosody is missing "
                    f"fields: "
                    f"{missing_prosody_fields}"
                )

            for field in (
                required_prosody_fields
            ):

                if not isinstance(
                    prosody[field],
                    (int, float),
                ):

                    raise ValueError(
                        f"Question {index} "
                        f"prosody.{field} "
                        "must be numeric."
                    )

    # =========================================================
    # HELPER
    # =========================================================

    @staticmethod
    def _number_or_zero(
        value,
    ):

        if value is None:
            return 0

        if isinstance(
            value,
            (int, float),
        ):

            return value

        try:

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return 0