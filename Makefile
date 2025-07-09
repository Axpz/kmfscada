.PHONY: help install dev lint format clean db-init db-migrate db-upgrade db-downgrade

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

check: ## Check Python version (3.12+)
	python scripts/check_python_version.py

install: check ## Install dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

lint: ## Run linting
	flake8 app
	mypy app

format: ## Format code
	black app
	isort app

clean: ## Clean up cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

db-init: ## Initialize database
	python scripts/init_db.py

db-migrate: ## Create new migration
	alembic revision --autogenerate -m "$(message)"

db-upgrade: ## Apply migrations
	alembic upgrade head

db-downgrade: ## Rollback migration
	alembic downgrade -1

docker: ## Build Docker image
	docker build -t kmfscada:latest .

docker-build: ## Build Docker image
	docker build --platform linux/amd64 -t kmfscada-linux-amd64:latest .

docker-run: ## Run Docker container
	docker run -p 8000:8000 kmfscada:latest

docker-compose-up: ## Start services with Docker Compose
	docker-compose up -d

docker-compose-down: ## Stop services with Docker Compose
	docker-compose down

supabase-up: ## Start Supabase services
	docker-compose -f docker-compose.scada.yml up -d

supabase-down: ## Stop Supabase services
	docker-compose -f docker-compose.scada.yml down

supabase-logs: ## View Supabase logs
	docker-compose -f docker-compose.scada.yml logs -f

setup: install db-init ## Complete setup (install + init db)
	@echo "Setup complete! Run 'make dev' to start the development server."

setup-supabase: install db-init supabase-up ## Complete setup with Supabase
	@echo "Supabase setup complete! Run 'make supabase-logs' to view logs." 