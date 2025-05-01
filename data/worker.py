import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Worker(Base):
    __tablename__ = 'workers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=True)
    salary = Column(Float, nullable=True)
    position = Column(String, nullable=True)
    # Внешний ключ к бизнесу
    business_id = Column(Integer, ForeignKey('businesses.id'))

    business = relationship('Business', back_populates='workers')

    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
