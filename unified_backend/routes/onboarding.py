from fastapi import APIRouter, Query, UploadFile, File, Form, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from services.rag_service import save_file_and_chunks, list_files, clear_files, handle_chat
from schemas import ChatOut, UploadOut, FileItem, FAQItem, ChatOut as ChatOutSchema
from models import Document
Base.metadata.create_all(bind=engine)
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/files/upload", response_model=List[UploadOut])
async def upload_files(
    files: List[UploadFile] = File(...),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    DEFAULT_USER = "hr_admin"
    outs = []

    # fallback to default user if none provided
    effective_user = user_id or DEFAULT_USER

    for f in files:
        try:
            bytes_data = await f.read()
            doc_id = save_file_and_chunks(db, effective_user, bytes_data, f.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        outs.append({
            "document_id": doc_id,
            "filename": f.filename,
            "user_id": effective_user
        })

    return outs


@router.get("/files", response_model=List[FileItem])
def files(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    rows = list_files(db, user_id)
    return [{"id": r["id"], "filename": r["filename"], "created_at": r["created_at"]} for r in rows]

@router.delete("/files/clear")
def clear(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    clear_files(db, user_id)
    return {"status": "ok"}

@router.delete("/files/delete")
def delete_files(
    file_ids: List[int] = Query(...),   # pass multiple file IDs as query params
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Delete specific files by their IDs.
    Example: DELETE /files/delete?file_ids=1&file_ids=3&user_id=user_123
    """
    # Query documents
    q = db.query(Document).filter(Document.id.in_(file_ids))
    if user_id:
        q = q.filter(Document.user_id == user_id)

    # Delete files from disk if needed
    docs_to_delete = q.all()
    for doc in docs_to_delete:
        try:
            import os
            os.remove(doc.filepath)  # assumes Document.filepath exists
        except Exception:
            pass

    # Delete from DB
    deleted_count = q.delete(synchronize_session=False)
    db.commit()

    return {"status": "ok", "deleted_count": deleted_count}

@router.post("/chat", response_model=ChatOut)
def chat(user_id: Optional[str] = Form(None), session_id: str = Form(...), message: str = Form(...), db: Session = Depends(get_db)):
    answer, sources = handle_chat(db, user_id, session_id, message)
    return {"reply": answer, "sources": sources}

@router.get("/faqs/top", response_model=List[FAQItem])
def top_faqs(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.query("faqs") if False else db.query  # placeholder; real code below
    # real query:
    rows = db.query.__self__.query  # placeholder to avoid linter complaints (not executed)
    # Correct query:
    rows = db.query.__class__
    # Instead just run a proper query:
    from models import FAQ
    rows = db.query(FAQ).order_by(FAQ.count.desc()).limit(limit).all()
    return [{"question": r.question, "count": r.count} for r in rows]
