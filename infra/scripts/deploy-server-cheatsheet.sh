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
# chmod +x infra/scripts/apply-seeds.sh

# 3. Prepare deploy environment variables.
# cp .env.deploy.example .env.deploy
# nano .env.deploy
#
# Required minimum changes inside .env.deploy:
# - POSTGRES_PASSWORD
# - PGADMIN_DEFAULT_PASSWORD
# - BACKEND_SECRET_KEY
# - BACKEND_CORS_ORIGINS
# - FRONTEND_SERVER_NAMES
# - CERTBOT_EMAIL
# - CERTBOT_CERT_NAME
# - BACKEND_COOKIE_SECURE=true for HTTPS
# - API_ADMIN_KEY (required on VPS for backend API unlock)
# - FRONTEND_INTERNAL_API_KEY (required so frontend UI can proxy to backend without manual headers)

# 4. Build the application images from Dockerfiles.
docker build -t promo-constructor-backend:latest ./backend
docker build -t promo-constructor-frontend:latest ./frontend

# 5. Start PostgreSQL first.
docker compose --env-file .env.deploy -f docker-compose.deploy.yml up -d pc_postgres

# 6. Apply Alembic migrations using the backend image.
docker compose --env-file .env.deploy -f docker-compose.deploy.yml run --rm pc_backend alembic upgrade head

# 7. Start the whole application stack.
docker compose --env-file .env.deploy -f docker-compose.deploy.yml up -d

# Backend API protection note:
# - if API admin protection is enabled, direct /api/v1/*, /docs, /redoc and /swagger require the X-Admin-Key header
# - regular frontend UI traffic goes through an internal nginx proxy path and does not require the browser to set X-Admin-Key manually
# - no browser unlock page is used in the current simplified protection model

# 8. Optional manual seed loading for demo/test data.
# This is intentionally not part of migrations or automatic startup.
# Run only when you explicitly want to populate the deploy database with seed data:
# sudo ./infra/scripts/apply-seeds.sh
# If the script is not executable on the server, run:
# sudo bash ./infra/scripts/apply-seeds.sh

# 9. Before requesting certificates:
# - make sure your domain A/AAAA records point to this VPS
# - make sure ports 80 and 443 are open on the server/firewall
# - make sure no host-level nginx/apache occupies ports 80/443
# - on Ubuntu, inspect listeners with:
#   sudo ss -tulpn | grep -E ':(80|443)\s'
# - if UFW is enabled, inspect rules with:
#   sudo ufw status verbose
# - if needed, open ports with:
#   sudo ufw allow 80/tcp
#   sudo ufw allow 443/tcp
# - if your VPS provider has a cloud firewall/security group, make sure 80/443 are allowed there too
#
# Optional sanity-check for ACME webroot:
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml run --rm --entrypoint sh certbot -c \
#   "mkdir -p /var/www/certbot/.well-known/acme-challenge && echo ok > /var/www/certbot/.well-known/acme-challenge/test"
# Then open:
# http://your-domain.example/.well-known/acme-challenge/test

# 10. Request the first certificate with webroot challenge.
# Replace domains and email with your real values.
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml run --rm certbot \
#   certonly --webroot -w /var/www/certbot \
#   --cert-name example.com \
#   -d example.com -d www.example.com \
#   --email you@example.com --agree-tos --no-eff-email
#
# After successful issue, restart frontend so nginx switches to HTTPS config.
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml restart pc_frontend

# 11. pgAdmin is part of the mandatory stack and is reachable over HTTPS after certificate issue:
# https://your-domain.example/pgadmin/

# 12. Check status and logs.
docker compose --env-file .env.deploy -f docker-compose.deploy.yml ps
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml logs -f pc_backend
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml logs -f pc_frontend

# 13. Renew certificates periodically from host cron.
# Example cron entry:
# 0 3 * * * cd /path/to/promo-constructor && docker compose --env-file .env.deploy -f docker-compose.deploy.yml run --rm certbot renew --webroot -w /var/www/certbot && docker compose --env-file .env.deploy -f docker-compose.deploy.yml exec -T pc_frontend nginx -s reload

# 14. Useful maintenance commands.
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml pull
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml down
# docker compose --env-file .env.deploy -f docker-compose.deploy.yml up -d
# docker image prune -f
