#!/bin/sh

export $(grep -v '^#' .env | xargs)


envsubst '$API_BASE_URL $MATERIAL_QUERIES_PATH' < product-query-ui/js/query-page.ts.template > product-query-ui/js/query-page.ts
sleep 1
live-server --port=8000
