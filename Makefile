# =============================================================================
# WaterSync Makefile - Docker-First Development
# =============================================================================
# All Python commands run inside Docker containers.
# No local Python environment needed - just Docker and make.
#
# Usage:
#   make help          - Show all available commands
#   make up            - Start all services
#   make shell         - Open bash in Django container
#   make test          - Run tests
# =============================================================================

# Configuration
COMPOSE_FILE := docker-compose.local.yml
COMPOSE_PROD := docker-compose.production.yml
DOCKER_COMPOSE := docker compose -f $(COMPOSE_FILE)
DOCKER_COMPOSE_PROD := docker compose -f $(COMPOSE_PROD)
EXEC := $(DOCKER_COMPOSE) exec django
EXEC_IT := $(DOCKER_COMPOSE) exec -it django
RUN := $(DOCKER_COMPOSE) run --rm django

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

# =============================================================================
# Docker Services
# =============================================================================

.PHONY: up
up: ## Start all Docker services
	@echo "$(GREEN)🚀 Starting all services...$(RESET)"
	@$(DOCKER_COMPOSE) up -d

.PHONY: down
down: ## Stop all Docker services
	@echo "$(YELLOW)🛑 Stopping all services...$(RESET)"
	@$(DOCKER_COMPOSE) down

.PHONY: restart
restart: ## Restart all Docker services
	@echo "$(YELLOW)🔄 Restarting all services...$(RESET)"
	@$(DOCKER_COMPOSE) restart

.PHONY: logs
logs: ## Follow logs from all services
	@$(DOCKER_COMPOSE) logs -f

.PHONY: logs-django
logs-django: ## Follow Django container logs
	@$(DOCKER_COMPOSE) logs -f django

.PHONY: logs-celery
logs-celery: ## Follow Celery worker logs
	@$(DOCKER_COMPOSE) logs -f celeryworker

.PHONY: ps
ps: ## Show running containers
	@$(DOCKER_COMPOSE) ps

.PHONY: build
build: ## Build Docker images
	@echo "$(GREEN)🔨 Building Docker images...$(RESET)"
	@$(DOCKER_COMPOSE) build

.PHONY: build-no-cache
build-no-cache: ## Build Docker images without cache
	@echo "$(GREEN)🔨 Building Docker images (no cache)...$(RESET)"
	@$(DOCKER_COMPOSE) build --no-cache

.PHONY: pull
pull: ## Pull latest base images
	@$(DOCKER_COMPOSE) pull

# =============================================================================
# Shell Access
# =============================================================================

.PHONY: shell
shell: ## Open bash shell in Django container
	@$(EXEC_IT) bash

.PHONY: shell-root
shell-root: ## Open bash shell as root in Django container
	@$(DOCKER_COMPOSE) exec -it -u root django bash

.PHONY: django-shell
django-shell: ## Open Django shell_plus
	@$(EXEC) python manage.py shell_plus

.PHONY: dbshell
dbshell: ## Open PostgreSQL shell
	@$(EXEC) python manage.py dbshell

# =============================================================================
# Django Management
# =============================================================================

.PHONY: migrate
migrate: ## Run database migrations
	@echo "$(GREEN)🗄️ Running migrations...$(RESET)"
	@$(EXEC) python manage.py migrate

.PHONY: makemigrations
makemigrations: ## Create new migrations
	@echo "$(GREEN)📝 Creating migrations...$(RESET)"
	@$(EXEC) python manage.py makemigrations

.PHONY: migrations
migrations: makemigrations migrate ## Create and run migrations

.PHONY: showmigrations
showmigrations: ## Show migration status
	@$(EXEC) python manage.py showmigrations

.PHONY: superuser
superuser: ## Create a superuser
	@echo "$(GREEN)👤 Creating superuser...$(RESET)"
	@$(EXEC_IT) python manage.py createsuperuser

.PHONY: collectstatic
collectstatic: ## Collect static files
	@echo "$(GREEN)📦 Collecting static files...$(RESET)"
	@$(EXEC) python manage.py collectstatic --no-input

.PHONY: check
check: ## Run Django system checks
	@$(EXEC) python manage.py check

.PHONY: check-deploy
check-deploy: ## Run Django deployment checks
	@$(EXEC) python manage.py check --deploy

.PHONY: urls
urls: ## Show all URL patterns
	@$(EXEC) python manage.py show_urls

.PHONY: flush
flush: ## Flush the database (DANGER!)
	@echo "$(YELLOW)⚠️  This will delete all data!$(RESET)"
	@$(EXEC_IT) python manage.py flush

# =============================================================================
# Testing
# =============================================================================

.PHONY: test
test: ## Run tests with pytest
	@echo "$(GREEN)🧪 Running tests...$(RESET)"
	@$(EXEC) pytest

.PHONY: test-v
test-v: ## Run tests with verbose output
	@$(EXEC) pytest -v

.PHONY: test-x
test-x: ## Run tests, stop on first failure
	@$(EXEC) pytest -x

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@echo "$(GREEN)🧪 Running tests with coverage...$(RESET)"
	@$(EXEC) pytest --cov=watersync --cov-report=html --cov-report=term-missing

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@$(EXEC) pytest-watch

