import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

from data.db_session import SqlAlchemyBase


class StatsUsers(SqlAlchemyBase):
    __tablename__ = 'stats_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    business_count = Column(Integer, nullable=True)
    business_management_count = Column(Integer, nullable=True)
    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
