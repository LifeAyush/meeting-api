from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ActionItem(BaseModel):
    owner: str = ""
    task: str
    due_hint: str | None = None


class SummaryCreate(BaseModel):
    meeting_id: str
    summary_text: str
    action_items: list[ActionItem] = Field(default_factory=list)


class SummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: str
    summary_text: str
    action_items: list[ActionItem] = Field(default_factory=list)
    created_at: datetime
