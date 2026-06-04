run:
	python -m app.main

test:
	python -m pytest -q

lint:
	python -m ruff check .

format:
	python -m ruff format .

migrate:
	alembic upgrade head
