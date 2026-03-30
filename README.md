# 🍯 HoneyTrap

**Professional Honeypot Intrusion Detection System**

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)

---

## 📋 Overview

HoneyTrap is an enterprise-grade honeypot application that simulates vulnerable services to detect, log, and analyze malicious intrusion attempts in real-time. Designed for security teams and researchers.

### Key Capabilities

| Feature | Details |
|---------|---------|
| 🎯 **Honeypot Services** | SSH, FTP, WordPress Admin, phpMyAdmin simulations |
| 🌍 **Geolocation** | IP enrichment with country, city, ISP data |
| 🔍 **Attack Classification** | Automatic TTPs detection: SQLi, XSS, Brute-Force, Scans |
| 🛡️ **Rate Limiting** | DDoS protection via Redis-backed rate limiting |
| 📊 **Real-time Dashboard** | Live charts, metrics, and attack visualization |
| 📤 **Export Capabilities** | CSV/JSON export for SIEM integration |
| 🐳 **Container Native** | Multi-container orchestration with Docker Compose |
| 🔍 **Monitoring** | Health checks, metrics, structured logging |
| 🧪 **Production Ready** | CI/CD, comprehensive tests, security hardening |

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** 20.10+
- **OR** Python 3.10+, PostgreSQL 14+, Redis 7+

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/honeytrap.git
cd honeytrap

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Database initialization (first run)
docker-compose exec honey-app flask db upgrade
docker-compose exec honey-app flask seed-db

# Access application
open http://localhost:5000
```

### Option 2: Local Development

```bash
# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
flask db upgrade
flask seed-db

# Run development server
flask run --debug
# Visit http://localhost:5000
```

---

## 📚 Documentation

| Resource | Description |
|----------|-------------|
| [API Documentation](docs/api.md) | Complete REST API reference |
| [Architecture Guide](docs/architecture.md) | System design and components |
| [User Guide](docs/user-guide.md) | Dashboard and feature usage |
| [Deployment Guide](docs/deployment.md) | Production deployment best practices |
| [Contributing](CONTRIBUTING.md) | Development guidelines |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│         Browser / Security Dashboard                │
│         http://localhost:5000                       │
└────────────────┬────────────────────────────────────┘
                 │ HTTP Requests
                 ▼
┌─────────────────────────────────────────────────────┐
│   honeytrap-app (Flask + Gunicorn)                  │
│   ├── Dashboard (HTML Templates)                    │
│   ├── API Routes (/api/*)                           │
│   ├── Honeypot Services (/fake/*)                   │
│   ├── GeoIP Lookup                                  │
│   └── Attack Classification                         │
└────────┬──────────────────────────────┬─────────────┘
         │ SQL Queries                  │ Cache/Rate Limit
         ▼                              ▼
    ┌─────────────────┐        ┌──────────────────┐
    │ PostgreSQL 16   │        │   Redis 7        │
    │ honeytrap_db    │        │ Rate Limiter     │
    │ (Attacks Table) │        │ (Session Cache)  │
    └─────────────────┘        └──────────────────┘
```

---

## 📖 API Examples

### Get Recent Attacks

```bash
curl -X GET http://localhost:5000/api/attacks?limit=10&offset=0

# Response:
{
  "total": 156,
  "limit": 10,
  "offset": 0,
  "attacks": [
    {
      "id": 156,
      "ip_address": "192.168.1.100",
      "country": "United States",
      "attack_type": "brute_force",
      "severity": "high",
      "timestamp": "2024-03-30T12:34:56"
    }
  ]
}
```

### Get Statistics

```bash
curl -X GET http://localhost:5000/api/stats

# Response:
{
  "total_attacks": 156,
  "total_blocked_ips": 23,
  "by_type": {
    "sqli": 45,
    "xss": 32,
    "brute_force": 41,
    "scan": 38
  },
  "by_severity": {
    "high": 78,
    "medium": 56,
    "low": 22
  }
}
```

### Health Check

