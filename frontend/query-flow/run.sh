#!/bin/sh

export $(grep -v '^#' .env | xargs)


envsubst '$API_BASE_URL $MATERIAL_QUERIES_PATH' < query-ui/js/query-page.js > /tmp/Xxx.js
mv /tmp/Xxx.js query-ui/js/query-page.js

npx serve -l ${HTTP_PORT}
