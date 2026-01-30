#!/bin/sh

export $(grep -v '^#' .env | xargs)


envsubst '${HTTP_PORT} ${API_BASE_URL} ${API_INGEST_PATH} ${API_MATERIALS_PATH}' < ingest-ui/js/ingest-page.ts.template > /tmp/Xxx.ts
mv /tmp/Xxx.ts ingest-ui/js/ingest-page.ts
sleep 1
npx live-server --port=${HTTP_PORT} --browser=google-chrome
