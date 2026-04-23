from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backendapi.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def create_session():
    with Session(engine) as session:
        yield session
