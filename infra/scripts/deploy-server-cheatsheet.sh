#!/usr/bin/env bash
set -euo pipefail

# Promo Constructor server deploy cheatsheet.
# Run commands step by step or reuse this file as a checklist.

# 1. Install Docker + Compose plugin on the server (Ubuntu example).
# sudo apt-get update
# sudo apt-get install -y ca-certificates curl git docker.io docker-compose-plugin
# sudo systemctl enable --now docker

# 2. Clone the project.
# git clone <your-repository-url> promo-constructor
# cd promo-constructor

# 3. Prepare deploy environment variables.
# cp .env.deploy.example .env.deploy
# nano .env.deploy
#
# Required minimum changes inside .env.deploy:
# - POSTGRES_PASSWORD
# - PGADMIN_DEFAULT_PASSWORD
# - BACKEND_SECRET_KEY
# - BACKEND_CORS_ORIGINS
# - FRONTEND_PORT
# - BACKEND_COOKIE_SECURE=true for HTTPS

# 4. Build the application images from Dockerfiles.
docker build -t promo-constructor-backend:latest ./backend
docker build -t promo-constructor-frontend:latest ./frontend

# 5. Start PostgreSQL first.
docker compose --env-file .env.deploy -f docker-compose.deploy.yml up -d pc_postgres

# 6. Apply Alembic migrations using the backend image.
docker compose --env-file .env.deploy -f docker-compose.deploy.yml run --rm pc_backend alembic upgrade head

# 7. Start the whole application stack.
docker compose --env-file .env.deploy -f docker-compose.deploy.yml up -d

# 8. Optional: start pgAdmin only when needed.
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml --profile tools up -d pc_pgadmin

# 9. Check status and logs.
docker compose --env-file .env.deploy -f docker-compose.deploy.yml ps
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml logs -f pc_backend
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml logs -f pc_frontend

# 10. Useful maintenance commands.
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml pull
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml down
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml up -d
# docker image prune -f
