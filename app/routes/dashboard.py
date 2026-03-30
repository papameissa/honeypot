from flask import Blueprint, render_template
from ..models import Attack, BlockedIP, AttackStat
from ..extensions import db
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    total_attacks = Attack.query.count()
    total_blocked = BlockedIP.query.count()

    # Top 5 attacking IPs
    top_ips = [
        {"ip_address": row[0], "count": row[1]}
        for row in db.session.query(Attack.ip_address, func.count(Attack.id).label("count"))
        .group_by(Attack.ip_address)
        .order_by(func.count(Attack.id).desc())
        .limit(5)
        .all()
    ]

    # Recent 20 attacks
    recent_attacks = Attack.query.order_by(Attack.timestamp.desc()).limit(20).all()

    # Attack type distribution
    type_stats = [
        {"attack_type": row[0], "count": row[1]}
        for row in db.session.query(Attack.attack_type, func.count(Attack.id).label("count"))
        .group_by(Attack.attack_type)
        .all()
    ]

    # Severity distribution
    severity_stats = [
        {"severity": row[0], "count": row[1]}
        for row in db.session.query(Attack.severity, func.count(Attack.id).label("count"))
        .group_by(Attack.severity)
        .all()
    ]

    return render_template(
        "dashboard.html",
        total_attacks=total_attacks,
        total_blocked=total_blocked,
        top_ips=top_ips,
        recent_attacks=recent_attacks,
        type_stats=type_stats,
        severity_stats=severity_stats,
    )
