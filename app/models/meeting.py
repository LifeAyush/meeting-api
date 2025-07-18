from sqlalchemy.sql import func
from sqlalchemy import Column, String, DateTime

from app.models.base import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
