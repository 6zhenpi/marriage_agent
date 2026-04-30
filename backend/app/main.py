from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.chat import router as chat_router
from app.api.feedback import router as feedback_router

app = FastAPI(
    title="婚姻家庭法律咨询助手",
    description="婚姻家庭法律知识科普AI助手后端API",
    version="1.0.0",
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(feedback_router, prefix="/api", tags=["feedback"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "婚姻家庭法律咨询助手"}
