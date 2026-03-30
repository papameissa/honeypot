# HoneyTrap Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User/Attacker                            │
│                   Internet Traffic (HTTP/TCP)                   │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                     ▼
          ┌──────────────────┐   ┌─────────────────┐
          │  Nginx/Reverse   │   │ Direct Honeypot │
          │  Proxy (443/80)  │   │   Ports (22,   │
          └────────┬─────────┘   │   21, 3306..)  │
                   │              └─────────┬────────┘
                   └────────────┬───────────┘
                                │
                    ┌───────────▼────────────┐
                    │  honeytrap-app        │
                    │  (Flask + Gunicorn)   │
                    │  - Dashboard Routes   │
                    │  - API Routes         │
                    │  - Honeypot Services  │
                    │  - GeoIP Lookup       │
                    │  - Classifier        │
                    │  - Logger/Exporter   │
                    └──────────┬──────┬─────┘
                               │      │
                ┌──────────────┘      └──────────────┐
                ▼                                    ▼
         ┌──────────────┐                    ┌───────────────┐
         │ PostgreSQL   │                    │  Redis 7      │
         │ (honey-db)   │                    │  (honey-redis)│
         │ - Attacks    │                    │ - Rate Limit  │
         │ - Blocked IPs│                    │ - Sessions    │
         │ - Stats      │                    │ - Cache       │
         └──────────────┘                    └───────────────┘
```

---

## Component Architecture

### 1. Flask Application (`honeytrap-app`)

#### Entry Point
- **File**: `run.py`
- **Factory**: `app/__init__.py` → `create_app()`
- **Server**: Gunicorn (4 workers, 2 threads each)

#### Core Components

**Routes** (`app/routes/`)
```
├── dashboard.py      # Main dashboard page
├── honeypot.py       # Fake services (/fake/*)
├── api.py            # REST API (/api/*)
├── export.py         # Export routes (/export/*)
└── health.py         # Health checks (/health/*)
```

**Models** (`app/models.py`)
- `Attack` - Individual intrusion attempts
- `BlockedIP` - Blocked IP addresses
- `AttackStat` - Aggregated statistics

**utilities** (`app/utils/`)
```
├── classifier.py    # Attack type detection (SQLi, XSS, etc.)
├── exporter.py      # CSV/JSON export functionality
├── geoip.py         # IP geolocation using ip-api.com
└── logger.py        # Structured JSON logging
```

**Extensions** (`app/extensions.py`)
- SQLAlchemy ORM
- Flask-Limiter (rate limiting)
- Flask-Migrate (database migrations)
- Flask-CORS (cross-origin requests)

#### Security Features
- CORS with origin validation
- CSRF protection on forms
- Input validation on all endpoints
- SQL injection prevention via ORM
- Rate limiting (20 req/min per IP)
- Security headers (CSP, X-Frame-Options, etc.)
- Non-root container execution

---

### 2. Database Layer (`honey-db`)

#### PostgreSQL 16

**Schema:**
```sql
-- Attacks: Store individual intrusion attempts
attacks (
    id INT PRIMARY KEY,
    ip_address VARCHAR(45),
    attack_type VARCHAR(50),     -- INDEXED
    target_service VARCHAR(50),
    severity VARCHAR(10),        -- INDEXED
    timestamp DATETIME,          -- INDEXED
    payload TEXT,
    user_agent TEXT,
    country VARCHAR(100),
    city VARCHAR(100),
    isp VARCHAR(200)
)

-- Blocked IPs: Track blocklisted addresses
blocked_ips (
    id INT PRIMARY KEY,
    ip_address VARCHAR(45) UNIQUE,
    reason VARCHAR(200),
    blocked_at DATETIME
)

