"""
Génère des exports CSV et JSON à partir des données d'attaques.
"""

import csv
import io
import json
from ..models import Attack


def export_attacks_csv() -> str:
    """Retourne une chaîne CSV de toutes les attaques."""
    attacks = Attack.query.order_by(Attack.timestamp.desc()).all()
    output = io.StringIO()
    fieldnames = [
        "id", "ip_address", "country", "city", "isp",
        "attack_type", "target_service", "payload",
        "user_agent", "timestamp", "severity",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for a in attacks:
        writer.writerow({
            "id": a.id,
            "ip_address": a.ip_address,
            "country": a.country or "",
            "city": a.city or "",
            "isp": a.isp or "",
            "attack_type": a.attack_type,
            "target_service": a.target_service or "",
            "payload": (a.payload or "")[:500],
            "user_agent": a.user_agent or "",
            "timestamp": a.timestamp.isoformat() if a.timestamp else "",
            "severity": a.severity or "",
        })
    return output.getvalue()


def export_attacks_json() -> str:
    """Retourne une chaîne JSON de toutes les attaques."""
    attacks = Attack.query.order_by(Attack.timestamp.desc()).all()
    return json.dumps(
        {"total": len(attacks), "attacks": [a.to_dict() for a in attacks]},
        indent=2,
        ensure_ascii=False,
        default=str,
    )
