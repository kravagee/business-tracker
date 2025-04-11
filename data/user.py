from sqlalchemy import Column, Integer, String, PickleType
from .db_session import SqlAlchemyBase



class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=True)
    hashed_password = Column(Integer, nullable=True)
    api_key = Column(Integer, nullable=True)
    business_owned_list = Column(PickleType, nullable=True)
    business_managed_list = Column(PickleType, nullable=True)
