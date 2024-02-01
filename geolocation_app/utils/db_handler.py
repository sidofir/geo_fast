from datetime import datetime

from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class GeolocationRequestModel(Base):
    __tablename__ = "geolocation_requests"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    domain = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    locations = Column(String, nullable=True)
    servers = Column(String, nullable=True)
    status = Column(String, default="Pending")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)
