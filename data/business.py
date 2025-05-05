import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship

from data.db_session import SqlAlchemyBase


class Business(SqlAlchemyBase):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    owner = relationship('User', back_populates='owned_businesses', foreign_keys=[owner_id])

    # Связь с работниками
    workers = relationship('Worker', back_populates='business')
    # Связь с продуктами
    products = relationship('Product', back_populates='business')

    # Можно оставить как JSON список ID, если нужно
    worker_list = Column(JSON, nullable=True)
    product_list = Column(JSON, nullable=True)
    manager_list = Column(JSON, nullable=True)

    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
