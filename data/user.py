import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, nullable=True)

    # Связи с бизнесами, где пользователь владелец
    owned_businesses = relationship('Business', back_populates='owner', foreign_keys='Business.owner_id')
    # Связи с бизнесами, где пользователь менеджер
    managed_businesses = relationship('Business', back_populates='manager', foreign_keys='Business.manager_id')

    # Эти поля-последствия, также можно оставить как JSON, или убрать их, если реализуешь связи
    business_owner_list = Column(JSON, nullable=True)
    business_manager_list = Column(JSON, nullable=True)

    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
