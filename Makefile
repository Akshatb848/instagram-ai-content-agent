.PHONY: setup validate-env lint format test test-unit test-integration test-render local-up local-down migrate seed export-workflows deploy-n8n deploy-renderer trigger clean
PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e ".[dev]"
validate-env:
	$(PYTHON) -c "from instagram_agent.config import Settings; Settings(); print('configuration valid')"
lint:
	ruff check .
	mypy src
format:
	ruff format .
	ruff check . --fix
test test-unit:
	pytest
test-integration:
	pytest -m integration
test-render:
	pytest tests/test_renderer.py
local-up:
	docker compose -f docker-compose.local.yml up -d --build
local-down:
	docker compose -f docker-compose.local.yml down
migrate:
	alembic upgrade head
seed:
	$(PYTHON) scripts/seed_sources.py
export-workflows:
	node scripts/validate-workflows.mjs
deploy-n8n:
	powershell -ExecutionPolicy Bypass -File infra/tailscale/deploy.ps1
deploy-renderer:
	@echo "Renderer is deployed by GitHub Actions"
trigger:
	@echo "Use workflow_dispatch with an opaque render_job_id"
clean:
	$(PYTHON) scripts/clean.py
