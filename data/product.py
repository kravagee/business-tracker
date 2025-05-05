import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from db_session import SqlAlchemyBase

class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=True)
    image = Column(String, nullable=True)
    price = Column(Float, nullable=True)

    business_id = Column(Integer, ForeignKey('businesses.id'))
    business = relationship('Business', back_populates='products')

    modified_date = Column(datetime.datetime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
