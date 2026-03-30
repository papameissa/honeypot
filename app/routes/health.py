"""Health check and status endpoint."""
from flask import Blueprint, jsonify
from ..extensions import db
from ..models import Attack
import os

health_bp = Blueprint("health", __name__, url_prefix="/health")


@health_bp.route("/", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    Returns application and database status.
    """
    try:
        # Check database connection
        db.session.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return jsonify({
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("FLASK_ENV", "development"),
        "database": db_status,
        "checks": {
            "database": db_status == "healthy",
            "api": True,
        }
    }), 200 if db_status == "healthy" else 503


@health_bp.route("/readiness", methods=["GET"])
def readiness_check():
    """Kubernetes readiness probe."""
    try:
        db.session.execute("SELECT 1")
        return jsonify({"ready": True}), 200
    except Exception:
        return jsonify({"ready": False}), 503


@health_bp.route("/liveness", methods=["GET"])
def liveness_check():
    """Kubernetes liveness probe."""
    return jsonify({"alive": True}), 200


@health_bp.route("/stats", methods=["GET"])
def stats_endpoint():
    """Application statistics."""
    try:
        total_attacks = Attack.query.count()
        return jsonify({
            "total_attacks": total_attacks,
            "status": "operational",
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500