```bash
curl -X GET http://localhost:5000/health/

# Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "healthy",
  "checks": {
    "database": true,
    "api": true
  }
}
```

---

## 🔧 Configuration

### Environment Variables

```env
# Flask
FLASK_ENV=production
SECRET_KEY=your-long-random-secret-key

# Database
POSTGRES_USER=honeytrap
POSTGRES_PASSWORD=strongpassword123
POSTGRES_DB=honeytrap
DATABASE_URL=postgresql://honeytrap:password@honey-db:5432/honeytrap

# Redis
REDIS_URL=redis://honey-redis:6379/0

# Honeypot
BLOCK_THRESHOLD=10              # Block IP after N attacks
RATE_LIMIT="20 per minute"      # Rate limiting
GEOIP_ENABLED=true              # Enable IP geolocation
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
```

See `.env.example` for complete configuration options.

---

## 💻 Development

### Development Commands

```bash
# Using Makefile (recommended)
make help              # Show all commands
make install          # Install dependencies
make dev              # Setup dev environment
make run              # Run development server
make test             # Run tests
make lint             # Check code quality
make format           # Format code with Black

# Using Flask CLI
flask run --debug
flask db upgrade      # Apply migrations
flask seed-db        # Populate test data
flask init-db        # Initialize database
```

### Code Quality

Project enforces professional code standards:

- **Format**: Black (100 char line length)
- **Linting**: Flake8, Pylint
- **Type Checking**: mypy
- **Tests**: pytest with >80% coverage
- **Pre-commit**: Type hints required

Run all checks:

```bash
make lint              # Lint code
black app              # Format code
pytest --cov=app      # Run tests with coverage
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html

# Run specific test
pytest tests/test_api.py::test_get_attacks -v

# Run with markers
pytest -m "not slow"
```

---

## 🐳 Docker Operations

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f honey-app

# Execute command in container
docker-compose exec honey-app flask db upgrade

# Stop services
docker-compose down

# Clean everything (data included)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache
```

---

## 📊 Monitoring & Metrics

### Health Check Endpoints

- `GET /health/` - Full health check
- `GET /health/readiness` - Kubernetes readiness probe
- `GET /health/liveness` - Kubernetes liveness probe
- `GET /health/stats` - Application statistics

### Structured Logging

All logs are in JSON format for easy SIEM integration:

```json
{
  "timestamp": "2024-03-30T12:34:56.789Z",
  "level": "INFO",
  "logger": "app.routes.honeypot",
  "message": "Attack detected: SQLi on phpmyadmin",
  "module": "honeypot",
  "function": "fake_phpmyadmin",
  "line": 45
}
```

---

## 🔐 Security

### Features

- ✅ CSRF protection on forms
- ✅ SQL injection prevention via ORM parameterization
- ✅ XSS protection with template escaping
- ✅ Rate limiting (20 requests/minute per IP)
- ✅ Non-root container execution
- ✅ HTTPS ready (headers configured)
- ✅ CORS properly configured
- ✅ Input validation on all endpoints

### Reporting Security Issues

🚨 **Do NOT open public issues for security vulnerabilities.**

Email: `security@aymei-tech.com` with:
- Description of vulnerability
- Impact assessment
- Reproduction steps

---

## 📈 Performance

- **Honeypot Services**: <100ms response time
- **API Endpoints**: <200ms average (with GeoIP)
- **Dashboard**: <500ms data load
- **Rate Limiting**: Redis-backed (instant)
- **Concurrent Connections**: 100+ simultaneous

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code style guidelines
- Git workflow
- Testing requirements
- Pull request process

Quick start:

```bash
git checkout -b feature/your-feature
make dev
make lint
make test
git commit -m "feat: description"
git push origin feature/your-feature
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 👨‍💻 Author

**Manny** | AYMEI TECH

