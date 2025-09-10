# FastAPI Starter

## Quickstart
```bash
pip install softapi
softapi myapp --fastapi --jwt --db sqlite
cd myapp
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs
