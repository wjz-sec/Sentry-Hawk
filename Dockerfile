FROM python:3.10

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 创建非 root 用户
RUN useradd -ms /bin/bash appuser
USER appuser

# 设置工作目录
WORKDIR /app

# 复制并安装依赖
COPY --chown=appuser:appuser requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件
COPY --chown=appuser:appuser . /app/

# 暴露端口
EXPOSE 8000


# 启动命令
CMD ["sh", "-c", "python ./manage.py makemigrations && python ./manage.py migrate && python ./manage.py runserver 0.0.0.0:8000"]