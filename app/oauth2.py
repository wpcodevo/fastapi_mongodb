import base64
from datetime import datetime, timedelta, timezone
import jwt
from bson.objectid import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .database import User, TokenBlacklist
from .config import settings

security = HTTPBearer()

PRIVATE_KEY = base64.b64decode(settings.JWT_PRIVATE_KEY).decode("utf-8")
PUBLIC_KEY = base64.b64decode(settings.JWT_PUBLIC_KEY).decode("utf-8")


def create_access_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    if TokenBlacklist.find_one({"token": token}):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revogado (logout realizado).",
        )

    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido.",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Faça login novamente.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )

    user = User.find_one({"_id": ObjectId(str(user_id))})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
        )

    user["id"] = str(user["_id"])
    return user