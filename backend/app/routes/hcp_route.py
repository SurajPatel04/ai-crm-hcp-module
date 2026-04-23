from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
from app.core.database import get_db
from app.models.hcp import HCP
from app.models.users import User
from app.schemas.hcp import HCPCreate, HCPUpdate, HCPResponse
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/hcp", tags=["hcp"])


# ─── Autocomplete Search (for the form's HCP name field) ────────────
@router.get("/search", response_model=List[HCPResponse])
async def search_hcps(
    q: str = Query("", description="Search query — matches name, institution, or city"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lightweight autocomplete endpoint for the HCP name field.
    Returns matching HCPs by name, institution, or city — ordered by relevance.
    """
    if not q.strip():
        # Return all HCPs up to limit when query is empty
        result = await db.execute(
            select(HCP).order_by(HCP.full_name).limit(limit)
        )
        return result.scalars().all()

    pattern = f"%{q.strip()}%"
    query = (
        select(HCP)
        .where(
            or_(
                HCP.full_name.ilike(pattern),
                HCP.institution.ilike(pattern),
                HCP.city.ilike(pattern),
            )
        )
        .order_by(HCP.full_name)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=HCPResponse, status_code=status.HTTP_201_CREATED)
async def create_hcp(
    hcp_data: HCPCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        new_hcp = HCP(
            full_name=hcp_data.full_name,
            specialty=hcp_data.specialty,
            institution=hcp_data.institution,
            city=hcp_data.city,
            email=hcp_data.email,
            phone=hcp_data.phone,
        )
        db.add(new_hcp)
        await db.commit()
        await db.refresh(new_hcp)
        return new_hcp

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create HCP",
        )


@router.get("/", response_model=list[HCPResponse])
async def list_hcps(
    search: Optional[str] = Query(None, description="Search by name or institution"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(HCP)

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (HCP.full_name.ilike(search_filter)) | (HCP.institution.ilike(search_filter))
        )

    if specialty:
        query = query.where(HCP.specialty == specialty)

    query = query.order_by(HCP.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/count")
async def get_hcp_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(func.count(HCP.id)))
    total = result.scalar()
    return {"total": total}


@router.get("/{hcp_id}", response_model=HCPResponse)
async def get_hcp(
    hcp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()

    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    return hcp


@router.put("/{hcp_id}", response_model=HCPResponse)
async def update_hcp(
    hcp_id: int,
    hcp_data: HCPUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()

    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    update_fields = hcp_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(hcp, field, value)

    try:
        await db.commit()
        await db.refresh(hcp)
        return hcp
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update HCP",
        )


@router.delete("/{hcp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hcp(
    hcp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()

    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    try:
        await db.delete(hcp)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete HCP",
        )
