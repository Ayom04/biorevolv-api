import json
from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import schemas
from fastapi.middleware.cors import CORSMiddleware

# -------------------------------
# 🔹 Database Initialization
# -------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sensor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 🔹 Database Dependency
# -------------------------------


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------
# 🔹 WebSocket Connection Manager
# -------------------------------


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("🔌 Client connected")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print("❌ Client disconnected")

    async def broadcast(self, message: dict):
        data = json.dumps(message, default=str)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(data)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()

# -----------------------------
# 🔹 Basic Route
# -----------------------------


@app.get("/api")
def read_root():
    return {"message": "Welcome to the Sensor API"}

# -----------------------------
# 🔹 Sensor CRUD
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
    return db.query(models.Sensor).all()


@app.get("/api/sensors/{sensor_id}", response_model=schemas.SensorWithReadings)
def get_sensor(sensor_id: int, db: Session = Depends(get_db)):
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


@app.delete("/api/sensors/{sensor_id}/readings", response_model=dict)
def delete_sensor_readings(sensor_id: int, db: Session = Depends(get_db)):
    sensor = db.query(models.Sensor).filter(
        models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    deleted_count = db.query(models.SensorReading).filter(
        models.SensorReading.sensor_id == sensor_id).delete()
    db.commit()
    return {"deleted_readings": deleted_count}

# -----------------------------
# 🔹 Sensor Readings
# -----------------------------


@app.post("/api/sensors/data", response_model=schemas.SensorReadingResponse)
async def ingest_data(
    reading: schemas.SensorReadingCreate,
    db: Session = Depends(get_db)
):
    """Receive sensor reading and broadcast to all WebSocket clients."""
    sensor = db.query(models.Sensor).filter(
        models.Sensor.id == reading.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    # ✅ Set safe defaults for missing fields
    data = reading.dict()

    if data.get("value") is None:
        data["value"] = 0.0   # default or previous reading
    if not data.get("unit"):
        data["unit"] = sensor.unit if hasattr(sensor, "unit") else "N/A"
    if data.get("is_present") is None:
        data["is_present"] = True

    db_reading = models.SensorReading(**data)
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)

    # 🔹 Broadcast to all WebSocket clients
    await manager.broadcast({
        "type": "new_reading",
        "sensor_id": db_reading.sensor_id,
        "value": db_reading.value,
        "is_present": db_reading.is_present,
        "timestamp": str(db_reading.timestamp),
    })

    return db_reading


@app.get("/api/sensors/{sensor_id}/readings", response_model=list[schemas.SensorReadingResponse])
def get_readings(sensor_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.SensorReading)
        .filter(models.SensorReading.sensor_id == sensor_id)
        .order_by(models.SensorReading.timestamp.desc())
        .limit(50)
        .all()
    )


@app.get("/api/biogas-data", response_model=list[schemas.BiogasDataResponse])
def get_biogas_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db)
):
    return db.query(models.BiogasData).offset(skip).limit(limit).all()

# -----------------------------------
# 🔹 WebSocket Endpoint
# -----------------------------------


@app.websocket("/ws/sensors")
async def websocket_endpoint(websocket: WebSocket):
    """Each connected client will get new readings in real-time."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


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
