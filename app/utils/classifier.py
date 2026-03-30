"""
Classifie automatiquement le type d'attaque et sa sévérité
en analysant le payload et le User-Agent.
"""

import re

# --- Patterns de détection ---

SQLI_PATTERNS = [
    r"(?i)(union\s+select|select\s+.+from|insert\s+into|drop\s+table|--|;--|'--)",
    r"(?i)(or\s+1=1|and\s+1=1|or\s+'[^']*'='[^']*')",
    r"(?i)(sleep\s*\(|benchmark\s*\(|waitfor\s+delay)",
    r"(?i)(xp_cmdshell|exec\s*\(|execute\s*\()",
]

XSS_PATTERNS = [
    r"(?i)(<script|</script>|javascript:|onerror=|onload=|onclick=)",
    r"(?i)(alert\s*\(|confirm\s*\(|prompt\s*\()",
    r"(?i)(<iframe|<img\s+src|<svg\s+onload)",
    r"(?i)(document\.cookie|window\.location)",
]

BRUTE_FORCE_PATTERNS = [
    r"(?i)(password|passwd|pwd|pass|login|admin|root|user)",
    r"(?i)(123456|password123|admin123|letmein|qwerty)",
]

SCAN_PATTERNS = [
    r"(?i)(\.env|\.git|wp-config|web\.config|\.htaccess)",
    r"(?i)(\.\./|%2e%2e|directory traversal|/etc/passwd)",
    r"(?i)(phpinfo|phpMyAdmin|adminer|phpmyadmin)",
]

# Outils de scan/attaque connus
SCANNER_AGENTS = [
    "sqlmap", "nikto", "nmap", "masscan", "hydra",
    "metasploit", "burpsuite", "dirbuster", "gobuster",
    "nuclei", "zgrab", "python-requests", "curl/",
    "wget/", "scrapy", "go-http-client",
]


def classify_attack(payload: str = "", user_agent: str = "") -> dict:
    """
    Retourne un dict avec :
      - attack_type : brute_force | sqli | xss | scan | other
      - severity    : high | medium | low
      - is_bot      : True si User-Agent reconnu comme scanner
    """
    payload = payload or ""
    user_agent = user_agent or ""
    combined = payload + " " + user_agent

    # Détection du type
    if any(re.search(p, combined) for p in SQLI_PATTERNS):
        attack_type = "sqli"
        severity = "high"
    elif any(re.search(p, combined) for p in XSS_PATTERNS):
        attack_type = "xss"
        severity = "high"
    elif any(re.search(p, combined) for p in SCAN_PATTERNS):
        attack_type = "scan"
        severity = "medium"
    elif any(re.search(p, combined) for p in BRUTE_FORCE_PATTERNS):
        attack_type = "brute_force"
        severity = "medium"
    else:
        attack_type = "other"
        severity = "low"

    # Détection bot/scanner via User-Agent
    is_bot = any(tool.lower() in user_agent.lower() for tool in SCANNER_AGENTS)
    if is_bot and severity == "low":
        severity = "medium"

    return {
        "attack_type": attack_type,
        "severity": severity,
        "is_bot": is_bot,
    }
