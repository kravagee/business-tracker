import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StatsBusiness(Base):
    __tablename__ = 'stats_business'

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False)
    bought_products = Column(Integer, nullable=True)
    money_spent = Column(Float, nullable=True)
    worker_count = Column(Integer, nullable=True)
    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
