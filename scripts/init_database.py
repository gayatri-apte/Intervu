from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(
    0,
    str(BACKEND_DIR),
)

from app.db.database import init_db


def main():
    init_db()

    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)

    print("SQLite database initialized successfully.")
    print(
        "Location: "
        f"{PROJECT_ROOT / 'data' / 'interview.db'}"
    )


if __name__ == "__main__":
    main()