import datetime

from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, DateTime, TEXT
from sqlalchemy.orm import relationship

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, nullable=True)

    # Связи с бизнесами
    owned_businesses = relationship('Business', back_populates='owner', foreign_keys='Business.owner_id')

    # Поля для хранения списков (можно использовать вместо связей или вместе с ними)
    business_owner_list = Column(TEXT, nullable=True)
    business_manager_list = Column(TEXT, nullable=True)

    # Связь с работником (если пользователь является работником)

    modified_date = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
