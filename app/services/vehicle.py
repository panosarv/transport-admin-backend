from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.vehicle import Vehicle

async def list_vehicles(
    db: AsyncSession,
    company_id: int,
    user_id: int,
    is_admin: bool
) -> list[Vehicle]:
    """
    Return all vehicles for a company if admin;
    otherwise only vehicles assigned to the user.
    """
    stmt = select(Vehicle).where(Vehicle.company_id == company_id)
    if not is_admin:
        stmt = stmt.where(Vehicle.driver_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_vehicle(
    db: AsyncSession,
    vehicle_in: Vehicle,
    company_id: int
) -> Vehicle:
    """
    Create a new vehicle and assign it to the company.
    """
    vehicle = Vehicle(
        **vehicle_in.dict(exclude_unset=True),
        company_id=company_id
    )
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle