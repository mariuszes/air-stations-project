# requires Docker Desktop, kubectl, kind and Helm installed

# create cluster
kind create cluster --config .\kind-config.yaml

# build api image
docker build -t air-stations-api:local .
kind load docker-image air-stations-api:local --name air-stations-multi

# create redis storage
docker exec air-stations-multi-worker mkdir -p /mnt/redis-data

# install traefik
helm repo add traefik https://traefik.github.io/charts
helm repo update

helm install traefik traefik/traefik `
    -f .\traefik-values.yaml `
    -n traefik `
    --create-namespace `
    --wait

# create namespace
kubectl apply -f .\k8s\namespace.yaml

# apply kubernetes resources
kubectl apply -f .\k8s\