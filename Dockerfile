FROM python:3.14-bookworm AS development-image


ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy && \
    apt-get install --no-install-recommends -qy \
    build-essential \
    ca-certificates \
    gcc  \
    wget

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.14 \
    UV_PROJECT_ENVIRONMENT=/app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project

WORKDIR /app

COPY ./src ./src
COPY ./start.sh ./

ENV PATH=/app/bin:$PATH

RUN chmod +x start.sh

ENTRYPOINT ["/bin/bash", "/app/start.sh"]
