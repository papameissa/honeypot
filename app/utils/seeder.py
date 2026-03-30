"""Database seeding utility for populating initial test data."""
from datetime import datetime, timedelta
from app.extensions import db
from app.models import Attack, BlockedIP, AttackStat


def seed():
    """Seed the database with sample attack and statistics data."""
    # Clear existing data
    Attack.query.delete()
    BlockedIP.query.delete()
    AttackStat.query.delete()
    
    # Sample attack data
    sample_attacks = [
        Attack(
            ip_address="192.168.1.100",
            country="France",
            city="Paris",
            isp="Orange France",
            attack_type="sqli",
            target_service="admin",
            payload="' OR '1'='1' --",
            user_agent="Mozilla/5.0",
            severity="high",
        ),
        Attack(
            ip_address="10.0.0.50",
            country="China",
            city="Beijing",
            isp="China Unicom",
            attack_type="brute_force",
            target_service="ssh",
            payload="root:password123",
            user_agent="SSH-2.0-OpenSSH_7.4",
            severity="high",
        ),
        Attack(
            ip_address="172.16.0.10",
            country="United States",
            city="New York",
            isp="Verizon",
            attack_type="xss",
            target_service="phpmyadmin",
            payload="<script>alert('XSS')</script>",
            user_agent="Mozilla/5.0",
            severity="medium",
        ),
        Attack(
            ip_address="203.0.113.45",
            country="India",
            city="Mumbai",
            isp="Jio",
            attack_type="scan",
            target_service="ftp",
            payload="NMAP scan",
            user_agent="curl/7.64.1",
            severity="low",
        ),
        Attack(
            ip_address="198.51.100.99",
            country="Brazil",
            city="São Paulo",
            isp="Vivo",
            attack_type="other",
            target_service="admin",
            payload="Unknown payload",
            user_agent="Unknown",
            severity="low",
        ),
    ]
    
    for attack in sample_attacks:
        db.session.add(attack)
    
    # Sample blocked IPs
    blocked_ips = [
        BlockedIP(ip_address="192.168.1.100", reason="High frequency SQL injection attacks"),
        BlockedIP(ip_address="10.0.0.50", reason="Repeated SSH brute force attempts"),
        BlockedIP(ip_address="203.0.113.45", reason="Network enumeration scan"),
    ]
    
    for blocked_ip in blocked_ips:
        db.session.add(blocked_ip)
    
    # Sample attack statistics
    stats = [
        AttackStat(
            attack_type="sqli",
            count=45,
            severity="high",
        ),
        AttackStat(
            attack_type="brute_force",
            count=32,
            severity="high",
        ),
        AttackStat(
            attack_type="xss",
            count=18,
            severity="medium",
        ),
        AttackStat(
            attack_type="scan",
            count=42,
            severity="low",
        ),
        AttackStat(
            attack_type="other",
            count=12,
            severity="low",
        ),
    ]
    
    for stat in stats:
        db.session.add(stat)
    
    db.session.commit()
    print(f"✓ Added {len(sample_attacks)} sample attacks")
    print(f"✓ Added {len(blocked_ips)} blocked IPs")
    print(f"✓ Added {len(stats)} attack statistics")
