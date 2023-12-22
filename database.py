# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

DATABASE_URL = config("DATABASE_URL")

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class to handle database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base class for declarative models
Base = declarative_base()
