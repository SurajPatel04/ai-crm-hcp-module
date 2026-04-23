import jwt
from fastapi import HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.database import get_db
from app.models.users import User


def verify_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("userId")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: userId missing from payload")

        return int(user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired, please refresh or sign in again")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or malformed access token")


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token not found. Please sign in first."
        )

    user_id = verify_access_token(token)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User associated with this token no longer exists")

    return user