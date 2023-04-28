#!/bin/sh

# Wait 30 seconds for the database to build and launch
/etc/scripts/wait-for-it.sh -t 30 core-db:3306 -- echo "Database online"

# Go to application directory and launch FastAPI app
cd /app
uvicorn sedbackend.main:app --host 0.0.0.0 --port 80 --proxy-headers
