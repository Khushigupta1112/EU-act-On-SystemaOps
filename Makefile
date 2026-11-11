# =============================================================================
# SystemaOps AI Compliance Platform — Makefile
# =============================================================================
# Requires: make (GNU Make), docker, docker compose
#
# Usage: make <target>
# Run `make help` to see all available commands.
# =============================================================================

# ─── Configuration ────────────────────────────────────────────────────────────
DOCKER_COMPOSE  := docker compose
BACKEND_SERVICE := backend
FRONTEND_SERVICE:= frontend
PYTHON          := python3
NODE            := node

# Colours
CYAN   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m
RESET  := \033[0m
BOLD   := \033[1m

.DEFAULT_GOAL := help

# ─── Help ─────────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Show this help message
	@echo ""
	@echo "$(BOLD)SystemaOps AI Compliance Platform$(RESET)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(CYAN)%-22s$(RESET) %s\n\n", "Target", "Description"} \
	     /^[a-zA-Z0-9_-]+:.*?##/ { printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# ─── Environment ──────────────────────────────────────────────────────────────
.PHONY: env-setup
env-setup: ## Copy .env.example to .env if it doesn't exist
	@if [ ! -f .env ]; then \
	    cp .env.example .env; \
	    echo "$(GREEN)✓ .env created from .env.example$(RESET)"; \
	    echo "$(YELLOW)  Review and update secrets in .env before continuing$(RESET)"; \
	else \
	    echo "$(GREEN)✓ .env already exists$(RESET)"; \
	fi

# ─── Development ──────────────────────────────────────────────────────────────
.PHONY: dev
dev: env-setup ## Start all Docker services in development mode
	@echo "$(CYAN)Starting development stack...$(RESET)"
	$(DOCKER_COMPOSE) up -d --remove-orphans
	@echo ""
	@echo "$(GREEN)✓ Services started$(RESET)"
	@echo "$(CYAN)  Frontend    →  http://localhost:3000$(RESET)"
	@echo "$(CYAN)  Backend API →  http://localhost:8000$(RESET)"
	@echo "$(CYAN)  API Docs    →  http://localhost:8000/docs$(RESET)"
	@echo "$(CYAN)  Adminer     →  http://localhost:8080$(RESET)"

.PHONY: dev-fg
dev-fg: env-setup ## Start all Docker services in foreground (attached)
	$(DOCKER_COMPOSE) up --remove-orphans

.PHONY: stop
stop: ## Stop all Docker services
	@echo "$(CYAN)Stopping services...$(RESET)"
	$(DOCKER_COMPOSE) stop
	@echo "$(GREEN)✓ Services stopped$(RESET)"

.PHONY: restart
restart: stop dev ## Restart all Docker services

.PHONY: rebuild
rebuild: ## Rebuild Docker images and start services
	@echo "$(CYAN)Rebuilding images...$(RESET)"
	$(DOCKER_COMPOSE) build --no-cache
	$(DOCKER_COMPOSE) up -d --remove-orphans

# ─── Logs ─────────────────────────────────────────────────────────────────────
.PHONY: logs
logs: ## Follow logs from all services
	$(DOCKER_COMPOSE) logs -f

.PHONY: logs-backend
logs-backend: ## Follow backend service logs
	$(DOCKER_COMPOSE) logs -f $(BACKEND_SERVICE)

.PHONY: logs-frontend
logs-frontend: ## Follow frontend service logs
	$(DOCKER_COMPOSE) logs -f $(FRONTEND_SERVICE)

.PHONY: logs-postgres
logs-postgres: ## Follow PostgreSQL logs
	$(DOCKER_COMPOSE) logs -f postgres

# ─── Database Migrations ──────────────────────────────────────────────────────
.PHONY: migrate
migrate: ## Run Alembic migrations (upgrade head)
	@echo "$(CYAN)Running migrations...$(RESET)"
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(RESET)"

.PHONY: migrate-down
migrate-down: ## Revert last Alembic migration
	@echo "$(YELLOW)Reverting last migration...$(RESET)"
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) alembic downgrade -1
	@echo "$(GREEN)✓ Migration reverted$(RESET)"

.PHONY: migrate-history
migrate-history: ## Show Alembic migration history
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) alembic history --verbose

.PHONY: migrate-current
migrate-current: ## Show current Alembic revision
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) alembic current

.PHONY: migrate-new
migrate-new: ## Create a new migration (usage: make migrate-new MSG="add users table")
	@if [ -z "$(MSG)" ]; then \
	    echo "$(RED)Error: MSG is required. Usage: make migrate-new MSG=\"description\"$(RESET)"; \
	    exit 1; \
	fi
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) alembic revision --autogenerate -m "$(MSG)"

# ─── Testing ──────────────────────────────────────────────────────────────────
.PHONY: test-backend
test-backend: ## Run backend pytest suite with coverage
	@echo "$(CYAN)Running backend tests...$(RESET)"
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) \
	    pytest --cov=app --cov-report=term-missing --cov-fail-under=80 -v tests/

.PHONY: test-backend-fast
test-backend-fast: ## Run backend tests (no coverage, faster)
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) pytest -x -q tests/

