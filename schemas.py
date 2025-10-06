from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Sensor Schemas ---


class SensorCreate(BaseModel):
    name: str
    type: str
    location: Optional[str] = None


class SensorResponse(SensorCreate):
    id: int

    class Config:
        orm_mode = True


class SensorWithReadings(SensorResponse):
    # avoid mutable default; ensure nested response is parsed from ORM
    readings: List["SensorReadingResponse"] = Field(default_factory=list)

    class Config:
        orm_mode = True


# --- Reading Schemas ---
class SensorReadingCreate(BaseModel):
    sensor_id: int
    value: float
    unit: str
    is_present: Optional[bool] = True


class SensorReadingResponse(SensorReadingCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


# Forward reference fix
SensorWithReadings.update_forward_refs()
