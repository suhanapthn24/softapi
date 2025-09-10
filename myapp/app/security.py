from datetime import datetime, timedelta, timezone
import jwt
from .config import settings
def create_access_token(sub: str, minutes: int | None = None) -> str:
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": exp}, settings.SECRET_KEY, algorithm="HS256")
def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])