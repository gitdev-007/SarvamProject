from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL, normalize_db_url

app_db_url = normalize_db_url(DATABASE_URL)

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,  # Health check before using a connection from pool
    "pool_recycle": 300,    # Recycle stale connections after 5 minutes
}

if "sqlite" in app_db_url:
    connect_args["check_same_thread"] = False
else:
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_timeout"] = 30

engine = create_engine(
    app_db_url,
    connect_args=connect_args,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
