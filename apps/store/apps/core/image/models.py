import asyncio
import datetime
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import Column, Integer, String, TEXT, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, subqueryload, joinedload
from tornado.concurrent import run_on_executor, return_future

from core.settings import eng
from core.user.models import User

Base = declarative_base()
EXECUTOR = ThreadPoolExecutor(max_workers=5)


class Pdfs(Base):
    __tablename__ = 'pdfs'
    id = Column(Integer, primary_key=True)
    name = Column(String(127))
    path = Column(String())
    created = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(ForeignKey(User.id))
    user = relationship(User)
    images = relationship("PdfImages")


class PdfImages(Base):
    __tablename__ = "pdf_images"
    id = Column(Integer, primary_key=True)
    pdf_id = Column(Integer, ForeignKey("pdfs.id"))
    pdf = relationship(Pdfs)
    image = Column(String())


class AsyncOpPdfImage:
    def __init__(self, db_session, io_loop=None, executor=EXECUTOR):
        self.io_loop = io_loop or asyncio.get_event_loop()
        self.executor = executor
        self.db_session = db_session

    @run_on_executor
    @return_future
    def get_all(self, callback=None):
        session = self.db_session()
        try:
            # result = session.query(Pdfs).all()
            # result = session.query(Pdfs)\
            #     .options(subqueryload(Pdfs.user))\
            #     .options(subqueryload(Pdfs.images)).all()
            result = session.query(PdfImages)\
                .options(joinedload(PdfImages.pdf))\
                .options(subqueryload(PdfImages.pdf).subqueryload(Pdfs.user)).all()
        except Exception as e:
            result = e
        callback(result)

    @run_on_executor
    @return_future
    def get_by_id(self, id: int, callback=None):
        session = self.db_session()
        try:
            result = session.query(Pdfs).filter(Pdfs.id == id).one()
        except Exception as e:
            result = e
        callback(result)

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
