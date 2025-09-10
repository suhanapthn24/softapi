from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/__version__")
def version():
    # This is a trivial endpoint; users can override or extend
    return {"package": "softapi", "version": "0.2.2"}
