#!/usr/bin/env bash
set -euo pipefail

# Manual demo-data loader for a VPS administrator.
# Applies all SQL seeds to the running deploy database only after explicit YES confirmation.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker-compose.deploy.yml"
ENV_FILE="$REPO_ROOT/.env.deploy"
SEEDS_DIR="$REPO_ROOT/infra/sql/seeds"
POSTGRES_SERVICE="pc_postgres"

COMPOSE_CMD=(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE")

log() {
    printf '%s\n' "$1"
}

fail() {
    printf 'Error: %s\n' "$1" >&2
    exit 1
}

if [[ ! -f "$ENV_FILE" ]]; then
    fail "Deploy env file not found: $ENV_FILE"
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
    fail "Deploy compose file not found: $COMPOSE_FILE"
fi

if [[ ! -d "$SEEDS_DIR" ]]; then
    fail "Seeds directory not found: $SEEDS_DIR"
fi

mapfile -t seed_files < <(find "$SEEDS_DIR" -maxdepth 1 -type f -name '*.sql' | sort)

if [[ "${#seed_files[@]}" -eq 0 ]]; then
    fail "No .sql seed files found in $SEEDS_DIR"
fi

if ! "${COMPOSE_CMD[@]}" ps -q "$POSTGRES_SERVICE" >/dev/null 2>&1; then
    fail "Cannot inspect compose service '$POSTGRES_SERVICE'. Make sure the deploy stack is available."
fi

postgres_container_id="$("${COMPOSE_CMD[@]}" ps -q "$POSTGRES_SERVICE")"

if [[ -z "$postgres_container_id" ]]; then
    fail "Service '$POSTGRES_SERVICE' is not running. Start the deploy stack first."
fi

if ! "${COMPOSE_CMD[@]}" exec -T "$POSTGRES_SERVICE" sh -lc 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null; then
    fail "Service '$POSTGRES_SERVICE' is not ready to accept connections."
fi

log "Manual seed loading"
log "Compose file: $COMPOSE_FILE"
log "Env file: $ENV_FILE"
log "Target service: $POSTGRES_SERVICE"
log "Seed files:"
for seed_file in "${seed_files[@]}"; do
    log "  - $(basename "$seed_file")"
done
log "Warning: this will load demo/test data into the deploy database."
printf "Type YES to continue: "
read -r confirmation

if [[ "$confirmation" != "YES" ]]; then
    log "Seed loading cancelled."
    exit 0
fi

for seed_file in "${seed_files[@]}"; do
    log "Applying $(basename "$seed_file")..."
    "${COMPOSE_CMD[@]}" exec -T "$POSTGRES_SERVICE" sh -lc \
        'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f -' \
        < "$seed_file"
done

log "Done."
