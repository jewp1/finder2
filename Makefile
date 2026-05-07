.PHONY: help lint format test up down build logs migrate shell

help:
	@echo "lint     - проверить код (flake8 + black + isort)"
	@echo "format   - отформатировать код (black + isort)"
	@echo "test     - запустить тесты"
	@echo "up       - поднять сервисы"
	@echo "down     - остановить сервисы"
	@echo "build    - пересобрать образы"
	@echo "migrate  - запустить миграции"
	@echo "shell    - Django shell"

lint:
	cd backend && pip install -q -r requirements-lint.txt && flake8 . && black --check . && isort --check-only .

format:
	cd backend && black . && isort .

test:
	cd backend && pytest

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose up --build -d

logs:
	docker-compose logs -f

migrate:
	docker-compose exec backend python manage.py migrate --noinput

shell:
	docker-compose exec backend python manage.py shell
