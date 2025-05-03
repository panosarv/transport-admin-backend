# app/schemas/vehicle.py
from pydantic import BaseModel
from typing import Optional

class VehicleBase(BaseModel):
    make: str
    model: str
    driver_id: int
    registration_number: str

class VehicleCreate(VehicleBase):
    """
    Admins supply make, model, driver_id, and registration_number.
    The company_id is injected from the current_user in the service.
    """
    pass

class VehicleRead(VehicleBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True
        orm_mode = True