# =============================================================================
# Code Quality
# =============================================================================

.PHONY: lint
lint: ## Run ruff linter
	@echo "$(GREEN)🔍 Linting code...$(RESET)"
	@$(EXEC) ruff check .

.PHONY: lint-fix
lint-fix: ## Run ruff linter with auto-fix
	@echo "$(GREEN)🔧 Fixing lint issues...$(RESET)"
	@$(EXEC) ruff check . --fix

.PHONY: format
format: ## Format code with ruff
	@echo "$(GREEN)✨ Formatting code...$(RESET)"
	@$(EXEC) ruff format .

.PHONY: format-check
format-check: ## Check code formatting
	@$(EXEC) ruff format . --check

.PHONY: typecheck
typecheck: ## Run mypy type checking
	@echo "$(GREEN)📝 Type checking...$(RESET)"
	@$(EXEC) mypy watersync

.PHONY: djlint
djlint: ## Lint Django templates
	@$(EXEC) djlint watersync/_templates --lint

.PHONY: djlint-fix
djlint-fix: ## Reformat Django templates
	@$(EXEC) djlint watersync/_templates --reformat

.PHONY: quality
quality: lint format-check typecheck ## Run all quality checks
	@echo "$(GREEN)✅ All quality checks passed!$(RESET)"

.PHONY: precommit
precommit: ## Run pre-commit hooks on all files
	@$(EXEC) pre-commit run --all-files

# =============================================================================
# Documentation
# =============================================================================

.PHONY: docs
docs: ## Serve documentation locally
	@echo "$(GREEN)📚 Starting documentation server...$(RESET)"
	@$(EXEC) mkdocs serve -f docs/mkdocs.yml --dev-addr 0.0.0.0:8001

.PHONY: docs-build
docs-build: ## Build documentation
	@echo "$(GREEN)📚 Building documentation...$(RESET)"
	@$(EXEC) mkdocs build -f docs/mkdocs.yml

# =============================================================================
# Database Services
# =============================================================================

.PHONY: db-up
db-up: ## Start database services only (postgres, redis)
	@echo "$(GREEN)🗄️ Starting database services...$(RESET)"
	@$(DOCKER_COMPOSE) up -d postgres redis

.PHONY: db-down
db-down: ## Stop database services
	@$(DOCKER_COMPOSE) stop postgres redis

.PHONY: db-reset
db-reset: ## Reset database (DANGER!)
	@echo "$(YELLOW)⚠️  This will delete all data!$(RESET)"
	@$(DOCKER_COMPOSE) down -v postgres
	@$(DOCKER_COMPOSE) up -d postgres
	@sleep 3
	@$(MAKE) migrate

# =============================================================================
# Celery
# =============================================================================

.PHONY: celery-logs
celery-logs: ## Follow Celery worker logs
	@$(DOCKER_COMPOSE) logs -f celeryworker celerybeat

.PHONY: flower
flower: ## Open Flower in browser
	@echo "$(GREEN)🌸 Flower is available at http://localhost:5555$(RESET)"
	@xdg-open http://localhost:5555 2>/dev/null || open http://localhost:5555 2>/dev/null || true

# =============================================================================
# Production
# =============================================================================

.PHONY: prod-build
prod-build: ## Build production Docker images
	@echo "$(GREEN)🔨 Building production images...$(RESET)"
	@$(DOCKER_COMPOSE_PROD) build

.PHONY: prod-up
prod-up: ## Start production services
	@$(DOCKER_COMPOSE_PROD) up -d

.PHONY: prod-down
prod-down: ## Stop production services
	@$(DOCKER_COMPOSE_PROD) down

.PHONY: prod-logs
prod-logs: ## Follow production logs
	@$(DOCKER_COMPOSE_PROD) logs -f

# =============================================================================
# Utility
# =============================================================================

.PHONY: clean
clean: ## Clean Python cache files
	@echo "$(GREEN)🧹 Cleaning cache files...$(RESET)"
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true

.PHONY: clean-docker
clean-docker: ## Remove all Docker volumes and images for this project
	@echo "$(YELLOW)⚠️  This will remove all project Docker data!$(RESET)"
	@$(DOCKER_COMPOSE) down -v --rmi local

.PHONY: prune
prune: ## Prune unused Docker resources
	@docker system prune -f

# =============================================================================
# Combined Workflows
# =============================================================================

.PHONY: setup
setup: build up migrate superuser ## Initial project setup
	@echo "$(GREEN)✅ Project setup complete!$(RESET)"
	@echo "$(CYAN)Run 'make logs' to see the output$(RESET)"

.PHONY: reset
reset: down build up migrate ## Rebuild and restart everything
	@echo "$(GREEN)✅ Reset complete!$(RESET)"

.PHONY: fresh
fresh: clean-docker build up migrate ## Complete fresh start
	@echo "$(GREEN)✅ Fresh start complete!$(RESET)"

# =============================================================================
# Help
# =============================================================================

.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)WaterSync - Docker-First Development$(RESET)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
