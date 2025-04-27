from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.booking import BookingCreate, BookingRead
from app.services.booking import (
    list_bookings,
    get_booking,
    create_booking,
    delete_booking
)
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.get("/", response_model=List[BookingRead])
async def read_bookings(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    is_admin = current_user.role_id == 1
    return await list_bookings(
        db,
        current_user.company_id,
        current_user.id,
        is_admin
    )

@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_new_booking(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await create_booking(
        db,
        booking_in,
        current_user.id,
        current_user.company_id
    )

@router.get("/{booking_id}", response_model=BookingRead)
async def read_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    is_admin = current_user.role_id == 1
    booking = await get_booking(
        db,
        booking_id,
        current_user.company_id,
        current_user.id,
        is_admin
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    is_admin = current_user.role_id == 1
    await delete_booking(
        db,
        booking_id,
        current_user.id,
        current_user.company_id,
        is_admin
    )