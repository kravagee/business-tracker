import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, Table
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase

# Промежуточная таблица для связи многие-ко-многим между Business и User (менеджерами)
business_manager_association = Table(
    'business_manager_association',
    SqlAlchemyBase.metadata,
    Column('business_id', Integer, ForeignKey('businesses.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class Business(SqlAlchemyBase):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    owner = relationship('User', back_populates='owned_businesses')

    # Связь с менеджерами через промежуточную таблицу
    managers = relationship(
        'User',
        secondary=business_manager_association,
        back_populates='managed_businesses'
    )

    # Связь с работниками
    workers = relationship('Worker', back_populates='business')
    # Связь с продуктами
    products = relationship('Product', back_populates='business')

    # Можно оставить как JSON список ID, если нужно
    worker_list = Column(JSON, nullable=True)
    product_list = Column(JSON, nullable=True)

    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)