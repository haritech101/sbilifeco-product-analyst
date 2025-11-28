# sbilife/chromadb-gateway
FROM python:3.12

WORKDIR /usr/local/chromadb-gateway

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-gateway-chromadb==0.1.0 \
    sbilifeco-http-server-vectoriser==0.1.0 \
    sbilifeco-http-server-vector-repo==0.1.0

EXPOSE 80
EXPOSE 81

ENV HTTP_PORT_VECTORISER=80
ENV HTTP_PORT_VECTOR_REPO=80
ENV DB_PATH=
ENV COLLECTION_NAME=

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]