# sbilife/ingest-flow 
FROM python:3.12

WORKDIR /usr/local/ingest-flow

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-productanalyst-flow-ingest==0.1.2 \
    sbilifeco-productanalyst-http-server-ingest-flow==0.1.0 \
    sbilifeco-http-client-material-reader==0.1.0 \
    sbilifeco-http-client-vectoriser==0.1.0 \
    sbilifeco-http-client-vector-repo==0.1.1 \
    sbilifeco-http-client-id-name-repo==0.1.0

EXPOSE 80

ENV HTTP_PORT=80
ENV MATERIAL_READER_PROTO=http
ENV MATERIAL_READER_HOST=localhost
ENV MATERIAL_READER_PORT=80
ENV VECTORISER_PROTO=http
ENV VECTORISER_HOST=localhost
ENV VECTORISER_PORT=80
ENV VECTOR_REPO_PROTO=http
ENV VECTOR_REPO_HOST=localhost
ENV VECTOR_REPO_PORT=80

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]