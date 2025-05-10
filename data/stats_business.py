import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class StatsBusiness(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'stats_business'

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(Integer, ForeignKey('businesses.id'))
    bought_products = Column(Integer, nullable=True)
    money_spent = Column(Float, nullable=True)
    worker_count = Column(Integer, nullable=True)

    business = relationship('Business')

    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
