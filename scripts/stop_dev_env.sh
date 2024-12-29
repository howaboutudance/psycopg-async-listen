#!/usr/bin/env zsh

# This scriot stops the dev environment by stopping the podman containers and removing the podman pod
# include an -all flag to remove volumes and networks as well

# read .env if present to set variables
if [ -f .env ]; then
    source .env
fi

# query for podman pods associated with the psycopg_async_listen network
# if the pod exists, stop the pod and remove
echo "Stopping pods.."
podman pod ps --filter network=psycopg_async_listen -q | xargs -r podman pod stop

echo "Removing pods.."
podman pod ps --filter network=psycopg_async_listen -q | xargs -r podman pod rm

# if -all flag is present, remove volumes and networks
if [ "$1" = "-all" ]; then
    echo "removing volumes..."
    podman volume rm postgres_data
    podman volume rm mosquitto_data
    podman volume rm mosquitto_log
    podman volume rm redis_data 

    echo "removing networks..."
    podman network rm psycopg_async_listen
fi