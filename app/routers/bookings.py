from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from typing import List

from app.schemas.booking import (
    BookingCreate, BookingRead, BookingFilter,
    EarningsReport, CountReport, ReportParams, StatusUpdate
)
from app.services.booking import (
    list_bookings, create_booking,
    earnings_report, count_report, get_booking,update_booking_status
)
from app.dependencies import get_db, get_current_user
from app.core.ws import manager

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.websocket("/ws/bookings")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)

@router.get("/", response_model=List[BookingRead])
async def read_bookings(
    status: BookingFilter = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await list_bookings(db, current_user, status)

@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_new_booking(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await create_booking(db, booking_in, current_user, manager)

@router.get("/earnings", response_model=List[EarningsReport])
async def get_earnings(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    params: ReportParams = Depends()
):
    return await earnings_report(db, current_user, params)

@router.get("/count", response_model=List[CountReport])
async def get_counts(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    params: ReportParams = Depends()
):
    return await count_report(db, current_user, params)

@router.get("/{booking_id}/invoice")
async def get_invoice(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    booking = await get_booking(db, booking_id, current_user)
    if not booking:
        raise HTTPException(404, "Booking not found")
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Invoice for Booking #{booking.id}")
    p.drawString(100, 780, f"Driver ID: {booking.driver_id}")
    p.drawString(100, 760, f"Vehicle ID: {booking.vehicle_id}")
    p.drawString(100, 740, f"Price: ${booking.price}")
    p.drawString(100, 720, f"Pickup: {booking.pickup_time}")
    p.drawString(100, 700, f"Dropoff: {booking.dropoff_time}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment;filename=invoice_{booking.id}.pdf'}
    )


@router.patch("/{booking_id}/status", response_model=BookingRead)
async def change_status(
    booking_id: int,
    status_in: StatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    updated = await update_booking_status(
        db, booking_id, status_in.status, current_user, manager
    )
    if not updated:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found or unauthorized")
    return updated