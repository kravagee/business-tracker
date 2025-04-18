from sqlalchemy import Column, Integer, String, PickleType
from .db_session import SqlAlchemyBase



class Business(SqlAlchemyBase):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    worker_list = Column(PickleType, nullable=True)
    manager_list = Column(PickleType, nullable=True)
    product_list = Column(PickleType, nullable=True)

