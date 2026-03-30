import requests
import os
import logging

logger = logging.getLogger(__name__)

GEOIP_ENABLED = os.getenv("GEOIP_ENABLED", "true").lower() == "true"
_CACHE = {}


def get_geoip(ip: str) -> dict:
    """
    Lookup geolocation for an IP using ip-api.com (free, no key needed).
    Returns dict with country, city, isp or empty strings on failure.
    Results are cached in-memory to limit API calls.
    """
    if not GEOIP_ENABLED:
        return {"country": "", "city": "", "isp": ""}

    # Skip private / loopback IPs
    if ip in ("127.0.0.1", "::1") or ip.startswith("192.168.") or ip.startswith("10."):
        return {"country": "Local", "city": "Local", "isp": "Private Network"}

    if ip in _CACHE:
        return _CACHE[ip]

    try:
        resp = requests.get(
            f"http://ip-api.com/json/{ip}",
            timeout=3,
            params={"fields": "country,city,isp,status"},
        )
        data = resp.json()
        if data.get("status") == "success":
            result = {
                "country": data.get("country", ""),
                "city": data.get("city", ""),
                "isp": data.get("isp", ""),
            }
        else:
            result = {"country": "Unknown", "city": "Unknown", "isp": "Unknown"}
    except Exception as exc:
        logger.warning("GeoIP lookup failed for %s: %s", ip, exc)
        result = {"country": "", "city": "", "isp": ""}

    _CACHE[ip] = result
    return result
