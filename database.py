import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_PATH = BASE_DIR / "sensors.db"


def load_env_file(env_path: Path) -> None:
    """Load simple KEY=VALUE pairs from .env without adding a new dependency."""
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def normalize_database_url(database_url: str) -> str:
    database_url = database_url.strip()

    if database_url.startswith("DATABASE_URL="):
        database_url = database_url.split("=", 1)[1].strip()

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


load_env_file(BASE_DIR / ".env")

SQLALCHEMY_DATABASE_URL = normalize_database_url(
    os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")
)

engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
except ModuleNotFoundError as exc:
    if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
        raise RuntimeError(
            "PostgreSQL driver not installed. Run 'venv/bin/pip install -r requirements.txt' "
            "inside this project and start the server again."
        ) from exc
    raise
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