-- Statistics: Aggregated attack counts
attack_stats (
    id INT PRIMARY KEY,
    attack_type VARCHAR(50),
    count INT,
    severity VARCHAR(10),
    updated_at DATETIME
)
```

**Indexes Strategy:**
- `ip_address` - For IP lookups and blocking
- `attack_type` - For type distribution queries
- `severity` - For severity filtering
- `timestamp` - For time-range queries

**Partitioning** (Optional for production):
```sql
PARTITION BY RANGE (YEAR(timestamp))
```

---

### 3. Caching Layer (`honey-redis`)

#### Redis 7 Use Cases

| Use Case | Key Pattern | TTL | Purpose |
|----------|-------------|-----|---------|
| Rate Limiting | `rate_limit:{ip}` | 60s | Per-IP request counts |
| Session Cache | `session:{sid}` | 1h | User session storage |
| GeoIP Cache | `geoip:{ip}` | 7d | Cached location lookups |
| Stats Cache | `stats:hourly` | 5m | Dashboard chart data |
| Blacklist | `blocked:{ip}` | 24h | In-memory IP blocklist |

---

### 4. External Services

#### IP Geolocation (`ip-api.com`)
```python
# Request
GET https://ip-api.com/json/{ip_address}

# Response
{
    "status": "success",
    "country": "United States",
    "city": "Los Angeles",
    "isp": "Verizon Communications",
    "lat": 34.0522,
    "lon": -118.2437
}
```

#### Alternative: MaxMind GeoIP2
```python
# For production: Self-hosted MaxMind database
from geoip2.database import Reader
reader = Reader('GeoLite2-City.mmdb')
response = reader.city('192.168.1.1')
```

---

## Data Flow

### Attack Detection Flow

```
Attacker Request (SSH/FTP/HTTP)
        │
        ▼
┌──────────────────────────────────┐
│ honeypot_bp.fake_service()       │
│ - Log request details            │
├──────────────────────────────────┤
│ classifier.detect_attack()       │
│ - Analyze payload                │
│ - Determine attack type          │
│ - Calculate severity             │
├──────────────────────────────────┤
│ geoip.lookup_ip()                │
│ - Reverse DNS lookup (Redis)     │
│ - Fetch from ip-api.com if miss  │
│ - Cache for 7 days               │
├──────────────────────────────────┤
│ logger.log_attack()              │
│ - Create Attack DB record        │
│ - Output JSON to stdout          │
│ - Alert if severity=high         │
├──────────────────────────────────┤
│ Check IP blocklist (Redis)       │
│ IF blocked_count > 10:           │
│   - Add to blocked_ips table     │
│   - Cache in Redis               │
│ RETURN: Honeypot response        │
└──────────────────────────────────┘
        │
        ▼
 Fake Service Response
 (SSH prompt, FTP listing, etc.)
```

### Dashboard Flow

```
User → Browser:5000/
        │
        ▼
┌──────────────────────────────────┐
│ dashboard_bp.index()             │
├──────────────────────────────────┤
│ Query Database:                  │
│ - Count total attacks            │
│ - Get top 5 attacking IPs        │
│ - Recent 20 attacks              │
│ - Attack type distribution       │
│ - Severity distribution          │
├──────────────────────────────────┤
│ Convert to JSON-serializable:    │
│ - SQLAlchemy Row → Dict          │
│ - Format timestamps              │
├──────────────────────────────────┤
│ Render dashboard.html            │
│ + Inject data as JavaScript      │
└──────────────────────────────────┘
        │
        ▼
 Rendered HTML + Charts.js
```

---

## Deployment Architecture

### Docker Compose Topology

```
┌─────────────────────────────────────────────┐
│        Docker Bridge Network                │
│        (honeytrap-net)                      │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐  ┌──────────┐  ┌──────────┐
│  │ honeytrap-   │  │ honey-   │  │ honey-   │
│  │ app:5000     │  │ db:5432  │  │ redis    │
│  │              │  │          │  │ :6379    │
│  │ Service 1    │  │ PG 16    │  │ Redis 7  │
│  └──────┬───────┘  └────┬─────┘  └────┬─────┘
│         │               │             │
│         └───────────────┼─────────────┘
│                         │
│  Volumes:              │
│  - logs/           ────┘
│  - uploads/
│  - pgdata/
│  - redisdata/
│                         │
└─────────────────────────┼─────────────────────┘
          │
          └─ Host Port Mapping
             - 5000:5000 (Flask app)
