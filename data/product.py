from sqlalchemy import Column, Integer, String, PickleType
from .db_session import SqlAlchemyBase



class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    status = Column(Integer, nullable=True)
    image = Column(String, nullable=True)
    price = Column(Integer, nullable=True)