# sbilife/sqlite-gateway
FROM python:3.14-alpine

WORKDIR /usr/local/sqlite-gateway

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-gateway-sqlite==0.1.0 \
    sbilifeco-http-server-id-name-repo==0.1.0

EXPOSE 80

ENV HTTP_PORT=80
ENV DB_PATH=

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]