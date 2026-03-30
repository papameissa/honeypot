"""
Database models for HoneyTrap honeypot system.
Tracks attacks, blocked IPs, and attack statistics.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from .extensions import db


class Attack(db.Model):
    """
    Represents a single attack/intrusion attempt on the honeypot.
    
    Attributes:
        id: Unique attack identifier
        ip_address: Source IP address (IPv4 or IPv6)
        country: Attacker's country (from GeoIP)
        city: Attacker's city (from GeoIP)
        isp: Attacker's ISP/AS organization (from GeoIP)
        attack_type: Classification (sqli, xss, brute_force, scan, other)
        target_service: Target service (ssh, ftp, admin, phpmyadmin)
        payload: Attack payload/request body
        user_agent: HTTP User-Agent or SSH client string
        timestamp: When attack was recorded (UTC)
        severity: Risk level (low, medium, high)
    """
    
    __tablename__ = "attacks"

    # Primary Key
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # IP Information
    ip_address: str = db.Column(db.String(45), nullable=False, index=True)
    country: Optional[str] = db.Column(db.String(100))
    city: Optional[str] = db.Column(db.String(100))
    isp: Optional[str] = db.Column(db.String(200))
    
    # Attack Information
    attack_type: str = db.Column(
        db.String(50),
        nullable=False,
        default="other",
        index=True,
        comment="Type: sqli, xss, brute_force, scan, other"
    )
    target_service: Optional[str] = db.Column(
        db.String(50),
        index=True,
        comment="Service: ssh, ftp, admin, phpmyadmin"
    )
    payload: Optional[str] = db.Column(db.Text)
    user_agent: Optional[str] = db.Column(db.Text)
    
    # Metadata
    timestamp: datetime = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow(),
        nullable=False,
        index=True
    )
    severity: str = db.Column(
        db.String(10),
        default="low",
        index=True,
        comment="Level: low, medium, high"
    )

    def __repr__(self) -> str:
        """String representation of Attack."""
        return f"<Attack {self.id}: {self.ip_address} - {self.attack_type}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert attack record to dictionary for JSON serialization.
        
        Returns:
            Dictionary with all attack attributes
        """
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "country": self.country,
            "city": self.city,
            "isp": self.isp,
            "attack_type": self.attack_type,
            "target_service": self.target_service,
            "payload": self.payload,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "severity": self.severity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attack":
        """
        Create Attack instance from dictionary.
        
        Args:
            data: Dictionary with attack attributes
            
        Returns:
            New Attack instance
        """
        return cls(
            ip_address=data["ip_address"],
            country=data.get("country"),
            city=data.get("city"),
            isp=data.get("isp"),
            attack_type=data.get("attack_type", "other"),
            target_service=data.get("target_service"),
            payload=data.get("payload"),
            user_agent=data.get("user_agent"),
            severity=data.get("severity", "low"),
        )


class BlockedIP(db.Model):
    """
    Represents an IP address blocked due to excessive attack attempts.
    
    Attributes:
        id: Unique identifier
        ip_address: Blocked IP address (unique constraint)
        reason: Why the IP was blocked
        blocked_at: When the block was applied (UTC)
    """
    
    __tablename__ = "blocked_ips"

    # Primary Key
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # IP Information
    ip_address: str = db.Column(
        db.String(45),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Block Information
    reason: Optional[str] = db.Column(db.String(200))
    blocked_at: datetime = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow(),
        nullable=False,
        index=True
    )

    def __repr__(self) -> str:
        """String representation of BlockedIP."""
        return f"<BlockedIP {self.id}: {self.ip_address}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert blocked IP record to dictionary for JSON serialization.
        
        Returns:
            Dictionary with all blocked IP attributes
        """
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "reason": self.reason,
            "blocked_at": self.blocked_at.isoformat() if self.blocked_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BlockedIP":
        """
        Create BlockedIP instance from dictionary.
        
        Args:
            data: Dictionary with blocked IP attributes
            
        Returns:
            New BlockedIP instance
        """
        return cls(
            ip_address=data["ip_address"],
            reason=data.get("reason"),
        )

    def is_blocked(self) -> bool:
        """Check if IP is currently blocked (always True for simplicity)."""
        return True


class AttackStat(db.Model):
    """
    Aggregated attack statistics for performance optimization.
    Useful for dashboard charting without querying large attack tables.
    
    Attributes:
        id: Unique identifier
        attack_type: Type of attack (sqli, xss, etc.)
        count: Number of attacks of this type
        severity: Severity level
        updated_at: Last update timestamp
    """
    
    __tablename__ = "attack_stats"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attack_type: str = db.Column(db.String(50), unique=True, nullable=False, index=True)
    count: int = db.Column(db.Integer, default=0)
    severity: Optional[str] = db.Column(db.String(10))
    updated_at: datetime = db.Column(
        db.DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow()
    )

    def __repr__(self) -> str:
        """String representation of AttackStat."""
        return f"<AttackStat {self.attack_type}: {self.count}>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "attack_type": self.attack_type,
            "count": self.count,
            "severity": self.severity,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


