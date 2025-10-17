from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Boolean


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    location = Column(String)

    readings = relationship("SensorReading", back_populates="sensor")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    is_present = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sensor = relationship("Sensor", back_populates="readings")


class BiogasData(Base):
    __tablename__ = "biogas_data"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(Float, nullable=False)
    VS_remaining_kg = Column(Float, nullable=False)
    VS_degraded_kg = Column(Float, nullable=False)
    cum_CH4_m3 = Column(Float, nullable=False)
    approx_biogas_m3 = Column(Float, nullable=False)
    VFA_g = Column(Float, nullable=False)
    NaHCO3_g_safety = Column(Float, nullable=False)
