FROM python:3.14-slim

ARG VERSION

WORKDIR /app

ENV VIRTUAL_ENV="/app/venv"

RUN python -m venv venv && \
    ./venv/bin/pip install --upgrade pip uv && \
    ./venv/bin/uv pip install "pyfilebrowser==${VERSION}"

ENV PATH="/app/venv/bin:$PATH"

EXPOSE 80

ENTRYPOINT [ "pyfilebrowser", "start-service" ]
