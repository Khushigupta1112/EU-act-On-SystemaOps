#!/usr/bin/env bash
# =============================================================================
# SystemaOps AI Compliance Platform — Development Startup Script (Linux/macOS)
# =============================================================================
# Usage: ./scripts/start-dev.sh [--no-migrate] [--rebuild]
#
# Flags:
#   --no-migrate   Skip running Alembic migrations
#   --rebuild      Force rebuild of Docker images before starting
# =============================================================================

set -euo pipefail

# ─── Colours ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Colour

# ─── Script directory (repo root) ────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# ─── Flags ───────────────────────────────────────────────────────────────────
RUN_MIGRATE=true
REBUILD=false

for arg in "$@"; do
  case $arg in
    --no-migrate) RUN_MIGRATE=false ;;
    --rebuild)    REBUILD=true ;;
    *)
      echo -e "${RED}Unknown flag: $arg${NC}"
      echo "Usage: $0 [--no-migrate] [--rebuild]"
      exit 1
      ;;
  esac
done

# ─── Banner ──────────────────────────────────────────────────────────────────
echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════════════╗"
echo "  ║     SystemaOps AI Compliance Platform          ║"
echo "  ║     Development Environment Startup            ║"
echo "  ╚═══════════════════════════════════════════════╝"
echo -e "${NC}"

# ─── Step 1: Check prerequisites ─────────────────────────────────────────────
echo -e "${BOLD}[1/6] Checking prerequisites...${NC}"

check_cmd() {
  local cmd=$1
  local install_hint=$2
  if ! command -v "$cmd" &>/dev/null; then
    echo -e "${RED}✗ '$cmd' not found. Install: $install_hint${NC}"
    exit 1
  fi
  echo -e "${GREEN}✓ $cmd $(${cmd} --version 2>/dev/null | head -1)${NC}"
}

check_cmd "docker"         "https://docs.docker.com/get-docker/"
check_cmd "docker"         "https://docs.docker.com/get-docker/"

# Check docker compose (v2 plugin or standalone v1)
if docker compose version &>/dev/null 2>&1; then
  DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &>/dev/null; then
  DOCKER_COMPOSE="docker-compose"
else
  echo -e "${RED}✗ 'docker compose' not found. Install Docker Desktop or the Compose plugin.${NC}"
  exit 1
fi
echo -e "${GREEN}✓ $DOCKER_COMPOSE ($($DOCKER_COMPOSE version --short 2>/dev/null || echo 'v1'))${NC}"

# Node and Python are optional (only needed for local dev without Docker)
if command -v node &>/dev/null; then
  echo -e "${GREEN}✓ node $(node --version)${NC}"
else
  echo -e "${YELLOW}⚠ node not found (only needed for local frontend dev outside Docker)${NC}"
fi

if command -v python3 &>/dev/null; then
  echo -e "${GREEN}✓ python3 $(python3 --version)${NC}"
else
  echo -e "${YELLOW}⚠ python3 not found (only needed for local backend dev outside Docker)${NC}"
fi

# ─── Step 2: Copy .env if not exists ─────────────────────────────────────────
echo -e "\n${BOLD}[2/6] Configuring environment...${NC}"

cd "$ROOT_DIR"

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo -e "${GREEN}✓ .env created from .env.example${NC}"
  echo -e "${YELLOW}⚠ Review .env and update any secrets before continuing.${NC}"
  echo -e "${YELLOW}  Especially: SECRET_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD${NC}"
  sleep 2
else
  echo -e "${GREEN}✓ .env already exists${NC}"
fi

# ─── Step 3: Build / Start Docker Compose ────────────────────────────────────
echo -e "\n${BOLD}[3/6] Starting Docker services...${NC}"

if [ "$REBUILD" = true ]; then
  echo -e "${BLUE}  Rebuilding images (--rebuild flag)...${NC}"
  $DOCKER_COMPOSE build --no-cache
fi

$DOCKER_COMPOSE up -d --remove-orphans

echo -e "${GREEN}✓ Docker services started${NC}"

# ─── Step 4: Wait for services to be healthy ─────────────────────────────────
echo -e "\n${BOLD}[4/6] Waiting for services to be healthy...${NC}"

wait_healthy() {
  local service=$1
  local max_attempts=${2:-30}
  local attempt=0

  printf "  Waiting for %-20s " "$service..."
  while [ $attempt -lt $max_attempts ]; do
    status=$($DOCKER_COMPOSE ps -q "$service" 2>/dev/null | xargs docker inspect --format='{{.State.Health.Status}}' 2>/dev/null || echo "starting")
    if [ "$status" = "healthy" ]; then
      echo -e "${GREEN}healthy${NC}"
      return 0
    fi
    printf "."
    sleep 2
    attempt=$((attempt + 1))
  done
  echo -e "${RED}TIMEOUT${NC}"
  echo -e "${RED}Service '$service' did not become healthy in time.${NC}"
  echo -e "${YELLOW}Check logs: $DOCKER_COMPOSE logs $service${NC}"
  return 1
}

wait_healthy "postgres" 30
wait_healthy "redis" 15

# ─── Step 5: Run Alembic migrations ──────────────────────────────────────────
if [ "$RUN_MIGRATE" = true ]; then
  echo -e "\n${BOLD}[5/6] Running database migrations...${NC}"
  $DOCKER_COMPOSE exec -T backend alembic upgrade head
  echo -e "${GREEN}✓ Migrations applied${NC}"
else
  echo -e "\n${BOLD}[5/6] Skipping migrations (--no-migrate)${NC}"
fi

# ─── Step 6: Print startup summary ───────────────────────────────────────────
echo -e "\n${BOLD}[6/6] SystemaOps is ready!${NC}"
echo ""
echo -e "${CYAN}  ┌─────────────────────────────────────────────┐"
echo -e "  │  Service URLs                               │"
echo -e "  ├─────────────────────────────────────────────┤"
echo -e "  │  Frontend    →  http://localhost:3000        │"
echo -e "  │  Backend API →  http://localhost:8000        │"
echo -e "  │  API Docs    →  http://localhost:8000/docs   │"
echo -e "  │  Adminer     →  http://localhost:8080        │"
echo -e "  └─────────────────────────────────────────────┘${NC}"
echo ""
echo -e "  ${BOLD}Useful commands:${NC}"
echo -e "    make logs          # Follow all service logs"
echo -e "    make logs-backend  # Follow backend logs only"
echo -e "    make migrate       # Re-run migrations"
echo -e "    make test-backend  # Run backend test suite"
echo -e "    make stop          # Stop all services"
echo ""
