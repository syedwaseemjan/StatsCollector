"""
    models.py module is responsible for interacting with Database. Currently we
    have only one table Stats. All information we get from running
    client script on different machines is saved in the Stats table.
    Sqlalchemy ORM is used to help us with DB initialization and queries.
"""

import logging
import os
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app import settings

logger = logging.getLogger()

Base = declarative_base()


class Common(object):
    @classmethod
    def get_or_create(cls, ip, cpu_threshold, mem_threshold, email, *args, **kwargs):
        stats = dal.session.query(Stats).filter(Stats.ip == ip).first()
        if not stats:
            stats = Stats()
        stats.ip = ip
        stats.cpu_threshold = cpu_threshold
        stats.mem_threshold = mem_threshold
        stats.email = email
        return stats

    @classmethod
    def update(cls, ip, cpu_usage, mem_usage, uptime):
        stats = dal.session.query(Stats).filter(Stats.ip == ip).one()
        stats.cpu_usage = cpu_usage
        stats.mem_usage = mem_usage
        stats.uptime = uptime
        return stats

    @classmethod
    def save(cls, model):
        dal.session.add(model)
        try:
            dal.session.commit()
            logger.info(f"Stats record for ip: {model.ip} successfully added.")
        except IntegrityError as exe:
            dal.session.rollback()
            logger.exception(f"error: {exe}")


class Stats(Base, Common):

    __tablename__ = "stats"

    ip = Column(String, primary_key=True)
    cpu_threshold = Column(Float, nullable=False)
    cpu_usage = Column(Float)
    mem_threshold = Column(Float, nullable=False)
    mem_usage = Column(Float)
    uptime = Column(String(128))
    email = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        str_created_at = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return "<Stats (ip='%s', cpu_usage='%s', mem_usage=%s, created_at=%s)>" % (
            self.ip,
            self.cpu_usage,
            self.mem_usage,
            str_created_at,
        )


class DataAccessLayer(object):
    session = None
    engine = None
    db_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", settings.get("DB", "DB_URI"))
    )
    conn_string = "sqlite:///{}".format(db_path)

    def __init__(self, conn_string=None):
        logger.info(conn_string)
        self.engine = create_engine(
            conn_string or self.conn_string,
            echo=settings.get("DB", "SQLALCHEMY_ECHO", boolean=True),
        )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)


dal = DataAccessLayer()
