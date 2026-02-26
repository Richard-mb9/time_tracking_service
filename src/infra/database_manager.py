from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import HOST_DB, PASSWORD_DB, USER_DB, PORT_DB, NAME_DB

URL_DB = f"postgresql://{USER_DB}:{PASSWORD_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"


_engine = create_engine(
    URL_DB,
    pool_size=30,
    max_overflow=10,
    pool_pre_ping=True,
    pool_timeout=30,
    pool_recycle=30,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_engine,
)


class DatabaseManagerConnection:
    def __init__(self):
        self.connect()

    def connect(self):
        self.session = SessionLocal()

    def close_session(self):
        self.session.close()

    def commit(self):
        self.session.commit()
