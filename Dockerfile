# Extend the official Rasa SDK image
FROM rasa/rasa-sdk:3.0.2

# Change back to root user to install dependencies
USER root

WORKDIR /app

# 设置国内pip镜像源
COPY pip.conf /root/.pip/pip.conf
# 拷贝依赖
COPY requirements.txt .

# 拷贝action
COPY ./actions /app/actions

RUN pip install --no-cache-dir -r requirements.txt


USER 1001
