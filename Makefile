.PHONY: help install dev run test lint format clean doc docker-up docker-down docker-logs

help:
	@echo "HoneyTrap Development Commands"
	@echo "=============================="
	@echo "make install      - Install Python dependencies"
	@echo "make dev          - Install dev dependencies"
	@echo "make run          - Run development server"
	@echo "make test         - Run tests"
	@echo "make test-cov     - Run tests with coverage report"
	@echo "make lint         - Run all linters"
	@echo "make format       - Format code with Black"
	@echo "make clean        - Clean cache/build files"
	@echo "make db-init      - Initialize database"
	@echo "make db-seed      - Seed database with test data"
	@echo "make db-reset     - Reset database"
	@echo "make docker-up    - Start Docker containers"
	@echo "make docker-down  - Stop Docker containers"
	@echo "make docker-logs  - View Docker logs"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

run:
	FLASK_ENV=development FLASK_APP=run.py flask run --debug

run-prod:
	gunicorn -w 4 -b 0.0.0.0:5000 run:app

test:
	FLASK_ENV=testing pytest tests/ -v

test-cov:
	FLASK_ENV=testing pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	-black --check app
	-flake8 app --max-line-length=100
	-pylint app/models.py app/utils/ --disable=all --enable=E,F
	-mypy app --ignore-missing-imports

format:
	black app

check-format:
	black --check app

clean:
	-find . -type d -name __pycache__ -exec rm -rf {} +
	-find . -type f -name "*.pyc" -delete
	-rm -rf .pytest_cache
	-rm -rf .mypy_cache
	-rm -rf htmlcov
	-rm -rf dist build *.egg-info

db-init:
	FLASK_ENV=development flask db upgrade
	FLASK_ENV=development flask init-db

db-seed:
	FLASK_ENV=development flask seed-db

db-reset:
	FLASK_ENV=development flask reset-db

docker-up:
	docker-compose up -d
	@echo "Containers started. Visit http://localhost:5000"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

docker-clean:
	docker-compose down -v
	docker system prune -f

setup-dev: install dev
	cp .env.example .env
	$(MAKE) db-init
	$(MAKE) db-seed
	@echo "Development environment initialized!"

docs:
	cd docs && make html
	@echo "Documentation built in docs/_build/html/index.html"
