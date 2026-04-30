from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

feedback_store: list[dict] = []


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: Optional[str] = None
    rating: str
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    message: str


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    feedback_store.append(
        {
            "session_id": request.session_id,
            "message_id": request.message_id,
            "rating": request.rating,
            "comment": request.comment,
        }
    )
    return FeedbackResponse(
        status="ok",
        message="感谢您的反馈！",
    )
