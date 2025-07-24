from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    summary_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

    meeting = relationship("Meeting", back_populates="summary")
