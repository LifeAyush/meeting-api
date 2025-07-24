from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer

from app.models.base import Base

class MeetingSummary(Base):
    __tablename__ = "meeting_summaries"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    summary_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

    meeting = relationship("Meeting", back_populates="summary")
