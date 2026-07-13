.PHONY: up down logs dev mcp test lint fmt check

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

dev:
	uvicorn app.main:app --reload --port 8080

mcp:
	python -m connectors.mcp.server

test:
	pytest

lint:
	ruff check .

fmt:
	ruff check --fix .
	ruff format .

check:
	bash scripts/check_clean_room.sh
