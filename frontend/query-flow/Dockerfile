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
COPY product-query-ui/css/* /app/query-flow/product-query-ui/css/
COPY product-query-ui/index.html /app/query-flow/product-query-ui/
COPY product-query-ui/js/*.js /app/query-flow/product-query-ui/js/

ENTRYPOINT [ "sh", "./run.sh" ]