FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_EDITABLE=1

RUN pip install --no-cache-dir uv==0.13.7 \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

# Lockfile obrigatório para builds reproduzíveis (sem .env na imagem).
COPY pyproject.toml uv.lock README.md ./
COPY app ./app

RUN uv sync --locked --no-dev --no-editable \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
