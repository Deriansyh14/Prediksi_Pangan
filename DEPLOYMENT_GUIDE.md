# 🚀 Panduan Deployment - Prediksi Harga Pangan

Panduan lengkap untuk deploy aplikasi ke berbagai platform.

## 📋 Daftar Isi

1. [Deployment ke Streamlit Cloud](#deployment-ke-streamlit-cloud)
2. [Deployment ke Heroku](#deployment-ke-heroku)
3. [Deployment ke PythonAnywhere](#deployment-ke-pythonanywhere)
4. [Deployment ke Server Own (Linux)](#deployment-ke-server-own)
5. [Deployment dengan Docker](#deployment-dengan-docker)
6. [Konfigurasi Domain Custom](#konfigurasi-domain-custom)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🌐 Deployment ke Streamlit Cloud

**Platform Rekomendasi** - Paling mudah & gratis untuk startup

### Prasyarat
- GitHub account
- Streamlit Cloud account (gratis)

### Langkah-Langkah

1. **Push ke GitHub**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Buka Streamlit Cloud**
   - URL: https://streamlit.io/cloud
   - Login dengan GitHub account

3. **Create New App**
   - Click "New app" → "From existing repo"
   - Repository: `sains-data/Stokastik_4_RB`
   - Branch: `main`
   - Main file path: `app.py`

4. **Deploy**
   - Click "Deploy" → Tunggu proses build
   - Aplikasi live dalam 2-5 menit

5. **Hasil**
   - URL: `https://your-app-name.streamlit.app`
   - Otomatis update saat push ke GitHub

### Tips
- Max 3 app gratis per akun
- CPU: 1 core, Memory: 512MB
- Cocok untuk demo & small production

---

## 🔴 Deployment ke Heroku

**Platform Alternatif** - Full control, memerlukan card kredit

### Prasyarat
- Heroku account (dengan payment method)
- Heroku CLI installed

### Langkah-Langkah

1. **Login ke Heroku**
```bash
heroku login
```

2. **Create App**
```bash
heroku create your-app-name
```

3. **Set Buildpack**
```bash
heroku buildpacks:set heroku/python
```

4. **Buat Procfile** (jika belum ada)
```
web: streamlit run --server.port=$PORT --server.address=0.0.0.0 app.py
```

5. **Setup Config**
```bash
heroku config:set STREAMLIT_SERVER_HEADLESS=true
heroku config:set STREAMLIT_SERVER_PORT=$PORT
heroku config:set STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

6. **Deploy**
```bash
git push heroku main
```

7. **Monitor**
```bash
heroku logs --tail
heroku open
```

### Tips
- Free tier sudah deprecated (perlu payment)
- CPU: 0.5x dyno, Memory: 512MB
- Restart harian otomatis

---

## 🐍 Deployment ke PythonAnywhere

**Platform Beginner-Friendly** - Uptime tinggi, support Python native

### Prasyarat
- PythonAnywhere account (free available)
- Domain atau subdomain pythonanywhere.com

### Langkah-Langkah

1. **Upload Repository**
   - Buka PythonAnywhere Dashboard
   - Console → Bash
```bash
git clone https://github.com/sains-data/Stokastik_4_RB.git
cd Stokastik_4_RB
```

2. **Setup Virtual Environment**
```bash
mkvirtualenv --python=/usr/bin/python3.10 pangan
pip install -r requirements.txt
```

3. **Create WSGI File**
   - Web → Add a new web app → Manual config → Python 3.10
   - Edit WSGI file:
```python
import sys
import os
path = '/home/username/Stokastik_4_RB'
if path not in sys.path:
    sys.path.append(path)

# Streamlit tidak kompatibel dengan WSGI
# Gunakan setup berikut di task scheduler
```

4. **Scheduled Task (Alternative)**
   - Tasks → Create new scheduled task
   - Waktu: Daily, misalnya 00:00
   - Command:
```bash
cd /home/username/Stokastik_4_RB
/home/username/.virtualenvs/pangan/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
```

5. **Konfigurasi**
   - Web → Domain: `username.pythonanywhere.com`
   - Setup custom domain di DNS settings

### Tips
- Free tier: 100MB storage, 1 CPU
- Paid: $5/month, unlimited resources
- Uptime: 99.9% guaranteed (paid)

---

## 💻 Deployment ke Server Own (Linux/Ubuntu)

**Full Control** - Self-hosted, maintenance sendiri

### Prasyarat
- Linux server (Ubuntu 20.04+)
- Python 3.10+
- SSH access

### Instalasi

1. **SSH ke Server**
```bash
ssh user@your-ip
```

2. **Install Dependencies**
```bash
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-venv python3-pip

# Install system packages
sudo apt-get install -y libpq-dev build-essential
```

3. **Clone Repository**
```bash
cd /opt
sudo git clone https://github.com/sains-data/Stokastik_4_RB.git
sudo chown -R $USER:$USER Stokastik_4_RB
cd Stokastik_4_RB
```

4. **Setup Virtual Environment**
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Test Aplikasi**
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
# Akses: http://your-ip:8501
```

6. **Setup Systemd Service** (Persistent)

Create `/etc/systemd/system/streamlit-pangan.service`:
```ini
[Unit]
Description=Streamlit Prediksi Pangan
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/opt/Stokastik_4_RB
Environment="PATH=/opt/Stokastik_4_RB/venv/bin"
ExecStart=/opt/Stokastik_4_RB/venv/bin/streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

7. **Enable & Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit-pangan
sudo systemctl start streamlit-pangan

# Monitor
sudo systemctl status streamlit-pangan
sudo journalctl -u streamlit-pangan -f
```

8. **Setup Nginx Reverse Proxy**

Create `/etc/nginx/sites-available/pangan`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/pangan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

9. **Setup SSL (Let's Encrypt)**
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Tips
- CPU: Depends on server
- Storage: Minimal 2GB untuk dataset
- Memory: 2GB recommended
- Monitoring: Setup Uptime monitoring

---

## 🐳 Deployment dengan Docker

**Containerized** - Mudah scale & replicate

### Build Docker Image

1. **Create Dockerfile** (jika belum ada)
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run app
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

2. **Build Image**
```bash
docker build -t pangan:latest .
```

3. **Test Local**
```bash
docker run -p 8501:8501 pangan:latest
# Akses: http://localhost:8501
```

4. **Push ke Docker Hub**
```bash
docker tag pangan:latest username/pangan:latest
docker login
docker push username/pangan:latest
```

### Deploy ke Cloud Platform

**Dengan Docker Compose:**
```yaml
version: '3.8'

services:
  pangan:
    image: username/pangan:latest
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    volumes:
      - ./models:/app/models
    restart: always
```

```bash
docker-compose up -d
```

**Deployment Platforms yang support Docker:**
- Railway.app
- Render.com
- Fly.io
- DigitalOcean (App Platform)
- AWS (ECS, EKB)

---

## 🔗 Konfigurasi Domain Custom

### Streamlit Cloud
1. Settings → Custom domain
2. Arahkan DNS CNAME ke `custom-domain.streamlit.app`

### Self-Hosted dengan Nginx
1. Beli domain (GoDaddy, Namecheap, dll)
2. Arahkan DNS A record ke server IP
3. Setup SSL dengan Let's Encrypt (see above)

### CloudFlare (Free CDN)
1. Add domain ke CloudFlare
2. Setup DNS records pointing to your server
3. Enable SSL (Free tier available)
4. CDN cache untuk static assets

---

## 📊 Monitoring & Maintenance

### Monitoring Uptime
- **Free:** Uptime Robot (uptime-robot.com)
- **Paid:** Datadog, New Relic, Sentry

### Backup Data
```bash
# Backup database & models
0 2 * * * /home/user/backup.sh

# backup.sh
#!/bin/bash
tar -czf /backup/pangan-$(date +%Y%m%d).tar.gz \
    /opt/Stokastik_4_RB/models \
    /opt/Stokastik_4_RB/data
```

### Update Dependencies
```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Test
streamlit run app.py
```

### Logs
```bash
# Systemd
journalctl -u streamlit-pangan -n 100 -f

# Docker
docker logs container-id -f

# Application
tail -f /var/log/streamlit-pangan.log
```

### Performance Tuning
- Max upload size: `.streamlit/config.toml`
- Cache settings: `@st.cache_data`
- Optimize model loading: Load once per session

---

## ✅ Checklist Pre-Deployment

- [ ] All tests passing
- [ ] Requirements.txt updated
- [ ] No hardcoded credentials
- [ ] .gitignore proper
- [ ] README.md complete
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Database/storage path correct
- [ ] Environment variables set
- [ ] SSL certificate ready (if custom domain)
- [ ] Monitoring setup
- [ ] Backup strategy ready

---

## 🆘 Troubleshooting Deployment

### App tidak bisa diakses
```bash
# Check service status
systemctl status streamlit-pangan

# Check logs
journalctl -u streamlit-pangan -n 50

# Check port
netstat -tlnp | grep 8501
```

### Memory leak
```bash
# Restart service
systemctl restart streamlit-pangan

# Monitor memory
free -h
# atau
watch -n 5 free -h
```

### Data tidak tersimpan
- Check model folder permissions
- Verify path dalam config
- Check disk space: `df -h`

### Slow performance
- Check CPU: `top`
- Check disk I/O: `iostat`
- Optimize queries/cache
- Scale resources

---

**Last Updated:** December 2025
**Version:** 1.0
