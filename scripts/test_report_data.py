from pathlib import Path
import json
import sys

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKEND_DIR = PROJECT_ROOT / "backend"

load_dotenv(
    BACKEND_DIR / ".env"
)

sys.path.insert(
    0,
    str(BACKEND_DIR)
)


from app.db.database import SessionLocal
from app.batch.report_data import ReportDataLoader


SESSION_ID = 2


def main():

    db = SessionLocal()

    try:

        loader = ReportDataLoader(db)

        data = loader.load_session_data(
            SESSION_ID
        )

        print(
            json.dumps(
                data,
                indent=2,
                default=str,
            )
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()