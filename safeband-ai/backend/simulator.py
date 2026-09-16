import random
import time
import requests


API_URL = "http://127.0.0.1:8000/fall/ml-process"
USER_ID = "test-user-001"


def generate_normal_reading():
    return {
        "sensor": {
            "user_id": USER_ID,

            "adxl_acc_x": round(random.uniform(-0.5, 0.5), 3),
            "adxl_acc_y": round(random.uniform(-0.5, 0.5), 3),
            "adxl_acc_z": round(random.uniform(9.3, 10.3), 3),

            "itg_gyro_x": round(random.uniform(-0.2, 0.2), 3),
            "itg_gyro_y": round(random.uniform(-0.2, 0.2), 3),
            "itg_gyro_z": round(random.uniform(-0.2, 0.2), 3),

            "mma_acc_x": round(random.uniform(-0.5, 0.5), 3),
            "mma_acc_y": round(random.uniform(-0.5, 0.5), 3),
            "mma_acc_z": round(random.uniform(9.3, 10.3), 3),

            "heart_rate": random.randint(65, 95),
            "spo2": random.randint(96, 100),
            "sugar_level": random.randint(80, 130),

            "latitude": 11.0168,
            "longitude": 76.9558
        },
        "inactivity_seconds": 0,
        "user_response": "not_confirmed"
    }


def generate_fall_reading():
    return {
        "sensor": {
            "user_id": USER_ID,

            "adxl_acc_x": round(random.uniform(10, 18), 3),
            "adxl_acc_y": round(random.uniform(8, 15), 3),
            "adxl_acc_z": round(random.uniform(15, 25), 3),

            "itg_gyro_x": round(random.uniform(3, 8), 3),
            "itg_gyro_y": round(random.uniform(3, 8), 3),
            "itg_gyro_z": round(random.uniform(3, 8), 3),

            "mma_acc_x": round(random.uniform(10, 18), 3),
            "mma_acc_y": round(random.uniform(8, 15), 3),
            "mma_acc_z": round(random.uniform(15, 25), 3),

            "heart_rate": random.randint(100, 140),
            "spo2": random.randint(88, 96),
            "sugar_level": random.randint(80, 180),

            "latitude": 11.0168,
            "longitude": 76.9558
        },
        "inactivity_seconds": 30,
        "user_response": "confirmed"
    }


def send_reading(payload):
    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=10
        )

        print(f"HTTP Status: {response.status_code}")
        print(response.text)
        print("-" * 70)

    except requests.exceptions.RequestException as error:
        print("Request failed:", error)


if __name__ == "__main__":
    counter = 0

    print("SafeBand AI simulator started...")
    print("Press CTRL+C to stop.")

    while True:
        counter += 1

        if counter % 10 == 0:
            print("Sending simulated FALL reading...")
            payload = generate_fall_reading()
        else:
            print("Sending simulated NORMAL reading...")
            payload = generate_normal_reading()

        send_reading(payload)

        time.sleep(3)