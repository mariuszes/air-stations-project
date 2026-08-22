# Air Stations API

A small Docker-based project using Python, FastAPI, Redis and the public GIOŚ air quality API.

The application allows users to search air quality stations by city, check sensors available at a selected station and fetch measurement data for a selected sensor.

## Features

* Dockerfile for building the Python application
* Docker Compose for running the application and Redis together
* `.env` file for environment variables
* Redis cache
* Redis volume for data persistence
* Health check endpoint
* FastAPI backend
* Simple HTML interface
* Integration with the public GIOŚ air quality API


## How to Run

Build and start the whole project:
`docker compose up --build`

http://localhost:8000

Remove containers and volumes:
`docker compose down --volumes`

To run the Kubernetes version of the project, run this command in your terminal: `.\start-k8s.ps1`

## Available Pages and API Routes

* **Web interface**

_GET /_ - opens a simple page where the user can test all main functions from the browser.
 


`http://localhost:8000`


* **Health check**

_GET /health_ - checks whether the FastAPI application is running.

`http://localhost:8000/health`

* **Readiness check**

_GET /ready_ - checks if the application and Redis are ready to serve requests.

`http://localhost:8000/ready`

* **Find stations by city**

_GET /stations?city=wroclaw_ - returns air quality stations for the selected city.

Example:
`http://localhost:8000/stations?city=wroclaw`

* **Find sensors by station ID**

_GET /stations/{station_id}/sensors_ - returns sensors available at the selected station.

Example:
`http://localhost:8000/stations/117/sensors`

* **Find measurements by sensor ID**

_GET /sensors/{sensor_id}/measurements_  - returns measurement data for the selected sensor.

Example:
`http://localhost:8000/sensors/670/measurements`

## Docker

The project uses two containers:

1. `app` - FastAPI Python application

2. `redis` - Redis cache database

The Python app is built from the local Dockerfile.
Redis uses the official redis:alpine image.

## Redis Cache

Redis is used as a cache layer.

The application stores:

1. `stations:all` -
Full list of air quality stations

2. `sensors:{station_id}` -
Sensors for a selected station

3. `measurements:{sensor_id}` -
Measurements for a selected sensor

This reduces the number of requests sent to the external GIOŚ API.


## Kubernetes

While revisiting this project to learn Kubernetes, I practiced:

- Multi-node kind cluster
- Deployments and ReplicaSets
- Pod self-healing and node failure recovery
- Scaling and rolling updates
- ClusterIP, NodePort and headless Services
- CoreDNS, service discovery and EndpointSlices
- ConfigMaps (loading environment configuration previously kept in `.env`) and namespaces
- Liveness and readiness probes
- CPU and memory requests and limits
- kube-proxy, API Server, iptables concepts and Pod-to-Pod communication
- Traefik Ingress Controller, IngressClass and `networking.k8s.io/v1` Ingress
- StatefulSet with stable Pod identity
- PersistentVolume and PersistentVolumeClaim
- Local persistent storage with node affinity

The Redis StatefulSet intentionally uses a single replica. It was mainly added to understand StatefulSet behaviour, stable Pod identity and persistent storage. Scaling this particular setup to multiple Redis replicas sharing the same volume could lead to <u>race conditions</u>.

While revisiting this project to learn Kubernetes, I read *Kubernetes: Up & Running*. Since I used an older edition, I often checked current Kubernetes documentation to understand how some of the older concepts are handled today - for example, using EndpointSlices instead of the older Endpoints API, current node affinity mechanisms and Gateway API (I still used Ingress here to learn the fundamentals).

## Notes

Some sensors may not return measurement data. This depends on the GIOŚ API and the type of measurement station.
