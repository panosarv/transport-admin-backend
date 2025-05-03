from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, extract
from typing import List
from datetime import date
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.schemas.booking import (
    BookingCreate, BookingFilter,
    EarningsReport, CountReport, ReportParams
)

async def list_bookings(
    db: AsyncSession,
    current_user,
    filters: BookingFilter
) -> List[Booking]:
    stmt = select(Booking).join(User, Booking.driver)
    stmt = stmt.where(User.company_id == current_user.company_id)
    if current_user.role_id != 1:
        stmt = stmt.where(Booking.driver_id == current_user.id)
    if filters.status:
        stmt = stmt.where(Booking.status == filters.status)
    if filters.date_from:
        stmt = stmt.where(Booking.pickup_time >= filters.date_from)
    if filters.date_to:
        stmt = stmt.where(Booking.pickup_time <= filters.date_to)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_booking(
    db: AsyncSession,
    booking_in: BookingCreate,
    current_user,
    manager
) -> Booking:
    booking = Booking(**booking_in.dict(), driver_id=current_user.id)
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    from app.schemas.booking import BookingRead
    await manager.broadcast({
        'event': 'new_booking',
        'booking': BookingRead.from_orm(booking).dict()
    })
    return booking

async def earnings_report(
    db: AsyncSession,
    current_user,
    params: ReportParams
) -> List[EarningsReport]:
    # Base completed bookings scoped
    base = select(Booking).join(User, Booking.driver).where(
        Booking.status == BookingStatus.completed,
        User.company_id == current_user.company_id
    )
    if current_user.role_id != 1:
        base = base.where(Booking.driver_id == current_user.id)

    # All-time
    if not params.timeframe:
        res = await db.execute(
            select(func.sum(Booking.price).label('total'))
            .select_from(Booking).join(User, Booking.driver)
            .where(
                Booking.status == BookingStatus.completed,
                User.company_id == current_user.company_id
            )
        )
        total = res.scalar() or 0
        return [EarningsReport(period='all_time', total=total)]

    # Yearly reports
    if params.timeframe == 'yearly':
        if params.year:
            # monthly breakdown for given year
            stmt = select(
                extract('month', Booking.pickup_time).label('period'),
                func.sum(Booking.price).label('total')
            ).select_from(Booking).join(User, Booking.driver)
            stmt = stmt.where(
                Booking.status == BookingStatus.completed,
                User.company_id == current_user.company_id,
                extract('year', Booking.pickup_time) == params.year
            ).group_by('period')
        else:
            # annual totals
            stmt = select(
                extract('year', Booking.pickup_time).label('period'),
                func.sum(Booking.price).label('total')
            ).select_from(Booking).join(User, Booking.driver)
            stmt = stmt.where(
                Booking.status == BookingStatus.completed,
                User.company_id == current_user.company_id
            ).group_by('period')
    # Monthly reports
    elif params.timeframe == 'monthly' and params.year and params.month:
        stmt = select(
            extract('week', Booking.pickup_time).label('period'),
            func.sum(Booking.price).label('total')
        ).select_from(Booking).join(User, Booking.driver)
        stmt = stmt.where(
            Booking.status == BookingStatus.completed,
            User.company_id == current_user.company_id,
            extract('year', Booking.pickup_time) == params.year,
            extract('month', Booking.pickup_time) == params.month
        ).group_by('period')
    # Weekly reports
    elif params.timeframe == 'weekly' and params.year and params.month and params.day:
        stmt = select(
            func.date(Booking.pickup_time).label('period'),
            func.sum(Booking.price).label('total')
        ).select_from(Booking).join(User, Booking.driver)
        stmt = stmt.where(
            Booking.status == BookingStatus.completed,
            User.company_id == current_user.company_id,
            func.date(Booking.pickup_time) == params.day
        ).group_by('period')
    else:
        return []

    res = await db.execute(stmt)
    return [EarningsReport(period=str(int(r.period)), total=r.total or 0) for r in res.all()]

async def count_report(
    db: AsyncSession,
    current_user,
    params: ReportParams
) -> List[CountReport]:
    # All-time
    if not params.timeframe:
        res = await db.execute(
            select(func.count().label('count'))
            .select_from(Booking).join(User, Booking.driver)
            .where(User.company_id == current_user.company_id)
        )
        total = res.scalar() or 0
        return [CountReport(period='all_time', count=total)]

    # mimic earnings grouping but count
    rows: List[CountReport] = []
    # implement as needed
    return rows

async def get_booking(
    db: AsyncSession,
    booking_id: int,
    current_user
) -> Booking | None:
    stmt = select(Booking).where(Booking.id == booking_id)
    stmt = stmt.join(User, Booking.driver)
    stmt = stmt.where(User.company_id == current_user.company_id)
    if current_user.role_id != 1:
        stmt = stmt.where(Booking.driver_id == current_user.id)
    res = await db.execute(stmt)
    return res.scalars().first()

async def update_booking_status(
    db: AsyncSession,
    booking_id: int,
    new_status: BookingStatus,
    current_user,
    manager
) -> Booking:
    booking = await get_booking(db, booking_id, current_user)
    if not booking:
        return None
    if current_user.role_id != 1 and booking.driver_id != current_user.id:
        return None
    booking.status = new_status
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    # broadcast update
    from app.schemas.booking import BookingRead
    await manager.broadcast({
        'event': 'update_booking',
        'booking': BookingRead.from_orm(booking).dict()
    })
    return booking