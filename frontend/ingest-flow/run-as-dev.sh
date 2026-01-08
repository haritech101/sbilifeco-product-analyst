#!/bin/sh

export $(grep -v '^#' .env | xargs)


envsubst < ingest-ui/js/ingest-page.ts > /tmp/Xxx.ts
mv /tmp/Xxx.ts ingest-ui/js/ingest-page.ts
sleep 1
npx live-server --port=${HTTP_PORT}
