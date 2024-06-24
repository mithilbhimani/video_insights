# database.py
from sqlalchemy import create_engine, Column, String, Text, Enum as SqlEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

DATABASE_URL = "postgresql://username:password@localhost:5432/dbname"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SubjectEnum(enum.Enum):
    math = "math"
    science = "science"
    history = "history"
    art = "art"
    music = "music"

class LevelEnum(enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
