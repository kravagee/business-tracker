import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from data.db_session import SqlAlchemyBase


class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=True)
    image = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    # Внешний ключ к бизнесу
    business_id = Column(Integer, ForeignKey('businesses.id'))

    business = relationship('Business', back_populates='products')

    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
