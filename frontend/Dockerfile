FROM node:22-alpine AS base

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

FROM base AS development

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

FROM base AS build

RUN npm run build

FROM nginx:1.29-alpine AS production

COPY nginx.http.conf.template /opt/promo-constructor/nginx/nginx.http.conf.template
COPY nginx.https.conf.template /opt/promo-constructor/nginx/nginx.https.conf.template
COPY docker-entrypoint.d/40-configure-https.sh /docker-entrypoint.d/40-configure-https.sh
RUN chmod +x /docker-entrypoint.d/40-configure-https.sh
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]
