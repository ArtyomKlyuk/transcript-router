FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY examples ./examples

RUN pip install .

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

CMD ["python", "examples/run_demo.py"]
