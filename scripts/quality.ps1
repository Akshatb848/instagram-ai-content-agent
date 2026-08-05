$ErrorActionPreference = 'Stop'
ruff check .
mypy src
pytest
alembic upgrade head
node scripts/validate-workflows.mjs

