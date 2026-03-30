from flask import Blueprint, request, render_template
from ..extensions import db, limiter
from ..models import Attack, BlockedIP
from ..utils.geoip import get_geoip
from ..utils.classifier import classify_attack
from ..utils.logger import log_attack
import os

honeypot_bp = Blueprint("honeypot", __name__, url_prefix="/fake")

BLOCK_THRESHOLD = int(os.getenv("BLOCK_THRESHOLD", 10))
RATE_LIMIT = os.getenv("RATE_LIMIT", "20 per minute")


def _record_attack(service: str):
    """Enregistre l'attaque en BDD, géolocalise, classifie, et bloque si nécessaire."""
    ip = request.remote_addr
    ua = request.headers.get("User-Agent", "")
    payload = (request.get_data(as_text=True) or "") + str(dict(request.args))

    geo = get_geoip(ip)
    classification = classify_attack(payload=payload, user_agent=ua)

    attack = Attack(
        ip_address=ip,
        country=geo["country"],
        city=geo["city"],
        isp=geo["isp"],
        attack_type=classification["attack_type"],
        target_service=service,
        payload=payload[:2000],
        user_agent=ua,
        severity=classification["severity"],
    )
    db.session.add(attack)

    # Blocage automatique si seuil atteint
    attack_count = Attack.query.filter_by(ip_address=ip).count()
    if attack_count >= BLOCK_THRESHOLD:
        existing = BlockedIP.query.filter_by(ip_address=ip).first()
        if not existing:
            blocked = BlockedIP(
                ip_address=ip,
                reason=f"Seuil de {BLOCK_THRESHOLD} attaques atteint",
            )
            db.session.add(blocked)

    db.session.commit()

    log_attack(
        ip=ip,
        attack_type=classification["attack_type"],
        service=service,
        payload=payload,
        country=geo["country"],
        severity=classification["severity"],
        user_agent=ua,
    )


@honeypot_bp.route("/ssh", methods=["GET", "POST"])
@limiter.limit(RATE_LIMIT)
def fake_ssh():
    _record_attack("ssh")
    error = None
    if request.method == "POST":
        error = "ssh: connect to host localhost port 22: Connection refused"
    return render_template("fake/ssh.html", error=error)


@honeypot_bp.route("/ftp", methods=["GET", "POST"])
@limiter.limit(RATE_LIMIT)
def fake_ftp():
    _record_attack("ftp")
    error = None
    if request.method == "POST":
        error = "530 Login incorrect."
    return render_template("fake/ftp.html", error=error)


@honeypot_bp.route("/admin", methods=["GET", "POST"])
@limiter.limit(RATE_LIMIT)
def fake_admin():
    _record_attack("admin")
    error = None
    if request.method == "POST":
        error = "ERROR: Invalid username or password."
    return render_template("fake/admin.html", error=error)


@honeypot_bp.route("/phpmyadmin", methods=["GET", "POST"])
@limiter.limit(RATE_LIMIT)
def fake_phpmyadmin():
    _record_attack("phpmyadmin")
    error = None
    if request.method == "POST":
        error = "#1045 - Access denied for user 'root'@'localhost'"
    return render_template("fake/phpmyadmin.html", error=error)
