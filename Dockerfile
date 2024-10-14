# app/Dockerfile
FROM python:3.11
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    cron \
    vim \
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

#Setup cron
COPY ./cronjob /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob
RUN touch ./data/cron.log
RUN ["chmod", "+x", "/app/pluggy_sync.py"]

EXPOSE 8501

CMD cron && tail -f /app/data/cron.log

#HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
#CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
