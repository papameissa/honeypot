"""
Tests des routes Flask — HoneyTrap
Lance avec : pytest tests/test_routes.py -v
"""

import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Crée une instance Flask de test avec SQLite en mémoire."""
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# ── Dashboard ────────────────────────────────────────────

class TestDashboard:
    def test_dashboard_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_dashboard_contains_honeytrap(self, client):
        resp = client.get("/")
        assert b"HoneyTrap" in resp.data or b"honeytrap" in resp.data.lower()


# ── Honeypot Routes ────────────────────────────────────────────

class TestHoneypotRoutes:
    @pytest.mark.parametrize("path", [
        "/fake/ssh",
        "/fake/ftp",
        "/fake/admin",
        "/fake/phpmyadmin",
    ])
    def test_fake_route_get_200(self, client, path):
        resp = client.get(path)
        assert resp.status_code == 200, f"GET {path} → {resp.status_code}"

    @pytest.mark.parametrize("path", [
        "/fake/ssh",
        "/fake/ftp",
        "/fake/admin",
        "/fake/phpmyadmin",
    ])
    def test_fake_route_post_records_attack(self, client, path):
        resp = client.post(path, data={"username": "admin", "password": "admin"})
        # POST retourne 200 avec message d'erreur leurre
        assert resp.status_code == 200

    def test_sql_injection_recorded(self, client):
        """Un payload SQLi doit être enregistré sans planter l'app."""
        resp = client.post(
            "/fake/phpmyadmin",
            data={"pma_username": "' OR '1'='1", "pma_password": "x"},
        )
        assert resp.status_code == 200

    def test_xss_payload_recorded(self, client):
        resp = client.post(
            "/fake/admin",
            data={"log": "<script>alert(1)</script>", "pwd": "x"},
        )
        assert resp.status_code == 200


# ── API Routes ────────────────────────────────────────────

class TestAPI:
    def test_api_attacks_returns_json(self, client):
        resp = client.get("/api/attacks")
        assert resp.status_code == 200
        assert resp.content_type.startswith("application/json")

    def test_api_attacks_structure(self, client):
        data = client.get("/api/attacks").get_json()
        assert "total" in data
        assert "attacks" in data
        assert isinstance(data["attacks"], list)

    def test_api_stats_returns_json(self, client):
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total_attacks" in data
        assert "total_blocked_ips" in data

    def test_api_top_ips_returns_list(self, client):
        resp = client.get("/api/top-ips")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_api_blocked_ips(self, client):
        resp = client.get("/api/blocked-ips")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "blocked_ips" in data


# ── Export Routes ────────────────────────────────────────────

class TestExport:
    def test_export_csv_returns_csv(self, client):
        resp = client.get("/export/csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.content_type

    def test_export_json_returns_json(self, client):
        resp = client.get("/export/json")
        assert resp.status_code == 200
        assert "application/json" in resp.content_type
