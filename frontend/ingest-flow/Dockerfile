# sbilife/productanalyst-ingest-flow-ui
FROM node:lts-alpine

EXPOSE 80
WORKDIR /app/ingest-flow
RUN apk add gettext
ENV HTTP_PORT=80
ENV API_BASE_URL=
ENV API_INGEST_PATH=/api/v1/ingest-requests

COPY package.json package-lock.json ./
RUN npm install --omit=dev

COPY run.sh /app/ingest-flow/
COPY ingest-ui/css/* /app/ingest-flow/ingest-ui/css/
COPY ingest-ui/index.html /app/ingest-flow/ingest-ui/
COPY ingest-ui/js/*.js /app/ingest-flow/ingest-ui/js/

ENTRYPOINT [ "sh", "./run.sh" ]