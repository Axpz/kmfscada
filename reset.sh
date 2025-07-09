#!/bin/bash

echo "Resetting SCADA system..."

# Stop and remove containers
docker compose -f docker-compose.yml -f ./dev/docker-compose.dev.yml down -v --remove-orphans