from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.vehicle import VehicleRead, VehicleCreate
from app.services.vehicle import list_vehicles, create_vehicle
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/", response_model=List[VehicleRead])
async def read_vehicles(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    is_admin = current_user.role_id == 1  # Adjust this check if role IDs differ
    return await list_vehicles(
        db,
        current_user.company_id,
        current_user.id,
        is_admin
    )

@router.post("/", response_model=VehicleRead, status_code=201)
async def create_new_vehicle(
    vehicle_in: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    
    if current_user.role_id != 1:
        # 403 Forbidden for non-admins
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return await create_vehicle(db, vehicle_in, current_user.company_id)