.PHONY: up down logs dev mcp test lint fmt check k8s-validate deploy-k3s deploy-k8s

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

k8s-validate:
	kubectl kustomize infra/k8s/overlays/k3s > /dev/null
	kubectl kustomize infra/k8s/overlays/k8s > /dev/null
	@echo "kustomize overlays render OK"

deploy-k3s:
	kubectl apply -k infra/k8s/overlays/k3s

deploy-k8s:
	kubectl apply -k infra/k8s/overlays/k8s
