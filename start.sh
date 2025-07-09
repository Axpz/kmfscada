#!/bin/bash

docker compose -f docker-compose.scada.yml up -d

echo "SCADA System started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8001" 