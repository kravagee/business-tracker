import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Business(Base):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Внешние ключи для связей
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Владелец бизнеса
    # Массив ID работников и менеджеров можно оставить как JSON или реализовать связи отдельно

    owner = relationship('User', back_populates='owned_businesses')

    # Связь с менеджерами (модель User)
    managers = relationship('User',
                            secondary='business_managers',
                            back_populates='managed_businesses')

    # Связь с работниками
    workers = relationship('Worker', back_populates='business')

    # Связь с продуктами
    products = relationship('Product', back_populates='business')

    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
