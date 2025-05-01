import datetime
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, nullable=True)
    # Здесь храним как JSON списки ID бизнесов, которыми владеет или управляет пользователь
    business_owner_list = Column(JSON, nullable=True)
    business_manager_list = Column(JSON, nullable=True)

    # Связи для бизнесов, где пользователь владелец
    owned_businesses = relationship('Business',
                                    primaryjoin="or_(User.id==Business.owner_id)",
                                    back_populates='owner')

    # Связи для бизнесов, где пользователь менеджер
    managed_businesses = relationship('Business',
                                      back_populates='manager')

    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
