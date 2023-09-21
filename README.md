# Distributed-Instant-Messager
Startup Instructions:
1. Install Docker and Python 3.x.x
2. Run `docker-compose up --build --scale chat-app=3`
    1. To add more, increase port range in `docker-compose.yml` and add more servers with added ports under chat-app upstream in `nginx/nginx.conf`
3. Run `python3 /chat-app/chat-client.py` two or more times in separate terminals

# Design Diagram:
![alt text](https://https://github.com/4040tee/Distributed-Instant-Messager/blob/main/Design%20Diagram.png?raw=true)