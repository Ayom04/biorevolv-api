from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine, Base
import models
import schemas
# from ai_service import generate_sensor_insight

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sensor API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api")
def read_root():
    return {"message": "Welcome to the Sensor API"}
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


@app.get("/api/sensors/", response_model=list[schemas.SensorWithReadings])
def get_sensors(db: Session = Depends(get_db)):
    sensors = db.query(models.Sensor).all()
    return sensors


@app.get("/api/sensors/{sensor_id}", response_model=schemas.SensorWithReadings)
def get_sensor(sensor_id: int, db: Session = Depends(get_db)):
    print(sensor_id)
    sensor = db.query(models.Sensor).filter(
        models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return sensor


@app.delete("/api/sensors/{sensor_id}", response_model=schemas.SensorResponse)
def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    sensor = db.query(models.Sensor).filter(
        models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    db.delete(sensor)
    db.commit()
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


@app.get("/api/biogas-data", response_model=list[schemas.BiogasDataResponse])
def get_biogas_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db)
):
    """
    Fetch BiogasData with optional pagination.
    """
    data = db.query(models.BiogasData).offset(skip).limit(limit).all()
    return data

# -----------------------------
# Insights Endpoint (AI integration placeholder)
# -----------------------------

# @app.get("/api/sensors/{sensor_id}/insights")
# def get_insights(sensor_id: int, db: Session = Depends(get_db)):
#     readings = db.query(models.SensorReading).filter(
#         models.SensorReading.sensor_id == sensor_id
#     ).all()

#     if not readings:
#         raise HTTPException(
#             status_code=404, detail="No readings found for this sensor")

# # Prepare readings in dict format for AI
#     readings_data = [
#         {
#             "value": r.value,
#             "unit": r.unit,
#             "timestamp": str(r.timestamp)
#         }
#         for r in readings
#     ]

#     # Call AI service
#     insight = generate_sensor_insight(sensor_id, readings_data)

#     return {
#         "sensor_id": sensor_id,
#         "insight": insight
#     }
