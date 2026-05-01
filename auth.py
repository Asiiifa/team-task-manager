import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import bcrypt

from database import get_db
from models import User


SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
COOKIE_NAME = "access_token"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bcrypt_major_version = int(getattr(bcrypt, "__version__", "0").split(".", 1)[0])
_use_passlib_bcrypt = hasattr(bcrypt, "__about__") and _bcrypt_major_version < 5


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not _use_passlib_bcrypt:
        password_bytes = _bcrypt_password_bytes(plain_password)
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        password_bytes = _bcrypt_password_bytes(plain_password)
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    if not _use_passlib_bcrypt:
        password_bytes = _bcrypt_password_bytes(password)
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")
    try:
        return pwd_context.hash(password)
    except Exception:
        password_bytes = _bcrypt_password_bytes(password)
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def _bcrypt_password_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:72]


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    user = (
        db.query(User)
        .filter((User.username == username_or_email) | (User.email == username_or_email))
        .first()
    )
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise _redirect_to_login()
    payload = decode_token(token)
    user_id = payload.get("sub") if payload else None
    if not user_id:
        raise _redirect_to_login()
    user = db.get(User, int(user_id))
    if not user:
        raise _redirect_to_login()
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/dashboard"},
        )
    return current_user


def set_auth_cookie(response, token: str) -> None:
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def clear_auth_cookie(response) -> None:
    response.delete_cookie(COOKIE_NAME)


def _redirect_to_login() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_303_SEE_OTHER,
        headers={"Location": "/login"},
    )
