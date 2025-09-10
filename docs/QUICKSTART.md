# QUICKSTART

## 1) Install the CLI (local dev)
```bash
pip install -e .
softapi --help
```

## 2) Generate a project
```bash
softapi new myapp
cd myapp
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs

## 3) Endpoints in the starter
- `GET /health`
- `POST /auth/login` (demo JWT) → returns token
- `GET /auth/me` (Authorization: Bearer <token>)
- `POST /items`, `GET /items`, `GET /items/{id}`, `DELETE /items/{id}`

## 4) Switch DB to Postgres
Set in `.env`:
```
DB_URL="postgresql+psycopg2://user:pass@localhost:5432/mydb"
```
Install `psycopg2-binary` and reboot:
```bash
pip install psycopg2-binary
uvicorn app.main:app --reload
```