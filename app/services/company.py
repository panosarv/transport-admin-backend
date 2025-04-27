from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.company import Company
from app.schemas.company import CompanyCreate

async def list_companies(db: AsyncSession) -> list[Company]:
    result = await db.execute(select(Company))
    return result.scalars().all()

async def create_company(db: AsyncSession, company_in: CompanyCreate) -> Company:
    company = Company(**company_in.dict())
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company
