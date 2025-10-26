from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///database/app.db"

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
