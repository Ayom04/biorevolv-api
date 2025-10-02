from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import schemas
from ai_service import generate_sensor_insight

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sensor API")

# Dependency: DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Sensor Endpoints
# -----------------------------

@app.post("/api/sensors/", response_model=schemas.SensorResponse)
def create_sensor(sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    db_sensor = models.Sensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor


@app.get("/api/sensors/{sensor_id}", response_model=schemas.SensorWithReadings)
def get_sensor(sensor_id: int, db: Session = Depends(get_db)):
    sensor = db.query(models.Sensor).filter(
        models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


# -----------------------------
# Sensor Reading Endpoints
# -----------------------------

@app.post("/api/sensors/data", response_model=schemas.SensorReadingResponse)
def ingest_data(reading: schemas.SensorReadingCreate, db: Session = Depends(get_db)):
    sensor = db.query(models.Sensor).filter(
        models.Sensor.id == reading.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    db_reading = models.SensorReading(**reading.dict())
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


@app.get("/api/sensors/{sensor_id}/readings", response_model=list[schemas.SensorReadingResponse])
def get_readings(sensor_id: int, db: Session = Depends(get_db)):
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.sensor_id == sensor_id
    ).all()
    return readings


# -----------------------------
# Insights Endpoint (AI integration placeholder)
# -----------------------------

@app.get("/api/sensors/{sensor_id}/insights")
def get_insights(sensor_id: int, db: Session = Depends(get_db)):
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.sensor_id == sensor_id
    ).all()

    if not readings:
        raise HTTPException(
            status_code=404, detail="No readings found for this sensor")

# Prepare readings in dict format for AI
    readings_data = [
        {
            "value": r.value,
            "unit": r.unit,
            "timestamp": str(r.timestamp)
        }
        for r in readings
    ]

    # Call AI service
    insight = generate_sensor_insight(sensor_id, readings_data)

    return {
        "sensor_id": sensor_id,
        "insight": insight
    }
