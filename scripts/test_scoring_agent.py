from pathlib import Path
import sys

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKEND_DIR = PROJECT_ROOT / "backend"
ENV_PATH = BACKEND_DIR / ".env"

load_dotenv(ENV_PATH)

sys.path.insert(
    0,
    str(BACKEND_DIR),
)


from app.scoring.scoring_agent import (
    InterviewScoringAgent,
)


def main():

    question = (
        "Can you walk me through a time "
        "you faced a difficult technical challenge?"
    )

    answer = (
        "At my last job, we had a production incident "
        "where our message queue was backing up under load. "
        "I led the investigation and found a bottleneck "
        "in our consumer logic. I redesigned it to process "
        "messages in parallel batches, which reduced our "
        "backlog recovery time from two hours to about "
        "15 minutes."
    )

    agent = InterviewScoringAgent()

    result = agent.score(
        question=question,
        answer=answer,
    )

    print("=" * 60)
    print("INTERVIEW SCORING")
    print("=" * 60)

    print(
        f"Relevance: "
        f"{result['relevance']}/5"
    )

    print(
        f"STAR Structure: "
        f"{result['star_structure']}/5"
    )

    print(
        f"Completeness: "
        f"{result['completeness']}/5"
    )

    print()
    print("Feedback:")
    print(result["feedback"])


if __name__ == "__main__":
    main()