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