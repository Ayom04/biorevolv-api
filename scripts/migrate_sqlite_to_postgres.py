import argparse
from pathlib import Path

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

import models
from database import Base, normalize_database_url

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_URL = f"sqlite:///{BASE_DIR / 'sensors.db'}"


def build_engine(database_url: str):
    engine_kwargs = {}
    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["pool_pre_ping"] = True

    return create_engine(database_url, **engine_kwargs)


def ensure_empty_target(session: Session) -> None:
    counts = {
        "sensors": session.scalar(select(func.count()).select_from(models.Sensor)),
        "sensor_readings": session.scalar(
            select(func.count()).select_from(models.SensorReading)
        ),
        "biogas_data": session.scalar(
            select(func.count()).select_from(models.BiogasData)
        ),
    }

    if any(counts.values()):
        raise RuntimeError(
            "Target PostgreSQL database is not empty. "
            "Use an empty database to avoid duplicate data."
        )


def copy_sensors(source_session: Session, target_session: Session) -> int:
    sensors = source_session.scalars(
        select(models.Sensor).order_by(models.Sensor.id)
    ).all()
    for sensor in sensors:
        target_session.add(
            models.Sensor(
                id=sensor.id,
                name=sensor.name,
                type=sensor.type,
                location=sensor.location,
            )
        )
    return len(sensors)


def copy_readings(source_session: Session, target_session: Session) -> int:
    readings = source_session.scalars(
        select(models.SensorReading).order_by(models.SensorReading.id)
    ).all()
    for reading in readings:
        target_session.add(
            models.SensorReading(
                id=reading.id,
                sensor_id=reading.sensor_id,
                value=reading.value,
                unit=reading.unit,
                is_present=reading.is_present,
                timestamp=reading.timestamp,
            )
        )
    return len(readings)


def copy_biogas_data(source_session: Session, target_session: Session) -> int:
    entries = source_session.scalars(
        select(models.BiogasData).order_by(models.BiogasData.id)
    ).all()
    for entry in entries:
        target_session.add(
            models.BiogasData(
                id=entry.id,
                day=entry.day,
                VS_remaining_kg=entry.VS_remaining_kg,
                VS_degraded_kg=entry.VS_degraded_kg,
                cum_CH4_m3=entry.cum_CH4_m3,
                approx_biogas_m3=entry.approx_biogas_m3,
                VFA_g=entry.VFA_g,
                NaHCO3_g_safety=entry.NaHCO3_g_safety,
            )
        )
    return len(entries)


def reset_postgres_sequences(target_session: Session) -> None:
    table_names = ["sensors", "sensor_readings", "biogas_data"]
    for table_name in table_names:
        target_session.execute(
            text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_name}', 'id'),
                    COALESCE((SELECT MAX(id) FROM {table_name}), 1),
                    (SELECT COUNT(*) > 0 FROM {table_name})
                )
                """
            )
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Copy existing SQLite data into a PostgreSQL database."
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE_URL,
        help=f"Source SQLite URL. Defaults to {DEFAULT_SOURCE_URL}",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Target PostgreSQL DATABASE_URL",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    source_url = normalize_database_url(args.source)
    target_url = normalize_database_url(args.target)

    if not target_url.startswith("postgresql+psycopg://"):
        raise RuntimeError(
            "Target database must be a PostgreSQL URL, for example "
            "'postgresql://user:password@host:5432/dbname'."
        )

    source_engine = build_engine(source_url)
    target_engine = build_engine(target_url)

    Base.metadata.create_all(bind=target_engine)

    with Session(source_engine) as source_session, Session(target_engine) as target_session:
        ensure_empty_target(target_session)

        sensors_count = copy_sensors(source_session, target_session)
        readings_count = copy_readings(source_session, target_session)
        biogas_count = copy_biogas_data(source_session, target_session)

        target_session.commit()
        reset_postgres_sequences(target_session)
        target_session.commit()

    print(
        "Migration complete:",
        f"{sensors_count} sensors,",
        f"{readings_count} readings,",
        f"{biogas_count} biogas rows copied.",
    )


if __name__ == "__main__":
    main()
