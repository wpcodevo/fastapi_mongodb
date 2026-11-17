from datetime import datetime, timezone
import bcrypt
import jwt
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pymongo.errors import DuplicateKeyError

from app.database import User, TokenBlacklist
from app import schemas
from app.oauth2 import create_access_token, get_current_user, security, PUBLIC_KEY
from app.config import settings

router = APIRouter()
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponseSchema)
def create_user(payload: schemas.CreateUserSchema):
    hashed_password = bcrypt.hashpw(
        payload.password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    now = datetime.now(timezone.utc)
    user_doc = {
        "name": payload.name,
        "email": payload.email.lower(),
        "password": hashed_password,
        "role": "user",
        "created_at": now,
        "updated_at": now,
    }

    try:
        result = User.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conta já registrada com este e-mail.",
        )

    user_doc["id"] = str(result.inserted_id)
    return user_doc


@router.post("/login")
def login(payload: schemas.LoginUserSchema):
    db_user = User.find_one({"email": payload.email.lower()})

    if not db_user or not bcrypt.checkpw(
        payload.password.encode("utf-8"), db_user["password"].encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos.",
        )

    access_token = create_access_token(
        user_id=str(db_user["_id"]),
        email=db_user["email"],
    )

    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": ACCESS_TOKEN_EXPIRES_IN,
    }


@router.get("/verify", response_model=schemas.UserResponseSchema)
def verify_token(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )
        exp_timestamp = payload.get("exp")
        expires_at = (
            datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if exp_timestamp
            else datetime.now(timezone.utc)
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )

    TokenBlacklist.update_one(
        {"token": token},
        {"$set": {"token": token, "expires_at": expires_at}},
        upsert=True,
    )

    return {"status": "success", "message": "Logout realizado. Token revogado."}