from app.utils.hash import hash_token
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from app.core.database import get_db
from app.models.users import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import UserCreate, UserLogin
from app.utils.hash import get_password_hash, verify_password
from app.services.auth_service import generate_auth_tokens
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    email = user_data.email.lower()

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        new_user = User(
            full_name=user_data.full_name,
            email=email,
            hashed_password=get_password_hash(user_data.password)
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return {
            "success": True,
            "message": "Account Created Successfully!"
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )

@router.post("/signin")
async def signin(
    user_data: UserLogin, 
    request: Request, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    try:
        email = user_data.email.lower()

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        tokens = await generate_auth_tokens(user, request, db)

        # 🍪 Set cookies
        response.set_cookie(
            key="access_token",
            value=tokens["accessToken"],
            httponly=True,
            secure=True,
            samesite="Strict"
        )

        response.set_cookie(
            key="refresh_token",
            value=tokens["refreshToken"],
            httponly=True,
            secure=True,
            samesite="Strict"
        )

        return {
            "success": True,
            "message": "Login successful"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong"
        )

@router.post("/refresh")
async def refresh_token(
    request: Request, 
    response: Response, 
    db: AsyncSession = Depends(get_db)
):
    try:
        token = request.cookies.get("refresh_token")

        if not token:
            raise HTTPException(status_code=401, detail="No refresh token provided")

        hashed_token = hash_token(token)

        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == hashed_token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
        existing_token = result.scalar_one_or_none()

        result_revoked = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == hashed_token,
                RefreshToken.is_revoked == True
            )
        )
        revoked_token = result_revoked.scalar_one_or_none()

        if revoked_token:
            await db.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == revoked_token.user_id)
                .values(is_revoked=True)
            )
            await db.commit()

            raise HTTPException(
                status_code=401,
                detail="Token reuse detected — all sessions revoked"
            )

        if not existing_token:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired refresh token"
            )

        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == existing_token.id)
            .values(is_revoked=True)
        )

        # 👤 Get user
        user_result = await db.execute(
            select(User).where(User.id == existing_token.user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # 🔑 Generate new tokens
        tokens = await generate_auth_tokens(user, request, db)

        await db.commit()

        # 🍪 Set cookies
        response.set_cookie(
            key="access_token",
            value=tokens["accessToken"],
            httponly=True,
            secure=True,
            samesite="Strict"
        )

        response.set_cookie(
            key="refresh_token",
            value=tokens["refreshToken"],
            httponly=True,
            secure=True,
            samesite="Strict",
            path="/api/v1/auth"
        )

        return {
            "success": True,
            "message": "New access token generated"
        }

    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    token = request.cookies.get("refresh_token")

    if token:
        hashed_token = hash_token(token)

        await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token == hashed_token,
                RefreshToken.user_id == current_user.id,
                RefreshToken.is_revoked == False
            )
            .values(is_revoked=True)
        )

        await db.commit()

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/api/v1/auth")

    return {
        "success": True,
        "message": "Logged out successfully"
    }


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "created_at": str(current_user.created_at) if current_user.created_at else None,
        }
    }