.PHONY: test-frontend
test-frontend: ## Run frontend Jest test suite
	@echo "$(CYAN)Running frontend tests...$(RESET)"
	$(DOCKER_COMPOSE) exec $(FRONTEND_SERVICE) npm test -- --watchAll=false

.PHONY: test-frontend-coverage
test-frontend-coverage: ## Run frontend tests with coverage report
	$(DOCKER_COMPOSE) exec $(FRONTEND_SERVICE) npm test -- --coverage --watchAll=false

.PHONY: test
test: test-backend test-frontend ## Run all tests (backend + frontend)

# ─── Linting & Formatting ─────────────────────────────────────────────────────
.PHONY: lint
lint: lint-backend lint-frontend ## Run all linters

.PHONY: lint-backend
lint-backend: ## Lint backend Python code (ruff + mypy)
	@echo "$(CYAN)Linting backend...$(RESET)"
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) ruff check .
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) mypy app --ignore-missing-imports

.PHONY: lint-frontend
lint-frontend: ## Lint frontend TypeScript code (ESLint + tsc)
	@echo "$(CYAN)Linting frontend...$(RESET)"
	$(DOCKER_COMPOSE) exec $(FRONTEND_SERVICE) npm run lint
	$(DOCKER_COMPOSE) exec $(FRONTEND_SERVICE) npx tsc --noEmit

.PHONY: format
format: format-backend format-frontend ## Format all code

.PHONY: format-backend
format-backend: ## Format backend Python code (ruff format + isort)
	@echo "$(CYAN)Formatting backend...$(RESET)"
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) ruff format .
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) isort .
	@echo "$(GREEN)✓ Backend formatted$(RESET)"

.PHONY: format-frontend
format-frontend: ## Format frontend code (Prettier)
	@echo "$(CYAN)Formatting frontend...$(RESET)"
	$(DOCKER_COMPOSE) exec $(FRONTEND_SERVICE) npx prettier --write "**/*.{ts,tsx,js,jsx,json,css,md}"
	@echo "$(GREEN)✓ Frontend formatted$(RESET)"

# ─── Security ─────────────────────────────────────────────────────────────────
.PHONY: security-scan
security-scan: ## Run security scans (pip-audit + bandit + npm audit)
	@echo "$(CYAN)Running security scans...$(RESET)"
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) pip-audit -r requirements.txt
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) bandit -r app/ --severity-level medium
	$(DOCKER_COMPOSE) exec $(FRONTEND_SERVICE) npm audit --audit-level=high

# ─── Build ────────────────────────────────────────────────────────────────────
.PHONY: build
build: ## Build production Docker images
	@echo "$(CYAN)Building production images...$(RESET)"
	$(DOCKER_COMPOSE) build --target production
	@echo "$(GREEN)✓ Production images built$(RESET)"

.PHONY: build-backend
build-backend: ## Build production backend image only
	docker build ./backend --target production -t systemaops-backend:latest

.PHONY: build-frontend
build-frontend: ## Build production frontend image only
	docker build ./frontend --target production -t systemaops-frontend:latest

# ─── Database Utilities ───────────────────────────────────────────────────────
.PHONY: db-shell
db-shell: ## Open psql shell in the PostgreSQL container
	$(DOCKER_COMPOSE) exec postgres psql -U systemaops -d systemaops

.PHONY: db-reset
db-reset: ## Drop and recreate the dev database (DESTRUCTIVE)
	@echo "$(RED)WARNING: This will delete all data in the dev database!$(RESET)"
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
	    $(DOCKER_COMPOSE) exec postgres dropdb -U systemaops systemaops --if-exists; \
	    $(DOCKER_COMPOSE) exec postgres createdb -U systemaops systemaops; \
	    $(MAKE) migrate; \
	    echo "$(GREEN)✓ Database reset complete$(RESET)"; \
	else \
	    echo "Aborted."; \
	fi

# ─── Shell Access ─────────────────────────────────────────────────────────────
.PHONY: shell-backend
shell-backend: ## Open a bash shell in the backend container
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) bash

.PHONY: shell-frontend
shell-frontend: ## Open a bash shell in the frontend container
	$(DOCKER_COMPOSE) exec $(FRONTEND_SERVICE) sh

# ─── Status ───────────────────────────────────────────────────────────────────
.PHONY: status
status: ## Show status of all running services
	$(DOCKER_COMPOSE) ps

# ─── Cleanup ──────────────────────────────────────────────────────────────────
.PHONY: clean
clean: ## Stop containers and remove volumes (DESTRUCTIVE)
	@echo "$(RED)WARNING: This will remove all containers and volumes!$(RESET)"
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
	    $(DOCKER_COMPOSE) down -v --remove-orphans; \
	    echo "$(GREEN)✓ Clean complete$(RESET)"; \
	else \
	    echo "Aborted."; \
	fi

.PHONY: clean-images
clean-images: ## Remove all SystemaOps Docker images
	docker images --filter reference="systemaops*" -q | xargs -r docker rmi -f

.PHONY: prune
prune: ## Prune unused Docker resources (system-wide)
	docker system prune -f
