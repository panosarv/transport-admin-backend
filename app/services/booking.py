from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingCreate
from sqlalchemy import and_

async def list_bookings(db: AsyncSession, company_id: int, user_id: int, is_admin: bool):
    stmt = select(Booking).join(User).where(User.company_id == company_id)
    if not is_admin:
        stmt = stmt.where(Booking.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_booking(db: AsyncSession, booking_id: int, company_id: int, user_id: int, is_admin: bool):
    stmt = select(Booking).join(User).where(
        and_(Booking.id == booking_id, User.company_id == company_id)
    )
    if not is_admin:
        stmt = stmt.where(Booking.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_booking(db: AsyncSession, booking_in: BookingCreate, user_id: int, company_id: int):
    booking = Booking(**booking_in.model_dump(), user_id=user_id)
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking

async def delete_booking(db: AsyncSession, booking_id: int, user_id: int, company_id: int, is_admin: bool):
    booking = await get_booking(db, booking_id, company_id, user_id, is_admin)
    if booking:
        await db.delete(booking)
        await db.commit()