#!/usr/bin/env zsh

# This script is converting the docker-compose.yml to a podman setup script using
# podman pods, volumes and networks.

# read .env if present to set variables
if [ -f .env ]; then
    source .env
fi

# if POSTGRES_PORT is not set, set it to 5433
if [ -z "$POSTGRES_PORT" ]; then
    POSTGRES_PORT=5433
fi

# if either MOSQUITTO_MQTT_PORT or MOSQUITTO_HTTP_PORT is not set, set it to 1883 and 9001
# respectively
if [[ -z "$MOSQUITTO_MQTT_PORT" || -z "$MOSQUITTO_HTTP_PORT" ]]; then
    MOSQUITTO_MQTT_PORT=1883
    MOSQUITTO_HTTP_PORT=9001
fi

# if REDIS_PORT is not set, set it to 6379
if [ -z "$REDIS_PORT" ]; then
    REDIS_PORT=6379
fi

# setup network psycopg_async_listen network if does not exist
if ! podman network inspect psycopg_async_listen &> /dev/null; then
    podman network create psycopg_async_listen
fi

# if check if POSTGRES_PORT is already in use, using netcat
# if not:
# - create a postgres pod
# - create a postgres volume
# - start a postgres container
if [ nc -z localhost $POSTGRES_PORT ]; then
    echo "Error: Port $POSTGRES_PORT is already in use"
    exit 1
# else if POSTGRES_PASS is not set, echo an error message and exit
elif [ -z "$POSTGRES_PASS" ]; then
    echo "Error: POSTGRES_PASS is not set"
    exit 1
else
    podman pod create --name postgres_pod -p $POSTGRES_PORT:5432 --network psycopg_async_listen
    podman volume create postgres_data
    podman run --pod postgres_pod -v postgres_data:/var/lib/postgresql/data:Z -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=$POSTGRES_PASS -e POSTGRES_DB=postgres -d docker.io/library/postgres:13
fi

# if check if MOSQUITTO_MQTT_PORT or MOSQUITTO_HTTP_PORT is already in use, check using netcat,
# then echo and error message and exit
# if not:
# - create a mosquitto pod
# - create a mosquitto data volume
# - create a mosquitto log volume
# - start a mosquitto container
if nc -z localhost $MOSQUITTO_MQTT_PORT || nc -z localhost $MOSQUITTO_HTTP_PORT; then
    echo "Error: Port $MOSQUITTO_MQTT_PORT or $MOSQUITTO_HTTP_PORT is already in use"
    exit 1
else
    podman pod create --name mosquitto_pod -p $MOSQUITTO_MQTT_PORT:1883 -p $MOSQUITTO_HTTP_PORT:9001 --network psycopg_async_listen
    podman volume create mosquitto_data
    podman volume create mosquitto_log
    podman run --pod mosquitto_pod -v mosquitto_data:/mosquitto/data:Z -v mosquitto_log:/mosquitto/log:Z -d docker.io/eclipse-mosquitto
fi

# if check if REDIS_PORT is already in use, using netcat
# if not:
# - create a redis pod
# - create a redis volume
# - start a redis container
if nc -z localhost $REDIS_PORT; then
    echo "Error: Port $REDIS_PORT is already in use"
    exit 1
else
    podman pod create --name redis_pod -p $REDIS_PORT:6379 --network psycopg_async_listen
    podman volume create redis_data
    podman run --pod redis_pod -v redis_data:/data:Z -d docker.io/library/redis:6
fi

