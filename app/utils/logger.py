"""
Logger JSON structuré — compatible SIEM (Splunk, ELK, etc.)
Chaque attaque est enregistrée dans attacks.log au format JSON.
"""

import logging
import json
import os
from datetime import datetime, timezone


LOG_FILE = os.getenv("LOG_FILE", "attacks.log")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record, ensure_ascii=False)


def get_attack_logger() -> logging.Logger:
    """Retourne un logger JSON prêt à l'emploi."""
    logger = logging.getLogger("honeytrap.attacks")
    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_attack(ip: str, attack_type: str, service: str, payload: str = "",
               country: str = "", severity: str = "low", user_agent: str = ""):
    """Enregistre une attaque structurée dans le fichier de logs JSON."""
    logger = get_attack_logger()
    record = logging.LogRecord(
        name="honeytrap.attacks",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="attack_detected",
        args=(),
        exc_info=None,
    )
    record.extra = {
        "ip": ip,
        "attack_type": attack_type,
        "target_service": service,
        "payload_preview": payload[:200] if payload else "",
        "country": country,
        "severity": severity,
        "user_agent": user_agent,
    }
    logger.handle(record)
