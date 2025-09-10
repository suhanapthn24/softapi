
from pathlib import Path
from textwrap import dedent

def write_fastapi_basic(target_dir: Path, project_name: str = "softapi"):
    td = Path(target_dir)
    (td / "app" / "api").mkdir(parents=True, exist_ok=True)
    (td / "app" / "models").mkdir(parents=True, exist_ok=True)
    (td / "app" / "schemas").mkdir(parents=True, exist_ok=True)

    (td / "README.md").write_text(dedent(f"""
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
    """).strip())

    (td / "requirements.txt").write_text(dedent("""
    fastapi==0.115.0
    uvicorn==0.30.6
    pydantic==2.9.2
    pydantic-settings==2.5.2
    python-dotenv==1.0.1
    SQLAlchemy==2.0.34
    passlib[bcrypt]==1.7.4
    PyJWT==2.9.0
    httpx==0.27.2
    pytest==8.3.2
    """).strip())

    (td / ".env.example").write_text(
        'SECRET_KEY="dev-secret-change-me"\nDB_URL="sqlite:///./app.db"\nACCESS_TOKEN_EXPIRE_MINUTES=60\nCORS_ORIGINS="*"\n'
    )

    (td / "app" / "__init__.py").write_text("")
    (td / "app" / "config.py").write_text(dedent("""
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class Settings(BaseSettings):
        SECRET_KEY: str = "dev-secret-change-me"
        DB_URL: str = "sqlite:///./app.db"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
        CORS_ORIGINS: str = "*"
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    settings = Settings()
    """).strip())

    (td / "app" / "db.py").write_text(dedent("""
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
    """).strip())

    (td / "app" / "security.py").write_text(dedent("""
    from datetime import datetime, timedelta, timezone
    import jwt
    from .config import settings
    def create_access_token(sub: str, minutes: int | None = None) -> str:
        exp = datetime.now(tz=timezone.utc) + timedelta(minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode({"sub": sub, "exp": exp}, settings.SECRET_KEY, algorithm="HS256")
    def decode_token(token: str) -> dict:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    """).strip())

    (td / "app" / "models" / "__init__.py").write_text("")
    (td / "app" / "models" / "item.py").write_text(dedent("""
    from sqlalchemy import Integer, String
    from sqlalchemy.orm import Mapped, mapped_column
    from ..db import Base
    class Item(Base):
        __tablename__ = "items"
        id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
        name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
        description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    """).strip())

    (td / "app" / "schemas" / "__init__.py").write_text("")
    (td / "app" / "schemas" / "item.py").write_text(dedent("""
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
    """).strip())

    (td / "app" / "api" / "__init__.py").write_text("")
    (td / "app" / "api" / "routes_health.py").write_text(dedent("""
    from fastapi import APIRouter
    router = APIRouter(tags=["health"])
    @router.get("/health")
    def health():
        return {"status": "ok"}
    """).strip())

    (td / "app" / "api" / "routes_auth.py").write_text(dedent("""
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
    """).strip())

    (td / "app" / "api" / "routes_items.py").write_text(dedent("""
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
        db.add(obj); db.commit(); db.refresh(obj); return obj
    @router.get("", response_model=List[ItemOut])
    def list_items(db: Session = Depends(get_db), page: int = 1, per_page: int = 20):
        page = max(1, page); per_page = min(max(1, per_page), 100)
        return db.query(Item).order_by(Item.id.asc()).offset((page-1)*per_page).limit(per_page).all()
    @router.get("/{item_id}", response_model=ItemOut)
    def get_item(item_id: int, db: Session = Depends(get_db)):
        obj = db.get(Item, item_id)
        if not obj: raise HTTPException(404, "Item not found")
        return obj
    @router.delete("/{item_id}", status_code=204)
    def delete_item(item_id: int, db: Session = Depends(get_db)):
        obj = db.get(Item, item_id)
        if not obj: raise HTTPException(404, "Item not found")
        db.delete(obj); db.commit(); return
    """).strip())

    (td / "app" / "main.py").write_text(dedent("""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from .config import settings
    from .api.routes_health import router as health_router
    from .api.routes_auth import router as auth_router
    from .api.routes_items import router as items_router
    app = FastAPI(title="softapi", version="0.1.0")
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    app.include_router(health_router); app.include_router(auth_router); app.include_router(items_router)
    @app.get("/", tags=["root"])
    def root(): return {"message": "softapi starter up!"}
    """).strip())
