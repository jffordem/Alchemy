FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.10.12 /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Create a non-root user for security
RUN useradd -m appuser

# Install dependencies first for better caching (exact versions from uv.lock, no dev tools)
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache

# Copy project files, owned by the non-root user (needed by e.g. the /reload route)
COPY --chown=appuser:appuser . .

# Set port for Docker
ENV PORT=8080
EXPOSE 8080
ENV PATH="/app/.venv/bin:$PATH"

USER appuser

# Command to run the Flask app
CMD ["python", "app.py"]
