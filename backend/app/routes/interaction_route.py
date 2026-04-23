from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from app.core.database import get_db
from app.models.interaction import Interaction
from app.models.users import User
from app.schemas.interaction import InteractionCreate, InteractionUpdate, InteractionResponse
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    data: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        new_interaction = Interaction(
            hcp_id=data.hcp_id,
            logged_by_user_id=current_user.id,
            interaction_type=data.interaction_type,
            interaction_date=data.interaction_date,
            interaction_time=data.interaction_time,
            topics_discussed=data.topics_discussed,
            sentiment=data.sentiment,
            outcomes=data.outcomes,
            log_method=data.log_method,
            ai_summary=data.ai_summary,
            raw_chat_input=data.raw_chat_input,
        )
        db.add(new_interaction)
        await db.commit()
        await db.refresh(new_interaction, attribute_names=["hcp"])
        return new_interaction

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interaction",
        )


@router.get("/", response_model=list[InteractionResponse])
async def list_interactions(
    hcp_id: Optional[int] = Query(None, description="Filter by HCP"),
    interaction_type: Optional[str] = Query(None, description="Filter by type"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Interaction).options(selectinload(Interaction.hcp))

    if hcp_id is not None:
        query = query.where(Interaction.hcp_id == hcp_id)

    if interaction_type:
        query = query.where(Interaction.interaction_type == interaction_type)

    if sentiment:
        query = query.where(Interaction.sentiment == sentiment)

    query = query.order_by(Interaction.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/count")
async def get_interaction_count(
    hcp_id: Optional[int] = Query(None, description="Count for specific HCP"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(func.count(Interaction.id))

    if hcp_id is not None:
        query = query.where(Interaction.hcp_id == hcp_id)

    result = await db.execute(query)
    total = result.scalar()
    return {"total": total}


@router.get("/my", response_model=list[InteractionResponse])
async def list_my_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Interaction).options(selectinload(Interaction.hcp))
        .where(Interaction.logged_by_user_id == current_user.id)
        .order_by(Interaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Interaction).options(selectinload(Interaction.hcp)).where(Interaction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    return interaction


@router.put("/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(
    interaction_id: int,
    data: InteractionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Interaction).options(selectinload(Interaction.hcp)).where(Interaction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    if interaction.logged_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this interaction")

    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(interaction, field, value)

    try:
        await db.commit()
        await db.refresh(interaction, attribute_names=["hcp"])
        return interaction
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update interaction",
        )


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction(
    interaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Interaction).where(Interaction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    if interaction.logged_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this interaction")

    try:
        await db.delete(interaction)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete interaction",
        )