- Website: https://aymei-tech.com
- Email: dev@aymei-tech.com
- GitHub: [@yourusername](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Flask and SQLAlchemy communities
- Security research community
- Contributors and testers

---

## 📞 Support

- 📧 **Email**: dev@aymei-tech.com
- 💬 **Discussions**: GitHub Discussions
- 🐛 **Issues**: GitHub Issues
- 📖 **Documentation**: https://honeytrap.readthedocs.io

---

## 🗺️ Roadmap

- [ ] ML-based attack pattern detection
- [ ] Shodan API integration
- [ ] Slack/Telegram notifications
- [ ] Advanced analytics dashboard
- [ ] Kubernetes deployment guide
- [ ] Ansible deployment playbooks

---

**Made with ❤️ for the security community**

### Prérequis
- Docker + Docker Compose
- Git

### 1. Cloner le projet
```bash
git clone https://github.com/VOTRE_USER/honeytrap.git
cd honeytrap
```

### 2. Configurer l'environnement
```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

### 3. Lancer avec Docker Compose
```bash
docker-compose up --build
```

### 4. Accéder à l'application
- **Dashboard** : http://localhost:5000
- **API** : http://localhost:5000/api/attacks
- **Leurres** : http://localhost:5000/fake/ssh

---

## 🧪 Tests

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer les tests
pytest tests/ -v
```

Tests couverts :
- `test_routes.py` — Toutes les routes Flask (GET/POST)
- `test_classifier.py` — Classifieur d'attaques (SQLi, XSS, scan, brute-force, bots)

---

## 📡 API REST

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/attacks` | GET | Liste des attaques (JSON) |
| `/api/stats` | GET | Statistiques globales |
| `/api/top-ips` | GET | Top 10 IPs attaquantes |
| `/api/blocked-ips` | GET | IPs bloquées |
| `/export/csv` | GET | Export CSV complet |
| `/export/json` | GET | Export JSON complet |

---

## 🌐 Services Leurres

| Route | Service simulé | Cible |
|---|---|---|
| `/fake/ssh` | Terminal SSH Linux | Scanners automatiques |
| `/fake/ftp` | FileZilla FTP Server | Accès fichiers |
| `/fake/admin` | WordPress Admin | Brute-force CMS |
| `/fake/phpmyadmin` | phpMyAdmin 4.9 | Attaques SQL |

---

## 🗄 Modèle de données

**Table `attacks`** — Cœur du système  
`id · ip_address · country · city · isp · attack_type · target_service · payload · user_agent · timestamp · severity`

**Table `blocked_ips`** — IPs bannies automatiquement  
**Table `attack_stats`** — Agrégats horaires pour graphiques

---

## ⚙️ Variables d'environnement

Voir `.env.example` pour la liste complète.

| Variable | Description |
|---|---|
| `DATABASE_URL` | URL PostgreSQL |
| `REDIS_URL` | URL Redis |
| `BLOCK_THRESHOLD` | Nb attaques avant blocage (défaut: 10) |
| `GEOIP_ENABLED` | Activer la géoloc (défaut: true) |

---

## 🔄 CI/CD

Pipeline GitHub Actions (`.github/workflows/ci-cd.yml`) :

```
Push main → Tests pytest → Build Docker → Push Docker Hub
```

**Secrets GitHub à configurer :**
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

---

## 📦 Technologies utilisées

| Composant | Technologie |
|---|---|
| Backend | Flask 3.x, Python 3.11 |
| Base de données | PostgreSQL 16 |
| Cache / Rate Limit | Redis 7 |
| ORM | Flask-SQLAlchemy + Flask-Migrate |
| Géolocalisation | ip-api.com (gratuit, sans clé) |
| Frontend | Jinja2, Chart.js, CSS Grid |
| Conteneurisation | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Tests | pytest, pytest-flask |
| Production | Gunicorn WSGI |

---

## 👨‍💻 Auteur

**Manny** — L3 Réseaux & Informatique — ISI Keur Massar  
Marque : **AYMEI TECH** | Projet : DEVNET Examen Final 2025

---

*"Un attaquant qui entre dans un honeypot nous apprend plus qu'une alerte qui nous dit qu'il est là."*
