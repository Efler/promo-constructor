#!/bin/sh
set -eu

TEMPLATE_DIR="/opt/promo-constructor/nginx"
CONF_PATH="/etc/nginx/conf.d/default.conf"

FRONTEND_SERVER_NAMES="${FRONTEND_SERVER_NAMES:-_}"
CERTBOT_CERT_NAME="${CERTBOT_CERT_NAME:-}"
FRONTEND_INTERNAL_API_KEY="${FRONTEND_INTERNAL_API_KEY:-}"

export FRONTEND_SERVER_NAMES CERTBOT_CERT_NAME FRONTEND_INTERNAL_API_KEY

if [ -n "$CERTBOT_CERT_NAME" ] \
  && [ -f "/etc/letsencrypt/live/$CERTBOT_CERT_NAME/fullchain.pem" ] \
  && [ -f "/etc/letsencrypt/live/$CERTBOT_CERT_NAME/privkey.pem" ]; then
  envsubst '${FRONTEND_SERVER_NAMES} ${CERTBOT_CERT_NAME} ${FRONTEND_INTERNAL_API_KEY}' \
    < "$TEMPLATE_DIR/nginx.https.conf.template" \
    > "$CONF_PATH"
else
  envsubst '${FRONTEND_SERVER_NAMES}' \
    < "$TEMPLATE_DIR/nginx.http.conf.template" \
    > "$CONF_PATH"
fi
