.PHONY: install dev test lint run docker-build docker-up docker-down init-db

install:
	pip install -r requirements.txt

dev:
	uvicorn src.app:create_app --factory --reload --host 0.0.0.0 --port 8088

test:
	python -m pytest

lint:
	ruff check .

run:
	python bot.py

docker-build:
	docker build -t qq-private-ai-companion-bot .

docker-up:
	docker compose up -d

docker-down:
	docker compose down

init-db:
	python scripts/init_db.py
