# HoneyTrap API Documentation

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, no authentication is required. In production, add:
- API Key in header: `X-API-Key: your-key`
- JWT Bearer token

## Response Format

All responses are JSON with standard structure:

```json
{
  "status": "success|error",
  "data": {},
  "timestamp": "2024-03-30T12:34:56Z"
}
```

---

## Endpoints

### Attacks

#### Get Attacks List

```http
GET /api/attacks?limit=50&offset=0&type=sqli
```

**Parameters:**
- `limit` (int): Results per page (default: 50, max: 100)
- `offset` (int): Pagination offset (default: 0)
- `type` (string): Filter by attack type (optional)

**Response:**
```json
{
  "total": 156,
  "limit": 50,
  "offset": 0,
  "attacks": [
    {
      "id": 1,
      "ip_address": "192.168.1.100",
      "country": "United States",
      "city": "New York",
      "isp": "Verizon",
      "attack_type": "brute_force",
      "target_service": "ssh",
      "payload": "username:admin password:admin123",
      "user_agent": "ssh/1.0",
      "severity": "high",
      "timestamp": "2024-03-30T12:34:56Z"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid parameters
- `500` - Server error

---

### Statistics

#### Get Overview Statistics

```http
GET /api/stats
```

**Response:**
```json
{
  "total_attacks": 156,
  "total_blocked_ips": 23,
  "by_type": {
    "sqli": 45,
    "xss": 32,
    "brute_force": 41,
    "scan": 38,
    "other": 0
  },
  "by_severity": {
    "high": 78,
    "medium": 56,
    "low": 22
  },
  "by_service": {
    "ssh": 50,
    "ftp": 30,
    "admin": 45,
    "phpmyadmin": 31
  },
  "hourly": [
    {
      "hour": "2024-03-30T12:00:00Z",
      "count": 15
    }
  ]
}
```

---

### Top Attackers

#### Get Top 10 Attacking IPs

```http
GET /api/top-ips
```

**Response:**
```json
[
  {
    "ip": "192.168.1.100",
    "country": "United States",
    "count": 45
  },
  {
    "ip": "10.0.0.50",
    "country": "China",
    "count": 32
  }
]
```

---

### Blocked IPs

#### Get Blocked IPs List

```http
GET /api/blocked-ips
```

**Response:**
```json
{
  "total": 5,
  "blocked_ips": [
    {
      "id": 1,
      "ip_address": "192.168.1.50",
      "reason": "Threshold exceeded (attacks > 10)",
      "blocked_at": "2024-03-30T10:00:00Z"
    }
  ]
}
```

---

## Health Check

### Application Health

```http
GET /health/
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "database": "healthy",
  "checks": {
    "database": true,
    "api": true
  }
}
```

### Readiness (Kubernetes)

```http
GET /health/readiness
```

Returns `200` if application is ready to serve requests.

### Liveness (Kubernetes)

```http
GET /health/liveness
```

Always returns `200` if application is running.

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid limit parameter"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate Limited",
  "message": "20 per 1 minute"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "Please try again later"
}
```

---

## Rate Limiting

- **Default**: 20 requests per minute per IP
- **Headers**:
  - `X-RateLimit-Limit: 20`
  - `X-RateLimit-Remaining: 15`
  - `X-RateLimit-Reset: 1711800000`

---

## Pagination

All list endpoints support pagination:

```http
GET /api/attacks?limit=25&offset=50
```

- Maximum limit: 100
- Default limit: 50
- Offset starts at 0

---

## Filtering

Some endpoints support filtering:

```http
GET /api/attacks?type=sqli
GET /api/attacks?type=brute_force&severity=high
```

Available filters:
- `type` - Attack type (sqli, xss, brute_force, scan, other)
- `severity` - Severity level (low, medium, high)
- `service` - Target service (ssh, ftp, admin, phpmyadmin)

---

## CORS

Cross-Origin requests are allowed from configured origins:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## Examples

### Python (requests)

```python
import requests

# Get attacks
response = requests.get(
    'http://localhost:5000/api/attacks',
    params={'limit': 10, 'type': 'sqli'}
)
attacks = response.json()

# Get stats
stats = requests.get('http://localhost:5000/api/stats').json()

# Get top IPs
top_ips = requests.get('http://localhost:5000/api/top-ips').json()
```

### JavaScript (fetch)

```javascript
// Get attacks
const response = await fetch(
  '/api/attacks?limit=10&type=sqli'
);
const data = await response.json();

// Get statistics
const stats = await fetch('/api/stats').then(r => r.json());

console.log(stats);
```

### cURL

```bash
# Get attacks
curl http://localhost:5000/api/attacks?limit=10

# Get stats
curl http://localhost:5000/api/stats

# Get top IPs
curl http://localhost:5000/api/top-ips

# Health check
curl http://localhost:5000/health/
```

---

## Versioning

Current API version: **v1**

Future versions will use URL path:
```
/api/v2/attacks
```

---

## Guidelines

- Use HTTPS in production
- Implement API key authentication for sensitive operations
- Cache responses when appropriate
- Monitor rate limiting headers
- Handle errors gracefully on client side

---

Last Updated: March 30, 2024
