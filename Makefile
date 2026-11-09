.PHONY: dev lint format test clean dev-frontend build-frontend lint-frontend test-frontend frontend-up frontend-down

dev: ## 建虚拟环境 + 装全部依赖
	cd backend && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

lint: ## 代码规范检查
	cd backend && .venv/bin/ruff check app tests

format: ## 自动格式化 + 修能修的问题
	cd backend && .venv/bin/ruff format app tests && .venv/bin/ruff check --fix app tests

test: ## 跑测试
	cd backend && .venv/bin/python -m pytest -q

clean: ## 清理缓存和虚拟环境
	cd backend && rm -rf .venv .pytest_cache && find . -name "__pycache__" -type d -exec rm -rf {} +

dev-frontend: ## 启动前端开发服务器
	cd frontend && npm install && npm run dev

build-frontend: ## 构建前端生产产物
	cd frontend && npm ci && npm run build

lint-frontend: ## 前端代码规范检查
	cd frontend && npm run lint

test-frontend: ## 前端单测
	cd frontend && npm run test

frontend-up: ## docker 构建 + 启动前端(nginx)
	docker compose up -d --build frontend

frontend-down: ## 停止前端容器
	docker compose down frontend
