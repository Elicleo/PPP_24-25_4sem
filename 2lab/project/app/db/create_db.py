# sqlite:///app/db/example.db

# import sys
# from os.path import dirname, abspath
# sys.path.insert(0, dirname(dirname(abspath(__file__))))
# from app.models.models import User
# target_metadata = User.metadata

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite:///test.db')
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)


Base.metadata.create_all(engine)
