# 基础镜像:Python 3.10 轻量版
FROM python:3.10-slim
  
WORKDIR /app

# 先复制 pyproject + 装依赖(利用缓存:代码改了依赖不用重装)
COPY pyproject.toml .
RUN pip install --no-cache-dir .
  
# 再复制代码
COPY app/ ./app/
  
EXPOSE 8000

# 默认启动 API(Worker 用 command 覆盖)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
