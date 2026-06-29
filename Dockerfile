FROM python:3.14-slim

WORKDIR /app

COPY . .

ENV VIRTUAL_ENV="/app/venv"

RUN python -m venv venv && \
    ./venv/bin/pip install --upgrade pip uv && \
    ./venv/bin/uv pip install "."

ENV PATH="/app/venv/bin:$PATH"

EXPOSE 80

ENTRYPOINT [ "pyfilebrowser", "start-service" ]
