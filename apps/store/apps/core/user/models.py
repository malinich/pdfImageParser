import asyncio
from concurrent.futures import ThreadPoolExecutor

from core.settings import eng
from sqlalchemy import Column, Integer, String, BLOB
from sqlalchemy.ext.declarative import declarative_base
from tornado.concurrent import run_on_executor, return_future

EXECUTOR = ThreadPoolExecutor(max_workers=5)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    name = Column(String(50))
    email = Column(String(127), unique=True)
    password = Column(BLOB())


class AsyncOpUsers:
    def __init__(self, db_session, io_loop=None, executor=EXECUTOR):
        self.io_loop = io_loop or asyncio.get_event_loop()
        self.executor = executor
        self.db_session = db_session

    @run_on_executor
    @return_future
    def create(self, obj, callback=None):
        session = self.db_session()
        result = True
        try:
            session.add(obj)
            session.commit()
        except Exception as e:
            session.rollback()
            result = e
        callback(result)


Base.metadata.create_all(eng, checkfirst=True)
