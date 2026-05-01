import json
import requests
import redis
import os

GIOS_STATIONS_URL = os.getenv("GIOS_STATIONS_URL")
GIOS_SENSORS_URL = os.getenv("GIOS_SENSORS_URL")
GIOS_MEASUREMENTS_URL = os.getenv("GIOS_MEASUREMENTS_URL")

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
    )
# host="host.docker.internal" (without .yaml and .env)

def get_all_stations():
    cached_stations = redis_client.get("stations:all")

    if cached_stations:
        print("Stations loaded from Redis")
        return json.loads(cached_stations)

    print("Stations loaded from GIOS API")

    response = requests.get(
        GIOS_STATIONS_URL,
        params={"page": 0, "size": 500},
        timeout=10
    )
    response.raise_for_status()

    data = response.json()
    stations_list = data.get("Lista stacji pomiarowych", [])

    redis_client.setex("stations:all", 3600, json.dumps(stations_list)) # 1 hour

    return stations_list


def get_station_sensors(station_id: int):
    cache_key = f"sensors:{station_id}"
    cached_sensors = redis_client.get(cache_key)

    if cached_sensors:
        print("Sensors loaded from Redis")
        return json.loads(cached_sensors)

    print("Sensors loaded from GIOS API")

    response = requests.get(
        f"{GIOS_SENSORS_URL}/{station_id}",
        params={"page": 0, "size": 100},
        timeout=10
    )
    response.raise_for_status()

    data = response.json()

    redis_client.setex(cache_key, 3600, json.dumps(data)) # 1 hour

    return data


def get_sensor_measurements(sensor_id: int):
    cache_key = f"measurements:{sensor_id}"
    cached_measurements = redis_client.get(cache_key)

    if cached_measurements:
        print("Measurements loaded from Redis")
        return json.loads(cached_measurements)

    print("Measurements loaded from GIOS API")

    response = requests.get(
        f"{GIOS_MEASUREMENTS_URL}/{sensor_id}",
        timeout=10
    )
    response.raise_for_status()

    data = response.json()

    redis_client.setex(cache_key, 600, json.dumps(data)) # 10 minutes

    return data