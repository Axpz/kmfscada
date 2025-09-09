.PHONY: help install dev lint format clean db-init db-migrate db-upgrade db-downgrade up

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

check: ## Check Python version (3.12+)
	source ~/venv/bin/activate && python3 scripts/check_python_version.py

install: check ## Install dependencies
	pip install -r requirements.txt

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

ssl-generate: ## Generate SSL certificates
	./scripts/manage_ssl_certs.sh generate

ssl-verify: ## Verify SSL certificates
	./scripts/manage_ssl_certs.sh verify

ssl-renew: ## Renew SSL certificates
	./scripts/manage_ssl_certs.sh renew

up: ## Start production environment with SCADA
	docker network inspect zxnet >/dev/null 2>&1 || docker network create zxnet
	docker compose -f docker-compose.base.yml -f docker-compose.scada.yml up -d

dev: ## Start development environment with RabbitMQ
	docker network inspect zxnet >/dev/null 2>&1 || docker network create zxnet
	docker compose -f docker-compose.base.yml up -d
	# docker compose -f docker-compose.rabbitmq.yml up -d
	source ~/venv/bin/activate && python3 main.py

dev-down: ## Stop development environment
	docker compose -f docker-compose.base.yml -f docker-compose.rabbitmq.yml down

test-mqtt-ssl-full: ## Complete MQTT SSL test (start services + test + cleanup)
	@echo "🚀 启动完整MQTT SSL测试..."
	@echo "📦 启动服务..."
	docker network inspect zxnet >/dev/null 2>&1 || docker network create zxnet
	docker compose -f docker-compose.rabbitmq.yml up -d
	@echo "⏳ 等待服务启动 (30秒)..."
	@sleep 30
	@echo "🧪 运行测试..."
	source ~/venv/bin/activate && python3 scripts/test_mqtt_ssl_simple.py
	@echo "✅ 测试完成"

mqtt-ssl: ## Start MQTT SSL proxy
	docker network inspect zxnet >/dev/null 2>&1 || docker network create zxnet
	docker compose -f docker-compose.rabbitmq.yml up -d

mqtt-ssl-down: ## Stop MQTT SSL proxy
	docker compose -f docker-compose.rabbitmq.yml down

mqtt-ssl-logs: ## View MQTT SSL proxy logs
	docker compose -f docker-compose.rabbitmq.yml logs -f mqtt-ssl-proxy
