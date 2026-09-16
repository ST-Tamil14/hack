from fastapi import APIRouter

from backend.app.schemas.schemas import SensorReading

router = APIRouter(
    prefix="/sensor",
    tags=["Sensor"]
)


@router.post("/data")
def receive_sensor_data(sensor_data: SensorReading):
    return {
        "message": "Sensor data received successfully",
        "data": sensor_data.model_dump()
    }