# -*- coding: utf-8 -*-

"""
    models.py module is responsible for interacting with Database. Currently we
    have only one table Stats. All information we get from running client script
    on different machines is saved in the Stats table. Sqlalchemy ORM is used to 
    help us with DB initialization and queries.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Float, DateTime
import os, logging
from datetime import datetime
from config import DB_URI
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

Base = declarative_base()

class Stats(Base):

    __tablename__ = 'stats'

    ip              =   Column(String, primary_key=True)
    cpu_threshold   =   Column(Float, nullable=False)
    cpu_usage       =   Column(Float)
    mem_threshold   =   Column(Float, nullable=False)
    mem_usage       =   Column(Float)
    email           =   Column(String(128))
    created_at      =   Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        str_created_at = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return "<Stats (ip='%s', cpu_usage='%s', mem_usage=%s, created_at=%s)>" % (self.ip, self.cpu_usage, self.mem_usage, str_created_at)

def get_or_create(ip, cpu_threshold, mem_threshold, email, *args, **kwargs):
    stats = dal.session.query(Stats).filter(Stats.ip==ip).first()
    if not stats:
        stats = Stats()
    stats.ip=ip
    stats.cpu_threshold=cpu_threshold
    stats.mem_threshold=mem_threshold
    stats.email=email
    return stats

def update(ip, cpu_usage, mem_usage):
    stats = dal.session.query(Stats).filter(Stats.ip==ip).one()
    stats.cpu_usage = cpu_usage
    stats.mem_usage = mem_usage
    return stats

def save(model, msg):
    dal.session.add(model)
    try:
        dal.session.commit()
        logger.info("Stats record for ip: %s successfully added." % model.ip)
    except IntegrityError, exc:
        dal.session.rollback()
        logger.exception('error: %s' % exc.message) 

class DataAccessLayer(object):
    session = None
    engine = None
    db_path = os.path.join(os.path.dirname(__file__), DB_URI)
    conn_string = 'sqlite:///{}'.format(db_path)
    def __init__(self, conn_string=None):
        print conn_string
        self.engine = create_engine(conn_string or self.conn_string, echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

dal = DataAccessLayer()


