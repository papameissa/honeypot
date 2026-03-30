"""
Tests du classifieur d'attaques — HoneyTrap
Lance avec : pytest tests/test_classifier.py -v
"""

import pytest
from app.utils.classifier import classify_attack


class TestClassifySQLi:
    def test_union_select(self):
        result = classify_attack(payload="id=1 UNION SELECT 1,2,3--")
        assert result["attack_type"] == "sqli"
        assert result["severity"] == "high"

    def test_or_1_equals_1(self):
        result = classify_attack(payload="' OR '1'='1' --")
        assert result["attack_type"] == "sqli"

    def test_sleep_injection(self):
        result = classify_attack(payload="'; SLEEP(5)--")
        assert result["attack_type"] == "sqli"


class TestClassifyXSS:
    def test_script_tag(self):
        result = classify_attack(payload="<script>alert(1)</script>")
        assert result["attack_type"] == "xss"
        assert result["severity"] == "high"

    def test_onerror(self):
        result = classify_attack(payload="<img src=x onerror=alert(document.cookie)>")
        assert result["attack_type"] == "xss"

    def test_javascript_proto(self):
        result = classify_attack(payload="javascript:alert(1)")
        assert result["attack_type"] == "xss"


class TestClassifyScan:
    def test_env_file(self):
        result = classify_attack(payload="GET /.env HTTP/1.1")
        assert result["attack_type"] == "scan"

    def test_git_config(self):
        result = classify_attack(payload="GET /.git/config")
        assert result["attack_type"] == "scan"

    def test_path_traversal(self):
        result = classify_attack(payload="../../etc/passwd")
        assert result["attack_type"] == "scan"


class TestClassifyBruteForce:
    def test_password_keyword(self):
        result = classify_attack(payload="username=admin&password=admin123")
        assert result["attack_type"] == "brute_force"

    def test_common_password(self):
        result = classify_attack(payload="password=123456")
        assert result["attack_type"] == "brute_force"


class TestClassifyOther:
    def test_empty_payload(self):
        result = classify_attack(payload="")
        assert result["attack_type"] == "other"
        assert result["severity"] == "low"

    def test_normal_request(self):
        result = classify_attack(payload="GET /index.html HTTP/1.1")
        assert result["attack_type"] == "other"


class TestBotDetection:
    def test_sqlmap_detected(self):
        result = classify_attack(user_agent="sqlmap/1.8.3#stable (https://sqlmap.org)")
        assert result["is_bot"] is True

    def test_nikto_detected(self):
        result = classify_attack(user_agent="Nikto/2.1.6")
        assert result["is_bot"] is True

    def test_normal_browser_not_bot(self):
        result = classify_attack(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        assert result["is_bot"] is False

    def test_bot_elevates_severity(self):
        result = classify_attack(payload="", user_agent="curl/7.88.1")
        assert result["is_bot"] is True
        assert result["severity"] in ("medium", "high")
