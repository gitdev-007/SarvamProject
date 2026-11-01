import os
from pathlib import Path

# Load environment from .env files
for candidate in [
    Path(".env"),
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]:
    if candidate.is_file():
        with open(candidate, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY", "")
SARVAM_CHAT_MODEL = os.environ.get("SARVAM_CHAT_MODEL", "sarvam-105b-conversations")

# Database URLs (Neon PostgreSQL)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./tenderguard.db")
MIGRATION_DATABASE_URL = os.environ.get(
    "MIGRATION_DATABASE_URL",
    os.environ.get("DATABASE_URL_UNPOOLED", DATABASE_URL),
)

# Normalize postgres:// to postgresql+psycopg:// if needed
def normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

# Neon Object Storage (S3 compatible)
AWS_ENDPOINT_URL_S3 = os.environ.get("AWS_ENDPOINT_URL_S3", "")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.environ.get("AWS_REGION", "aws-us-east-2")
NEON_STORAGE_BUCKET = os.environ.get("NEON_STORAGE_BUCKET", "tenderguard-documents")

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
