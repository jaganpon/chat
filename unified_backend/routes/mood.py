import uuid
from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal, Base, engine
from schemas import MoodChatIn, MoodChatOut, MoodLogOut, MoodAnalyticsOut
from services.mood_service import MoodFlowService
from models import MoodLog

Base.metadata.create_all(bind=engine)
router = APIRouter()
flow = MoodFlowService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat", response_model=MoodChatOut)
def chat(body: MoodChatIn, db: Session = Depends(get_db)):
    # Ensure user_id and session_id exist
    user_id = body.user_id or f"user_{uuid.uuid4().hex[:8]}"
    session_id = body.session_id or f"sess_{uuid.uuid4().hex[:8]}"

    reply, stage, mood, reason, extra = flow.handle(
        user_id, session_id, body.message
    )

    # Always log conversation step
    today = datetime.now().strftime("%Y-%m-%d")
    username = extra.get("username") if extra and extra.get("username") else "Anonymous"

    log = MoodLog(
        user_id=user_id,
        session_id=session_id,
        mood=mood if mood else "unknown",
        reason=reason if reason else body.message,
        date=today,
        username=username
    )
    db.add(log)
    db.commit()

    return {
        "reply": reply,
        "stage": stage,
        "user_id": user_id,
        "session_id": session_id,
        "username": extra.get("username") if extra else None
    }
@router.get("/logs", response_model=list[MoodLogOut])
def logs(user_id: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(MoodLog)
    if user_id:
        q = q.filter(MoodLog.user_id == user_id)
    if date_from:
        q = q.filter(MoodLog.date >= date_from)
    if date_to:
        q = q.filter(MoodLog.date <= date_to)
    rows = q.order_by(MoodLog.created_at.desc()).all()
    return rows

@router.get("/analytics", response_model=MoodAnalyticsOut)
def analytics(group_by: str = "day", user_id: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(MoodLog)
    if user_id:
        q = q.filter(MoodLog.user_id == user_id)
    if date_from:
        q = q.filter(MoodLog.date >= date_from)
    if date_to:
        q = q.filter(MoodLog.date <= date_to)
    rows = q.all()

    buckets = {}
    reasons = []
    top_moods = {}
    for r in rows:
        label = r.date
        if group_by == "month":
            label = r.date[:7]
        elif group_by == "year":
            label = r.date[:4]
        buckets[label] = buckets.get(label, 0) + 1
        if r.reason:
            reasons.append(r.reason)
        if r.mood:
            top_moods[r.mood] = top_moods.get(r.mood, 0) + 1

    return {"buckets": buckets, "reasons": reasons, "top_moods": top_moods}
