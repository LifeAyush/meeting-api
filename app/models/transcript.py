from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime

from app.models.base import Base

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    speaker = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now())
    text = Column(Text, nullable=False)

    meeting = relationship("Meeting", back_populates="transcripts")
