from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SensorBase(BaseModel):
    name: str
    type: str
    location: Optional[str] = None


class SensorCreate(SensorBase):
    pass


class SensorResponse(SensorBase):
    id: int

    class Config:
        orm_mode = True


class SensorReadingBase(BaseModel):
    value: float
    unit: str


class SensorReadingCreate(SensorReadingBase):
    sensor_id: int


class SensorReadingResponse(SensorReadingBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class SensorWithReadings(SensorResponse):
    readings: List[SensorReadingResponse] = []
