from pathlib import Path
from textwrap import dedent


def write_fastapi_basic(
    target_dir: Path,
    project_name: str = "softapi",
    include_jwt: bool = True,
    db: str = "sqlite",            # "sqlite" | "postgres"
    include_docker: bool = False,  # add Dockerfile + docker-compose.yml
    include_alembic: bool = False, # add Alembic boilerplate
    include_colab: bool = False,   # add Colab runner using pyngrok
):
    """
    Scaffolds a FastAPI project with options that are compatible across Python 3.8+.
    - No 3.10+'|' unions in generated code (uses typing.Optional instead).
    - Requirements pinned conservatively to work with older pip/Windows wheels.
    - Optional extras: Docker, Alembic, Colab ngrok runner.
    """
    td = Path(target_dir)
    (td / "app" / "api").mkdir(parents=True, exist_ok=True)
    (td / "app" / "models").mkdir(parents=True, exist_ok=True)
    (td / "app" / "schemas").mkdir(parents=True, exist_ok=True)

    # --- README -----------------------------------------------------------------
    (td / "README.md").write_text(
        dedent(
            f"""
            # {project_name} • FastAPI Starter

            ## Quickstart
            ```bash
            python -m venv .venv
            # Windows: .\\.venv\\Scripts\\activate
            # macOS/Linux: source .venv/bin/activate
            pip install -r requirements.txt
            uvicorn app.main:app --reload
            ```
            Open http://127.0.0.1:8000/docs
            """
        ).strip()
        + "\n"
    )

    # --- Requirements -----------------------------------------------------------
    # Pins chosen for wide Python (3.8+) and pip compatibility (Windows wheels exist).
    req = [
        "fastapi==0.115.0",
        "uvicorn==0.30.6",
        "pydantic==2.9.2",
        "pydantic-settings==2.5.2",
        "python-dotenv==1.0.1",
        "SQLAlchemy==2.0.34",
        "httpx==0.27.2",
        "pytest==8.3.2",
        "python-multipart==0.0.6",  # form/file upload support
    ]
    if include_jwt:
        req += [
            "passlib[bcrypt]==1.7.4",
            "PyJWT==2.9.0",
            # bcrypt wheel exists on Windows/macOS/Linux for 3.8+
        ]
    if db == "postgres":
        req += ["psycopg2-binary==2.9.9"]
    if include_docker:
        # Dockerfile uses gunicorn + uvicorn worker
        req += ["gunicorn==22.0.0"]
    if include_alembic:
        req += ["alembic==1.13.2"]
    if include_colab:
        # ngrok + uvicorn in colab; nest_asyncio for event loop reuse
        req += ["pyngrok==7.2.3", "nest_asyncio==1.6.0"]

    (td / "requirements.txt").write_text("\n".join(req) + "\n")

    # --- .env.example -----------------------------------------------------------
    db_url = (
        "sqlite:///./app.db"
        if db == "sqlite"
        else "postgresql+psycopg2://user:pass@localhost:5432/mydb"
    )
    (td / ".env.example").write_text(
        'SECRET_KEY="dev-secret-change-me"\n'
        f'DB_URL="{db_url}"\n'
        "ACCESS_TOKEN_EXPIRE_MINUTES=60\n"
        'CORS_ORIGINS="*"\n'
    )

    # --- .gitignore (helpful cross-platform) -----------------------------------
    (td / ".gitignore").write_text(
        dedent(
            """
            __pycache__/
            *.pyc
            .venv/
            .env
            dist/
            build/
            *.egg-info/
            .idea/
            .vscode/
            app.db
            data/
            """
        ).strip()
        + "\n"
    )

    # --- Base files -------------------------------------------------------------
    (td / "app" / "__init__.py").write_text("")
    (td / "app" / "config.py").write_text(
        dedent(
            """
            from pydantic_settings import BaseSettings, SettingsConfigDict

            class Settings(BaseSettings):
                SECRET_KEY: str = "dev-secret-change-me"
                DB_URL: str = "sqlite:///./app.db"
                ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
                CORS_ORIGINS: str = "*"

                model_config = SettingsConfigDict(env_file=".env", extra="ignore")

            settings = Settings()
            """
        ).strip()
        + "\n"
    )

    (td / "app" / "db.py").write_text(
        dedent(
            """
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker, declarative_base
            from .config import settings

            connect_args = {"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {}
            engine = create_engine(settings.DB_URL, connect_args=connect_args, future=True)
            SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
            Base = declarative_base()

            def get_db():
                db = SessionLocal()
                try:
                    yield db
                finally:
                    db.close()
            """
        ).strip()
        + "\n"
    )

    # --- Security/auth (3.8+ friendly type hints) ------------------------------
    if include_jwt:
        (td / "app" / "security.py").write_text(
            dedent(
                """
                from typing import Optional
                from datetime import datetime, timedelta, timezone
                import jwt
                from .config import settings

                def create_access_token(sub: str, minutes: Optional[int] = None) -> str:
                    exp = datetime.now(tz=timezone.utc) + timedelta(
                        minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                    return jwt.encode({"sub": sub, "exp": exp}, settings.SECRET_KEY, algorithm="HS256")

                def decode_token(token: str) -> dict:
                    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                """
            ).strip()
            + "\n"
        )

    # --- Model + Schema ---------------------------------------------------------
    (td / "app" / "models" / "__init__.py").write_text("")
    (td / "app" / "models" / "item.py").write_text(
        dedent(
            """
            from sqlalchemy import Integer, String
            from sqlalchemy.orm import Mapped, mapped_column
            from ..db import Base

            class Item(Base):
                __tablename__ = "items"
                id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
                name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
                description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
            """
        ).strip()
        + "\n"
    )

    (td / "app" / "schemas" / "__init__.py").write_text("")
    (td / "app" / "schemas" / "item.py").write_text(
        dedent(
            """
            from pydantic import BaseModel, Field

            class ItemCreate(BaseModel):
                name: str = Field(min_length=1, max_length=120)
                description: str = Field(default="", max_length=500)

            class ItemOut(BaseModel):
                id: int
                name: str
                description: str

                class Config:
                    from_attributes = True
            """
        ).strip()
        + "\n"
    )

    # --- Routers ---------------------------------------------------------------
    (td / "app" / "api" / "__init__.py").write_text("")
    (td / "app" / "api" / "routes_health.py").write_text(
        dedent(
            """
            from fastapi import APIRouter

            router = APIRouter(tags=["health"])

            @router.get("/health")
            def health():
                return {"status": "ok"}
            """
        ).strip()
        + "\n"
    )

    if include_jwt:
        (td / "app" / "api" / "routes_auth.py").write_text(
            dedent(
                """
                from fastapi import APIRouter, Depends, HTTPException
                from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
                from pydantic import BaseModel
                from ..security import create_access_token, decode_token

                router = APIRouter(prefix="/auth", tags=["auth"])
                oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

                class TokenOut(BaseModel):
                    access_token: str
                    token_type: str = "bearer"

                @router.post("/login", response_model=TokenOut)
                def login(form: OAuth2PasswordRequestForm = Depends()):
                    return {"access_token": create_access_token(form.username), "token_type": "bearer"}

                @router.get("/me")
                def me(token: str = Depends(oauth2)):
                    try:
                        payload = decode_token(token)
                    except Exception:
                        raise HTTPException(401, "Invalid token")
                    return {"user": payload.get("sub")}
                """
            ).strip()
            + "\n"
        )

    (td / "app" / "api" / "routes_items.py").write_text(
        dedent(
            """
            from typing import List
            from fastapi import APIRouter, Depends, HTTPException
            from sqlalchemy.orm import Session
            from ..db import get_db, Base, engine
            from ..models.item import Item
            from ..schemas.item import ItemCreate, ItemOut

            router = APIRouter(prefix="/items", tags=["items"])
            Base.metadata.create_all(bind=engine)

            @router.post("", response_model=ItemOut)
            def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
                obj = Item(name=payload.name, description=payload.description)
                db.add(obj)
                db.commit()
                db.refresh(obj)
                return obj

            @router.get("", response_model=List[ItemOut])
            def list_items(db: Session = Depends(get_db), page: int = 1, per_page: int = 20):
                page = max(1, page)
                per_page = min(max(1, per_page), 100)
                return (
                    db.query(Item)
                    .order_by(Item.id.asc())
                    .offset((page - 1) * per_page)
                    .limit(per_page)
                    .all()
                )

            @router.get("/{item_id}", response_model=ItemOut)
            def get_item(item_id: int, db: Session = Depends(get_db)):
                obj = db.get(Item, item_id)
                if not obj:
                    raise HTTPException(404, "Item not found")
                return obj

            @router.delete("/{item_id}", status_code=204)
            def delete_item(item_id: int, db: Session = Depends(get_db)):
                obj = db.get(Item, item_id)
                if not obj:
                    raise HTTPException(404, "Item not found")
                db.delete(obj)
                db.commit()
                return
            """
        ).strip()
        + "\n"
    )

    # --- Docker artifacts -------------------------------------------------------
    if include_docker:
        (td / "Dockerfile").write_text(
            dedent(
                """
                FROM python:3.12-slim
                WORKDIR /app
                RUN apt-get update && apt-get install -y --no-install-recommends \
                    build-essential curl wget && rm -rf /var/lib/apt/lists/*
                COPY requirements.txt /app/requirements.txt
                RUN pip install --no-cache-dir -r /app/requirements.txt
                COPY app /app/app
                COPY .env /app/.env
                EXPOSE 8000
                CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker","-w","2","-b","0.0.0.0:8000","app.main:app"]
                """
            ).strip()
            + "\n"
        )
        (td / "docker-compose.yml").write_text(
            dedent(
                """
                version: "3.9"
                services:
                  softapi:
                    build: .
                    restart: unless-stopped
                    ports: ["8000:8000"]
                    env_file: [.env]
                    volumes: ["./data:/app/data"]
                    healthcheck:
                      test: ["CMD","wget","-qO-","http://localhost:8000/health"]
                      interval: 30s
                      timeout: 5s
                      retries: 3
                """
            ).strip()
            + "\n"
        )

    # --- Alembic boilerplate ----------------------------------------------------
    if include_alembic:
        (td / "alembic.ini").write_text(
            dedent(
                f"""
                [alembic]
                script_location = alembic
                sqlalchemy.url = {db_url}
                """
            ).strip()
            + "\n"
        )
        (td / "alembic").mkdir(exist_ok=True)
        (td / "alembic" / "env.py").write_text(
            dedent(
                """
                from alembic import context
                from app.db import engine, Base

                config = context.config
                target_metadata = Base.metadata

                def run_migrations_offline():
                    context.configure(url=str(engine.url), target_metadata=target_metadata, literal_binds=True)
                    with context.begin_transaction():
                        context.run_migrations()

                def run_migrations_online():
                    connectable = engine
                    with connectable.connect() as connection:
                        context.configure(connection=connection, target_metadata=target_metadata)
                        with context.begin_transaction():
                            context.run_migrations()

                if context.is_offline_mode():
                    run_migrations_offline()
                else:
                    run_migrations_online()
                """
            ).strip()
            + "\n"
        )
        (td / "alembic" / "README").write_text("Alembic migrations.\n")

    # --- Colab runner (pyngrok) -------------------------------------------------
    if include_colab:
        (td / "colab_run.py").write_text(
            dedent(
                """
                """
            ).strip()
            + "\n"
        )
        # Write actual content line-by-line to avoid any indent funk
        colab_lines = []
        colab_lines.append("import os")
        colab_lines.append("import nest_asyncio")
        colab_lines.append("nest_asyncio.apply()")
        colab_lines.append("from pyngrok import ngrok")
        colab_lines.append("")
        colab_lines.append("# Optional: set NGROK_AUTHTOKEN in environment for higher limits")
        colab_lines.append('token = os.environ.get("NGROK_AUTHTOKEN")')
        colab_lines.append("if token:")
        colab_lines.append("    ngrok.set_auth_token(token)")
        colab_lines.append("")
        colab_lines.append('public_url = ngrok.connect(addr=8000, proto="http").public_url')
        colab_lines.append('print("Public URL:", public_url)')
        colab_lines.append("")
        colab_lines.append("import uvicorn")
        colab_lines.append('uvicorn.run("app.main:app", host="0.0.0.0", port=8000)')
        (td / "colab_run.py").write_text("\n".join(colab_lines) + "\n")

        # Append Colab usage to README
        readme = (td / "README.md").read_text()
        readme += dedent(
            """
            ## Run on Google Colab (with public URL)
            ```python
            # In a Colab cell:
            !pip install -r requirements.txt
            import os
            os.environ['NGROK_AUTHTOKEN'] = 'YOUR_TOKEN'  # optional
            !python colab_run.py
            # Look for "Public URL: https://..." then open it in a new tab
            ```
            """
        )
        (td / "README.md").write_text(readme)

    # --- main.py: built line-by-line to avoid indentation issues ----------------
    includes = ["from .api.routes_health import router as health_router"]
    if include_jwt:
        includes.append("from .api.routes_auth import router as auth_router")
    includes.append("from .api.routes_items import router as items_router")

    routers = ["app.include_router(health_router)"]
    if include_jwt:
        routers.append("app.include_router(auth_router)")
    routers.append("app.include_router(items_router)")

    lines = []
    lines.append("from fastapi import FastAPI")
    lines.append("from fastapi.middleware.cors import CORSMiddleware")
    lines.append("")
    lines.append("from .config import settings")
    lines.extend(includes)
    lines.append("")
    lines.append('app = FastAPI(title="' + project_name + '", version="0.1.0")')
    lines.append("")
    lines.append('origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]')
    lines.append("app.add_middleware(")
    lines.append("    CORSMiddleware,")
    lines.append('    allow_origins=origins or ["*"],')
    lines.append("    allow_credentials=True,")
    lines.append('    allow_methods=["*"],')
    lines.append('    allow_headers=["*"],')
    lines.append(")")
    lines.append("")
    lines.extend(routers)
    lines.append("")
    lines.append('@app.get("/", tags=["root"])')
    lines.append("def root():")
    lines.append('    return {"message": "' + project_name + ' starter up!"}')
    lines.append("")

    (td / "app" / "main.py").write_text("\n".join(lines))
