# =============================================================================
# WaterSync Local Development Dockerfile
# =============================================================================
# Uses Python 3.12 with uv for fast dependency installation.
# GDAL and GIS libraries are installed via apt.

FROM python:3.12-slim-bookworm

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_SYSTEM_PYTHON=1

WORKDIR ${APP_HOME}

# Install system dependencies including GIS libraries
RUN apt-get update && apt-get install --no-install-recommends -y \
    # Build tools (for any packages that need compilation)
    build-essential \
    libpq-dev \
    # GIS libraries
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    # Development tools
    sudo \
    git \
    bash-completion \
    nano \
    # Database client
    postgresql-client \
    # Translations
    gettext \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

# Create devcontainer user for VS Code compatibility
RUN groupadd --gid 1000 dev-user \
    && useradd --uid 1000 --gid dev-user --shell /bin/bash --create-home dev-user \
    && echo dev-user ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/dev-user \
    && chmod 0440 /etc/sudoers.d/dev-user

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Copy dependency files first for layer caching
COPY pyproject.toml README.md ${APP_HOME}/

# Install Python dependencies (dev = development extras)
RUN uv pip install -e ".[dev]"

# Copy entrypoint
COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

# Copy application code
COPY . ${APP_HOME}

ENTRYPOINT ["/entrypoint"]
