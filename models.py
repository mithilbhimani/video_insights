from sqlalchemy import Column, Integer, String, Text, Enum as SqlEnum
from database import Base, SubjectEnum, LevelEnum

class VideoInsight(Base):
    __tablename__ = "video_insight"

    id = Column(Integer, primary_key=True, index=True)
    transcription = Column(Text, nullable=False)
    video_file_saved = Column(String, nullable=False)
    transcription_file_saved = Column(String, nullable=False)
    subjects = Column(SqlEnum(SubjectEnum), nullable=False)
    levels = Column(SqlEnum(LevelEnum), nullable=False)
    tags = Column(Text, nullable=True)
