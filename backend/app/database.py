import os
import sys
from pathlib import Path

def ensure_local_venv_site_packages() -> None:
    if ".venv" in sys.executable:
        return

    backend_dir = Path(__file__).resolve().parents[1]
    venv_lib_dir = backend_dir / ".venv" / "lib"
    if not venv_lib_dir.exists():
        return

    venv_site_packages_paths: list[str] = []
    for python_dir in sorted(venv_lib_dir.glob("python*")):
        site_packages = python_dir / "site-packages"
        if site_packages.exists():
            venv_site_packages_paths.append(str(site_packages))

    if not venv_site_packages_paths:
        return

    filtered_paths: list[str] = []
    for path in sys.path:
        if "site-packages" in path and not any(
            path.startswith(venv_path) for venv_path in venv_site_packages_paths
        ):
            continue
        filtered_paths.append(path)

    sys.path[:] = venv_site_packages_paths + [
        path for path in filtered_paths if path not in venv_site_packages_paths
    ]


ensure_local_venv_site_packages()

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Загружаем переменные из backend/.env независимо от директории запуска.
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Create backend/.env and add DATABASE_URL="
        "postgresql+psycopg://username:password@localhost:5432/db_name"
    )

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Создает SQLAlchemy-сессию для одного HTTP-запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
