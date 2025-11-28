# sbilife/docling-reader
FROM python:3.12

WORKDIR /usr/local/docling-reader

RUN pip install \
    --extra-index-url https://api.repoforge.io/yWf4uV/ \
    python-dotenv==1.1.1 \
    sbilifeco-gateway-pdf-readers==0.1.0 \
    sbilifeco-http-server-material-reader==0.1.1

EXPOSE 80

ENV HTTP_PORT=80

COPY envvars.py service.py ./

ENTRYPOINT ["python", "service.py"]