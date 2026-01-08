#!/bin/sh

export $(grep -v '^#' .env | xargs)


envsubst '${HTTP_PORT} ${API_BASE_URL} ${API_INGEST_PATH}' < ingest-ui/js/ingest-page.js > /tmp/Xxx.js
mv /tmp/Xxx.js ingest-ui/js/ingest-page.js

npx serve -l ${HTTP_PORT}
