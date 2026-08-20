FROM python:3.11-slim

# Install uv (borrowed from the official uv image).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies from the lockfile first (project source not needed yet, for caching).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application source and install the project itself.
COPY app ./app
RUN uv sync --frozen --no-dev

# Put the virtualenv on PATH so `uvicorn` resolves directly.
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
