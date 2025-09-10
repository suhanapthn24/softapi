# QUICKSTART

Install (editable) and scaffold:
```bash
pip install -e .
softapi new myapp --fastapi --jwt --db sqlite
cd myapp
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs