.PHONY: dev lint format test clean

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
