"""
HoneyTrap Application Factory
Professional honeypot intrusion detection system
"""
import logging
from flask import Flask
from flask_cors import CORS
from .extensions import db, limiter, migrate
from config import config_map
import os


def create_app(config_name: str | None = None) -> Flask:
    """
    Application factory with professional configuration.
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # ── Initialize Extensions ──
    db.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    
    # ── CORS Configuration ──
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", [])}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"],
        max_age=3600
    )
    
    # ── Security Headers ──
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' cdn.jsdelivr.net"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
    
    # ── Register Blueprints ──
    from .routes.dashboard import dashboard_bp
    from .routes.honeypot import honeypot_bp
    from .routes.api import api_bp
    from .routes.export import export_bp
    from .routes.health import health_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(honeypot_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(health_bp)
    
    # ── Error Handlers ──
    register_error_handlers(app)
    
    # ── Logging ──
    setup_logging(app)
    
    # ── CLI Commands ──
    register_cli_commands(app)
    
    return app


def register_error_handlers(app: Flask) -> None:
    """Register professional error handlers."""
    from flask import jsonify
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad Request", "message": str(e)}), 400
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "message": str(e)}), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found", "message": "Resource not found"}), 404
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({"error": "Rate Limited", "message": str(e.description)}), 429
    
    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal Server Error: {str(e)}")
        return jsonify({"error": "Internal Server Error", "message": "Please try again later"}), 500


def setup_logging(app: Flask) -> None:
    """Configure professional JSON logging."""
    import json
    from datetime import datetime
    
    class JSONFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_data)
    
    # Remove Flask's default handlers
    app.logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    app.logger.addHandler(handler)
    app.logger.setLevel(getattr(logging, app.config.get("LOG_LEVEL", "INFO")))


def register_cli_commands(app: Flask) -> None:
    """Register CLI commands for database management."""
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print("Database initialized.")
    
    @app.cli.command()
    def seed_db():
        """Seed database with test data."""
        from app.utils.seeder import seed
        seed()
        print("Database seeded.")
    
    @app.cli.command()
    def reset_db():
        """Reset the database."""
        if app.config.get("TESTING") or app.config.get("DEBUG"):
            db.drop_all()
            db.create_all()
            print("Database reset.")
        else:
            print("Reset only allowed in development/testing mode.")
