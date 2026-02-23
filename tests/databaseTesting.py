import pytest
from database.SQLTables import *
from database.muscleEnum import Muscles as m

@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

def test_create_tables():
    assert create_tables() is not None

def test_add_exercises():
    conn = add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    assert conn.execute(select(Exercise.name).where(Exercise.name == "Bench Press")).scalar() is not None

