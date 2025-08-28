from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True, nullable=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    filehash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    user_id = Column(String, index=True, nullable=True)
    text = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # JSON-encoded list
    ord = Column(Integer, default=0)

    document = relationship("Document", back_populates="chunks")

class FAQ(Base):
    __tablename__ = "faqs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, index=True, nullable=True)
    question = Column(Text, nullable=False, unique=True)
    count = Column(Integer, default=1)
    last_asked_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MoodLog(Base):
    __tablename__ = "mood_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, index=True)
    mood = Column(String, index=True)
    reason = Column(String, nullable=True)
    username = Column(String, default="Anonymous")
    date = Column(String, index=True)  # yyyy-mm-dd
    created_at = Column(DateTime, default=func.now())