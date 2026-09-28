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
from app.batch.report import ReportGenerator


SESSION_ID = 2


def main():

    db = SessionLocal()

    try:

        print("=" * 60)
        print("GENERATING INTERVIEW REPORT")
        print("=" * 60)

        # ---------------------------------------------
        # Load data from SQLite
        # ---------------------------------------------

        loader = ReportDataLoader(db)

        report_data = loader.load_session_data(
            SESSION_ID
        )

        print(
            "Loaded transcript, scoring and prosody "
            "data from SQLite."
        )

        # ---------------------------------------------
        # Generate report with existing ReportGenerator
        # ---------------------------------------------

        generator = ReportGenerator()

        report = generator.generate_report(
            report_data
        )

        # ---------------------------------------------
        # Display report
        # ---------------------------------------------

        print()
        print("=" * 60)
        print("GENERATED REPORT")
        print("=" * 60)

        print(
            json.dumps(
                report,
                indent=2
            )
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()