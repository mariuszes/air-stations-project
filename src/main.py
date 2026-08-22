from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from unidecode import unidecode
import requests
import redis

from src.gios_service import (
    get_all_stations,
    get_station_sensors,
    get_sensor_measurements
)
from src.gios_service import redis_client

app = FastAPI()


def normalize_text(text: str):
    return unidecode(text.lower().strip())


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Air Stations API</title>
    </head>
    <body>
        <h1>Air Stations API</h1>

        <h2>Find stations by city</h2>
        <input id="city" placeholder="City, e.g. Wroclaw">
        <button onclick="getStations()">Search stations</button>

        <h2>Find sensors by station ID</h2>
        <input id="stationId" placeholder="Station ID, e.g. 117">
        <button onclick="getSensors()">Search sensors</button>

        <h2>Find measurements by sensor ID</h2>
        <input id="sensorId" placeholder="Sensor ID, e.g. 670">
        <button onclick="getMeasurements()">Search measurements</button>

        <h2>Result</h2>
        <pre id="result" style="background:#eee; padding:15px;"></pre>

        <script>
            async function showResult(url) {
                const resultBox = document.getElementById("result");
                resultBox.textContent = "Loading...";

                try {
                    const response = await fetch(url);
                    const data = await response.json();
                    resultBox.textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    resultBox.textContent = "Error: " + error;
                }
            }

            function getStations() {
                const city = document.getElementById("city").value;
                showResult("/stations?city=" + encodeURIComponent(city));
            }

            function getSensors() {
                const stationId = document.getElementById("stationId").value;
                showResult("/stations/" + stationId + "/sensors");
            }

            function getMeasurements() {
                const sensorId = document.getElementById("sensorId").value;
                showResult("/sensors/" + sensorId + "/measurements");
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {
        "app": "ok"
    }

@app.get("/ready")
def ready():
    try:
        redis_client.ping()
        return {
            "app": "ok",
            "redis": "ok"
        }
    except redis.RedisError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Redis error: {error}"
        )

@app.get("/stations")
def get_stations(city: str):
    try:
        stations_list = get_all_stations()
    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch stations from GIOS API: {error}"
        )
    except redis.RedisError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Redis error: {error}"
        )

    matching_stations = []

    for station in stations_list:
        station_city = station.get("Nazwa miasta", "")

        if normalize_text(city) == normalize_text(station_city):
            matching_stations.append(
                {
                    "id": station.get("Identyfikator stacji"),
                    "station_name": station.get("Nazwa stacji"),
                    "city": station_city,
                    "street": station.get("Ulica"),
                    "commune": station.get("Gmina"),
                    "district": station.get("Powiat"),
                    "voivodeship": station.get("Województwo"),
                }
            )

    return {
        "city": city,
        "count": len(matching_stations),
        "stations": matching_stations,
        "stations_checked": len(stations_list),
    }


@app.get("/stations/{station_id}/sensors")
def station_sensors(station_id: int):
    try:
        return get_station_sensors(station_id)
    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch sensors from GIOS API: {error}"
        )
    except redis.RedisError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Redis error: {error}"
        )


@app.get("/sensors/{sensor_id}/measurements")
def sensor_measurements(sensor_id: int):
    try:
        return get_sensor_measurements(sensor_id)
    except requests.RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch measurements from GIOS API: {error}"
        )
    except redis.RedisError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Redis error: {error}"
        )