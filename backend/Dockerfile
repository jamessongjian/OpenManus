FROM python:3.12-slim

WORKDIR /app

# 设置Python路径
ENV PYTHONPATH=/app:$PYTHONPATH

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有必要文件
COPY . .

# 安装项目包
RUN pip install -e .

EXPOSE 8000

# 使用正确的模块路径启动服务
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 