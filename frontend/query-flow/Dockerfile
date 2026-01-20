# sbilife/productanalyst-query-flow-ui
FROM node:lts-alpine

EXPOSE 80
WORKDIR /app/query-flow
RUN apk add gettext
ENV HTTP_PORT=80
ENV API_BASE_URL=
ENV MATERIAL_QUERIES_PATH=/api/v1/material-queries

COPY package.json package-lock.json ./
RUN npm install --omit=dev

COPY run.sh /app/query-flow/
COPY query-ui/css/* /app/query-flow/query-ui/css/
COPY query-ui/index.html /app/query-flow/query-ui/
COPY query-ui/js/*.js /app/query-flow/query-ui/js/

ENTRYPOINT [ "sh", "./run.sh" ]