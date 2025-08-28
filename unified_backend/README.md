# Unified Chatbot Backend (FastAPI + Pydantic v2)

## Quickstart
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# edit .env, set OPENAI_API_KEY

# python version is 3.13 then if it is 
pip install --upgrade fastapi uvicorn pydantic pydantic-settings sqlalchemy openai python-multipart python-dotenv

uvicorn main:app --host 0.0.0.0 --port 8000 --reload


# drop the table of mood
python -m reset.reset_mood_db

```

## Endpoints (Onboarding RAG)
- `POST /onboarding/files/upload` (multipart) -> upload multiple files (txt/pdf/docx). Previous uploads are kept.
- `GET  /onboarding/files` -> list uploaded files
- `DELETE /onboarding/files/clear` -> delete all uploaded files and chunks
- `POST /onboarding/chat` -> body: { user_id, session_id, message } -> RAG answer with sources
- `GET  /onboarding/faqs/top?limit=20` -> most asked questions

## Endpoints (Mood Tracker)
- `POST /mood/chat` -> body: { user_id, session_id, message } (guided flow)
- `GET  /mood/logs` -> list logs (filters)
- `GET  /mood/analytics?group_by=day|month|year` -> counts for charting

SQLite is used for demo; you can replace with Postgres later without changing API.