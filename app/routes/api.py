from flask import Blueprint, jsonify, request
from ..models import Attack, BlockedIP, AttackStat
from ..extensions import db
from sqlalchemy import func

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/attacks")
def get_attacks():
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    attack_type = request.args.get("type")

    query = Attack.query.order_by(Attack.timestamp.desc())
    if attack_type:
        query = query.filter_by(attack_type=attack_type)

    attacks = query.offset(offset).limit(limit).all()
    total = Attack.query.count()

    return jsonify({
        "total": total,
        "limit": limit,
        "offset": offset,
        "attacks": [a.to_dict() for a in attacks],
    })


@api_bp.route("/stats")
def get_stats():
    total = Attack.query.count()
    blocked = BlockedIP.query.count()

    type_dist = (
        db.session.query(Attack.attack_type, func.count(Attack.id))
        .group_by(Attack.attack_type)
        .all()
    )
    severity_dist = (
        db.session.query(Attack.severity, func.count(Attack.id))
        .group_by(Attack.severity)
        .all()
    )
    service_dist = (
        db.session.query(Attack.target_service, func.count(Attack.id))
        .group_by(Attack.target_service)
        .all()
    )

    # Attacks per hour (last 24h) — compatible PostgreSQL et SQLite
    try:
        hourly = (
            db.session.query(
                func.date_trunc("hour", Attack.timestamp).label("hour"),
                func.count(Attack.id).label("count"),
            )
            .group_by("hour")
            .order_by("hour")
            .limit(24)
            .all()
        )
        hourly_data = [{"hour": str(h), "count": c} for h, c in hourly]
    except Exception:
        # SQLite fallback (tests unitaires)
        hourly_data = []

    return jsonify({
        "total_attacks": total,
        "total_blocked_ips": blocked,
        "by_type": {t: c for t, c in type_dist},
        "by_severity": {s: c for s, c in severity_dist},
        "by_service": {s: c for s, c in service_dist},
        "hourly": hourly_data,
    })


@api_bp.route("/top-ips")
def get_top_ips():
    top = (
        db.session.query(Attack.ip_address, Attack.country,
                         func.count(Attack.id).label("count"))
        .group_by(Attack.ip_address, Attack.country)
        .order_by(func.count(Attack.id).desc())
        .limit(10)
        .all()
    )
    return jsonify([
        {"ip": ip, "country": country or "?", "count": count}
        for ip, country, count in top
    ])


@api_bp.route("/blocked-ips")
def get_blocked_ips():
    blocked = BlockedIP.query.order_by(BlockedIP.blocked_at.desc()).all()
    return jsonify({"total": len(blocked), "blocked_ips": [b.to_dict() for b in blocked]})
