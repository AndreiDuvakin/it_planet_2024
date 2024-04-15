from .connect import base
from sqlalchemy import Column, Integer, VARCHAR, String
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class Account(base, UserMixin):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstName = Column(VARCHAR(100), nullable=False)
    lastName = Column(VARCHAR(100), nullable=False)
    email = Column(VARCHAR(100), nullable=False, unique=True)
    password = Column(String)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

    def set_password(self, password) -> None:
        self.password = generate_password_hash(password)
