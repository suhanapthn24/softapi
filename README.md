# FastAPI Starter

## Quickstart (CLI)
```bash
pip install softapi
softapi myapp --fastapi --jwt --db sqlite   # or: --db postgres, add --alembic, --docker, --colab
cd myapp

python -m venv .venv
# Windows: .\.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

cp .env.example .env            # Windows (PowerShell): copy .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload   # or: uvicorn app.main:create_app --factory --reload
