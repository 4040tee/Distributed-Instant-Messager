FROM python:latest
ENV MYSQL_PASSWORD=pass
WORKDIR /usr/src/chat-app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
STOPSIGNAL SIGKILL
ENTRYPOINT ["python3", "-u", "chat_server.py"]