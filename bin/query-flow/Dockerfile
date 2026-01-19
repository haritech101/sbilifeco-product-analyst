# sbilife/productanalyst-query-flow
FROM python:3.14-alpine

WORKDIR /usr/local/query-flow

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-productanalyst-flow-query==0.1.1 \
    sbilifeco-productanalyst-http-server-query-flow==0.1.0 \
    sbilifeco-http-client-llm==0.1.6 \
    sbilifeco-http-client-vectoriser==0.1.0 \
    sbilifeco-http-client-vector-repo==0.1.1

EXPOSE 80

ENV HTTP_PORT=80
ENV LLM_PROTO=http
ENV LLM_HOST=localhost
ENV LLM_PORT=80
ENV VECTORISER_PROTO=http
ENV VECTORISER_HOST=localhost
ENV VECTORISER_PORT=80
ENV VECTOR_REPO_PROTO=http
ENV VECTOR_REPO_HOST=localhost
ENV VECTOR_REPO_PORT=80

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]