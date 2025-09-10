
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes_health import router as health_router
from .api.routes_auth import router as auth_router
from .api.routes_items import router as items_router

app = FastAPI(title="myapp", version="0.1.0")
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(items_router)

@app.get("/", tags=["root"])
def root():
    return {"message": "myapp starter up!"}