```

### Kubernetes Deployment

```
┌────────────────────────────────────────────┐
│         Kubernetes Cluster                 │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────── Honeytrap Namespace ──────┐   │
│  │                                   │   │
│  │  Pod 1          Pod 2      Pod 3  │   │
│  │  ┌────────┐   ┌────────┐  ┌────────┐  │
│  │  │ Flask  │   │ Flask  │  │ Flask  │  │
│  │  │ App    │   │ App    │  │ App    │  │
│  │  └───┬────┘   └───┬────┘  └───┬────┘  │
│  │      │            │           │      │
│  │      └────────────┬───────────┘      │
│  │                   │                  │
│  │          Service (Load Balancer)     │
│  │                   │                  │
│  └───────────────────┼──────────────────┘
│                      │
│  ┌──────────────────┴──────────────────┐
│  │                                     │
│  │  ┌──────────┐        ┌──────────┐  │
│  │  │PostgreSQL│        │ Redis    │  │
│  │  │ StatefulSet      │Deployment  │  │
│  │  └──────────┘        └──────────┘  │
│  │                                     │
│  └─────────────────────────────────────┘
│
└────────────────────────────────────────────┘
  Ingress (HTTPS) → Service → Pods
```

---

## Performance Characteristics

### Response Times (Typical)

| Operation | Latency | Notes |
|-----------|---------|-------|
| Honeypot Response | 50-100ms | Simulated service response |
| Dashboard Load | 200-500ms | Includes 4 DB queries |
| API /attacks | 100-300ms | Depends on limit param |
| API /stats | 150-400ms | Aggregation query |
| GeoIP Lookup | 200-800ms | First hit from API, cached after |
| Rate Limit Check | <1ms | Redis in-memory |

### Scalability

- **Concurrent Users**: 100+ with current setup
- **Horizontal Scaling**: Add Flask pods behind load balancer
- **Database Scaling**: Read replicas, connection pooling
- **Caching**: Redis for hot data
- **CDN**: Static files (CSS, JS) via CloudFront/Cloudflare

---

## Security Architecture

### Threat Model

| Threat | Mitigation | Component |
|--------|-----------|-----------|
| SQL Injection | SQLAlchemy ORM parameterization | Database Layer |
| XSS | Template auto-escaping (Jinja2) | Frontend |
| CSRF | CSRF tokens on forms | Flask-Talisman |
| DDoS | Rate limiting (Redis) + WAF | Rate Limiter |
| Unauthorized Access | CORS validation, auth headers | Flask App |
| Data Breach | Encryption at rest (TLS), access logs | Infrastructure |
| Code Injection | No eval(), secure imports | Python SAST |

### Authentication Strategy (Future)

```python
# Optional: Add API Key or JWT
@auth_bp.route('/api/v2/attacks')
@require_api_key
def get_attacks():
    pass

# Or use Bearer tokens
@auth_bp.route('/api/v2/attacks')
@require_bearer_token
def get_attacks():
    pass
```

---

## Monitoring & Observability

### Metrics Collected

- Request count/latency (per endpoint)
- Error rates (4xx, 5xx)
- Database query duration
- Active connections
- Cache hit ratio
- Attack patterns (type distribution)

### Logging

```json
{
  "timestamp": "2024-03-30T12:34:56Z",
  "level": "INFO",
  "logger": "app.routes.honeypot",
  "message": "Attack detected",
  "request_id": "abc-123",
  "ip_address": "192.168.1.1",
  "attack_type": "sqli",
  "severity": "high"
}
```

### Health Checks

- `/health/` - Full health check
- `/health/readiness` - K8s readiness
- `/health/liveness` - K8s liveness
- Database connectivity test
- Redis connectivity test

---

## Disaster Recovery

### Backup Strategy

1. **Database**: Daily snapshots (pgBackRest)
2. **Volumes**: File-based backups (tar + gzip)
3. **Retention**: 30 days minimum
4. **Verification**: Weekly restore tests

### Recovery Time Objectives (RTO)

- **Database Failure**: <5 minutes (standby promotion)
- **App Crash**: <1 minute (container restart)
- **Full Cluster**: <30 minutes (from backup)

---

**Last Updated**: March 30, 2024
