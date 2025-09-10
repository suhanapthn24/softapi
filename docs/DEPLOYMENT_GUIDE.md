# Deployment Guide (for generated apps)

You have two production-ready options:

- **Docker (simple, portable)**
- **EC2 + Nginx + systemd (classic server)**

---

## A) Docker

Create these files in your app root:

**Dockerfile**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY app /app/app
COPY .env /app/.env
EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "app.main:app"]
```

**docker-compose.yml**
```yaml
version: "3.9"
services:
  softapi:
    build: .
    container_name: softapi
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

**.env (production)**
```env
SECRET_KEY="change-me-in-prod"
DB_URL="sqlite:///./app.db"
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

Run:
```bash
docker compose up -d --build
docker compose logs -f
```

---

## B) AWS EC2 + Nginx + systemd

**Server prep**
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip nginx
sudo ufw allow 'Nginx Full' || true
```

**App setup**
```bash
sudo mkdir -p /opt/softapi
sudo chown -R $USER:$USER /opt/softapi
# copy project into /opt/softapi
cd /opt/softapi
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit secrets
```

**systemd service** `/etc/systemd/system/softapi.service`
```
[Unit]
Description=softapi FastAPI service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/softapi
Environment="PATH=/opt/softapi/.venv/bin"
ExecStart=/opt/softapi/.venv/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000 app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```
Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable softapi
sudo systemctl start softapi
sudo systemctl status softapi
```

**Nginx site** `/etc/nginx/sites-available/softapi`
```
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```
Enable:
```bash
sudo ln -s /etc/nginx/sites-available/softapi /etc/nginx/sites-enabled/softapi
sudo nginx -t && sudo systemctl reload nginx
```

**HTTPS**
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**Checks**
```bash
curl http://localhost/health
```