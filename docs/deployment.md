# HoneyTrap Production Deployment Guide

## Pre-Deployment Checklist

- [ ] PostgreSQL 14+ installed and running
- [ ] Redis 7+ installed and running
- [ ] Docker & Docker Compose 20.10+ installed
- [ ] SSL/TLS certificates obtained
- [ ] Domain name configured
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring tools configured

---

## Docker Compose Deployment

### 1. Prepare Server

```bash
# Update system
sudo apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create deploy user
sudo useradd -m -s /bin/bash honeytrap
```

### 2. Clone and Setup

```bash
# Clone repository
sudo -u honeytrap git clone https://github.com/yourusername/honeytrap.git /opt/honeytrap
cd /opt/honeytrap

# Copy and configure environment
sudo -u honeytrap cp .env.example .env
sudo -u honeytrap nano .env  # Edit configuration
```

### 3. Configure Environment (.env)

```env
# Flask
FLASK_ENV=production
SECRET_KEY=your-long-random-secret-key-here-min-32-chars

# PostgreSQL
POSTGRES_USER=honeytrap
POSTGRES_PASSWORD=very-strong-random-password
POSTGRES_DB=honeytrap

# Redis
REDIS_PASSWORD=your-redis-password

# Security
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# GeoIP
GEOIP_ENABLED=true
GEOIP_API_KEY=your_ipapi_key  # Optional

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 4. Start Services

```bash
# Pull latest images
docker-compose pull

# Start services in background
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f honey-app

# Initialize database
docker-compose exec honey-app flask db upgrade
docker-compose exec honey-app flask seed-db
```

### 5. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/honeytrap`:

```nginx
upstream honeytrap {
    server localhost:5000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Proxy settings
    proxy_buffering off;
    proxy_request_buffering off;
    client_max_body_size 10M;

    location / {
        proxy_pass http://honeytrap;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health/ {
        proxy_pass http://honeytrap;
        access_log off;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/honeytrap /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### 6. SSL Certificate with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx

sudo certbot certonly --nginx \
  -d yourdomain.com \
  -d www.yourdomain.com

# Auto-renewal setup
sudo systemctl enable certbot.timer
```

---

## Kubernetes Deployment

### Helm Chart Structure

```yaml
# helm/honeytrap/values.yaml
replicaCount: 3

image:
  repository: ghcr.io/yourusername/honeytrap
  tag: "1.0.0"
  pullPolicy: IfNotPresent

nameOverride: honeytrap
fullnameOverride: honeytrap

service:
  type: LoadBalancer
  port: 80
  targetPort: 5000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: honeytrap.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: honeytrap-tls
      hosts:
        - honeytrap.example.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

postgresql:
  enabled: true
  auth:
    password: "change-me"

redis:
  enabled: true
```

Deploy:

```bash
helm install honeytrap ./helm/honeytrap \
  -f values-production.yaml \
  -n honeytrap \
  --create-namespace
```

---

## Monitoring & Logging

### Prometheus Metrics

Add to `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  networks:
    - honeytrap-net
```

### ELK Stack Integration

```yaml
filebeat:
  image: docker.elastic.co/beats/filebeat:8.0.0
  volumes:
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
    - /var/run/docker.sock:/var/run/docker.sock:ro
```

### Log Rotation

```bash
# Setup logrotate for volumes
cat > /etc/logrotate.d/honeytrap <<EOF
/var/lib/docker/volumes/*/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 honeytrap honeytrap
}
EOF

sudo logrotate -f /etc/logrotate.d/honeytrap
```

---

## Backup Strategy

### Daily Backups

```bash
#!/bin/bash
# backup-honeytrap.sh

BACKUP_DIR="/backups/honeytrap"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec -T honey-db pg_dump \
  -U honeytrap honeytrap | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup volumes
tar -czf "$BACKUP_DIR/volumes_$DATE.tar.gz" \
  /var/lib/docker/volumes/honeytrap_pgdata/_data

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Schedule with cron:

```bash
0 2 * * * /opt/honeytrap/backup-honeytrap.sh
```

---

## Performance Tuning

### PostgreSQL

```sql
-- In postgresql.conf
max_connections = 200
shared_buffers = 512MB
effective_cache_size = 1GB
maintenance_work_mem = 256MB
work_mem = 4MB
```

### Redis

```conf
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Flask/Gunicorn

```bash
# Dockerfile CMD optimization
gunicorn -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --worker-class gevent \
  --worker-connections 1000 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  -b 0.0.0.0:5000 \
  run:app
```

---

## Security Hardening

```bash
# Restrict firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Fail2Ban setup
sudo apt-get install fail2ban
sudo systemctl start fail2ban

# SSH hardening
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Update regularly
sudo apt-get update && sudo apt-get upgrade -y
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Check connectivity
docker-compose exec honey-db psql -U honeytrap honeytrap -c "SELECT 1;"

# View logs
docker-compose logs honey-db
```

### Out of Disk Space

```bash
# Check disk usage
docker system df

# Clean up
docker system prune -a --volumes
```

### High Memory Usage

```bash
# Check memory limits
docker stats

# Adjust in docker-compose.yml
services:
  honey-app:
    mem_limit: 512m
    memswap_limit: 1g
```

---

## Scaling Strategy

1. **Vertical Scaling**: Increase server resources
2. **Horizontal Scaling**: Run multiple instances behind load balancer
3. **Database Scaling**: Read replicas, connection pooling
4. **Caching**: Redis for frequently accessed data

---

## Maintenance Windows

```bash
# Update images
docker-compose pull
docker-compose up -d

# Database maintenance
docker-compose exec honey-db \
  vacuumdb -U honeytrap honeytrap

# Check and repair
docker-compose exec honey-db \
  reindexdb -U honeytrap honeytrap
```

---

## Support & Monitoring

- Set up uptime monitoring: UptimeRobot, Statuspage
- Enable application metrics: Datadog, New Relic
- Log aggregation: ELK Stack, Graylog
- Alert on errors: Sentry, Rollbar

---

**Last Updated**: March 30, 2024
