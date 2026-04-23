import jwt
from datetime import datetime, timedelta
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.core.config import settings
from app.models import RefreshToken
from app.utils.hash import hash_token


def generate_access_token(user) -> str:
    secret = settings.secret_key
    expires_in_minutes = settings.access_token_expire_time

    if not secret:
        raise Exception("Access token secret is not defined in environment variables.")

    expire = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

    payload = {
        "userId": user.id,
        "email": user.email,
        "role": user.role,
        "exp": expire,
    }

    return jwt.encode(payload, secret, algorithm=settings.algorithm)


def generate_refresh_token(user) -> str:
    secret = settings.refresh_token_secret_key
    expires_in_minutes = settings.refresh_token_expire_time

    if not secret:
        raise Exception("Refresh token secret is not defined in environment variables.")

    expire = datetime.utcnow() + timedelta(minutes=expires_in_minutes)

    payload = {
        "id": user.id,
        "exp": expire,
    }

    return jwt.encode(payload, secret, algorithm=settings.algorithm)


async def generate_refresh_token_and_store(user, req: Request, db: AsyncSession) -> str:
    refresh_token = generate_refresh_token(user)

    expires_at = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_time)
    device_info = req.headers.get("user-agent", None)
    ip_address = req.client.host if req.client else None
    hashed_token = hash_token(refresh_token)

    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user.id,
            RefreshToken.device_info == device_info
        )
        .values(is_revoked=True)
    )

    new_token_record = RefreshToken(
        token=hashed_token,
        user_id=user.id,
        expires_at=expires_at,
        device_info=device_info,
        ip_address=ip_address
    )
    db.add(new_token_record)
    await db.commit()

    return refresh_token


async def generate_auth_tokens(user, req: Request, db: AsyncSession) -> dict:
    access_token = generate_access_token(user)
    refresh_token = await generate_refresh_token_and_store(user, req, db)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
    }
