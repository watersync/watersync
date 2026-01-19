# =============================================================================
# WaterSync Production Dockerfile
# =============================================================================
# Multi-stage build for smaller production image.
# Uses Python 3.12 with uv for fast dependency installation.

# --- Builder Stage ---
FROM python:3.12-slim-bookworm AS builder

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_SYSTEM_PYTHON=1

WORKDIR ${APP_HOME}

# Install build dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ${APP_HOME}/

# Install production dependencies
RUN uv pip install -e ".[prod]"

# --- Runtime Stage ---
FROM python:3.12-slim-bookworm AS runtime

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR ${APP_HOME}

# Install runtime dependencies only
RUN apt-get update && apt-get install --no-install-recommends -y \
    # Runtime GIS libraries
    gdal-bin \
    libgdal32 \
    libgeos-c1v5 \
    libproj25 \
    # Database client
    libpq5 \
    postgresql-client \
    # Translations
    gettext \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

# Create non-root user for security
RUN groupadd --gid 1000 django \
    && useradd --uid 1000 --gid django --shell /bin/bash --create-home django

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy entrypoint
COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

# Copy application code
COPY --chown=django:django . ${APP_HOME}

# Switch to non-root user
USER django

ENTRYPOINT ["/entrypoint"]
