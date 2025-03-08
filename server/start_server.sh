#!/bin/bash

# 进入项目根目录
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# 安装项目依赖
pip install -r requirements.txt

# 设置Python路径
export PYTHONPATH=$PROJECT_ROOT

# 进入server目录并启动服务
cd server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 