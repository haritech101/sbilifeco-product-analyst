# sbilife/qdrant-gateway
FROM python:3.12-slim

WORKDIR /usr/local/qdrant-gateway

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-gateway-qdrant==0.1.0 \
    sbilifeco-http-server-vectoriser==0.1.0 \
    sbilifeco-http-server-vector-repo==0.1.1

EXPOSE 80
EXPOSE 81

ENV QDRANT_URL=http://localhost:6333
ENV COLLECTION_NAME=default
ENV VECTORSER_HTTP_PORT=80
ENV VECTOR_REPO_HTTP_PORT=81

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]