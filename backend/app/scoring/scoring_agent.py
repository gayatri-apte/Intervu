import json
import os
import time

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class InterviewScoringAgent:

    def __init__(self):

        # --------------------------------------------------
        # Groq API key
        # --------------------------------------------------

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add it to backend/.env"
            )

        # --------------------------------------------------
        # Groq model
        # --------------------------------------------------

        model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )

        self.model = model

        # --------------------------------------------------
        # Groq client
        # --------------------------------------------------

        self.client = Groq(
            api_key=api_key
        )

    def score(
        self,
        question: str,
        answer: str,
    ) -> dict:

        prompt = f"""
You are an interview answer evaluation agent.

Evaluate the candidate's answer to the interview question.

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate exactly these three dimensions:

1. Relevance
Determine how directly the answer addresses the question.

2. STAR Structure
Determine whether the answer demonstrates:
- Situation
- Task
- Action
- Result

3. Completeness
Determine whether the answer sufficiently addresses the
question and provides enough supporting detail.

Return ONLY valid JSON:

{{
    "relevance": <number from 0 to 5>,
    "star_structure": <number from 0 to 5>,
    "completeness": <number from 0 to 5>,
    "feedback": "<concise explanation>"
}}

Do not include markdown.
Do not include text outside the JSON.
"""

        max_attempts = 3

        for attempt in range(max_attempts):

            try:

                # --------------------------------------------------
                # Groq API call
                # --------------------------------------------------

                response = (
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are an interview "
                                    "answer evaluation agent. "
                                    "Always return valid JSON."
                                ),
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],
                        temperature=0,
                    )
                )

                # --------------------------------------------------
                # Extract response
                # --------------------------------------------------

                response_text = (
                    response.choices[0]
                    .message
                    .content
                )

                if not response_text:
                    raise ValueError(
                        "Groq returned an empty response."
                    )

                response_text = response_text.strip()

                # --------------------------------------------------
                # Parse JSON
                # --------------------------------------------------

                try:

                    result = json.loads(
                        response_text
                    )

                except json.JSONDecodeError as exc:

                    raise ValueError(
                        "Scoring agent returned "
                        "invalid JSON.\n"
                        f"Response: {response_text}"
                    ) from exc

                # --------------------------------------------------
                # Validate result
                # --------------------------------------------------

                self._validate_result(result)

                return result

            except Exception as exc:

                # Retry temporary API failures.
                # We do not retry validation errors because
                # those indicate a bad model response.

                error_message = str(exc).lower()

                temporary_error = any(
                    keyword in error_message
                    for keyword in (
                        "timeout",
                        "rate limit",
                        "429",
                        "503",
                        "502",
                        "500",
                        "service unavailable",
                        "connection",
                    )
                )

                if not temporary_error:
                    raise

                if attempt == max_attempts - 1:
                    raise

                wait_time = 2 ** attempt

                print(
                    f"Groq temporary error. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

        raise RuntimeError(
            "Scoring request failed."
        )

    @staticmethod
    def _validate_result(result: dict):

        required_fields = {
            "relevance",
            "star_structure",
            "completeness",
            "feedback",
        }

        missing_fields = (
            required_fields - result.keys()
        )

        if missing_fields:

            raise ValueError(
                f"Missing scoring fields: "
                f"{missing_fields}"
            )

        for field in (
            "relevance",
            "star_structure",
            "completeness",
        ):

            value = result[field]

            if not isinstance(
                value,
                (int, float),
            ):

                raise ValueError(
                    f"{field} must be numeric."
                )

            if not 0 <= value <= 5:

                raise ValueError(
                    f"{field} must be between 0 and 5."
                )

        if not isinstance(
            result["feedback"],
            str,
        ):

            raise ValueError(
                "feedback must be a string."
            )