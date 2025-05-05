import datetime
from sqlalchemy import Column, Integer, ForeignKey
from db_session import SqlAlchemyBase

class StatsUsers(SqlAlchemyBase):
    __tablename__ = 'stats_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    business_count = Column(Integer, nullable=True)
    business_management_count = Column(Integer, nullable=True)

    user = relationship('User')

    modified_date = Column(datetime.datetime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
