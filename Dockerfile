# app/Dockerfile
FROM python:3.11
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    cron \
    git \
    && rm -rf /var/lib/apt/lists/*

# RUN git clone https://github.com/tcpr1/actual-pluggy-py .
COPY . .
RUN pip3 install -r requirements.txt

ARG USERNAME=actual
ARG USER_UID=1001
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME
RUN mkdir -p /app/data/Backup && chown -R ${USERNAME}:${USERNAME} /app/data/Backup
WORKDIR /app

# Adiciona a configuração do Cron
RUN echo "0 5 * * * python /app/pluggy_sync.py > /app/data/cron_log.txt" >> /etc/crontab

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
