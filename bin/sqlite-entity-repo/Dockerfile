# sbilife/sqlite-id-name-repo
FROM python:3.12

WORKDIR /usr/local/sqlite-id-name-repo

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-gateway-entity-repo-sqlite==0.1.0 \
    sbilifeco-http-server-id-name-repo==0.1.0

EXPOSE 80

ENV HTTP_PORT=80
ENV DB_PATH=

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]