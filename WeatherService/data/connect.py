from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

__factory = None
base = declarative_base()


def init_db() -> None:
    global __factory
    from . import __all_models

    eng = create_engine('sqlite:///db/data.db')
    __factory = sessionmaker(bind=eng)
    print(__factory)
    base.metadata.create_all(eng)


def connect() -> Session:
    global __factory
    return __factory()
