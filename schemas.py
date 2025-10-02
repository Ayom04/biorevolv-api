from pydantic import BaseModel
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
    readings: List["SensorReadingResponse"] = []


# --- Reading Schemas ---
class SensorReadingCreate(BaseModel):
    sensor_id: int
    value: float
    unit: str


class SensorReadingResponse(SensorReadingCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


# Forward reference fix
SensorWithReadings.update_forward_refs()
