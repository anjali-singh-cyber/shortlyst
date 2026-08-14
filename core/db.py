from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///fitcheck.db"
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    """
    Creates all tables if they don't exist yet. Safe to call every
    time the app starts — it won't wipe existing data or error out
    if tables are already there.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    FastAPI will call this per-request to hand each endpoint a fresh
    database session, then automatically close it when the request
    finishes — this pattern is called a 'dependency' in FastAPI.
    """
    with Session(engine) as session:
        yield session