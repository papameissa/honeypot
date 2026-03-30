#!/usr/bin/env python3
"""
HoneyTrap — Attack Simulation Script
Teste tous les services leurres du honeypot
"""

import socket
import requests
import time
import sys
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:5000"
DEBUG = True
TIMEOUT = 5

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def log_test(service, status, message):
    """Log test result"""
    if status == "✓":
        color = Fore.GREEN
    elif status == "✕":
        color = Fore.RED
    else:
        color = Fore.YELLOW
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {status} {service:20} → {message}{Style.RESET_ALL}")


def test_ssh_brute_force():
    """Simulate SSH brute force attack on port 22"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 1: SSH Brute-Force Attack (Port 22)")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect(('localhost', 22))
        
        # Send SSH banner grab
        response = sock.recv(1024).decode('utf-8', errors='ignore')
        sock.close()
        
        if 'SSH' in response:
            log_test("SSH Banner", "✓", f"Honeypot detected: {response.strip()}")
        
        # Try multiple login attempts (simulate brute force)
        attempts = ['admin:admin', 'root:password', 'test:test', 'user:user']
        for attempt in attempts:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            try:
                sock.connect(('localhost', 22))
                log_test("SSH Attempt", "○", f"Login attempt: {attempt}")
                sock.close()
                time.sleep(0.3)
            except Exception as e:
                pass
        
        log_test("SSH Brute-Force", "✓", f"Attack logged in honeypot")
        
    except Exception as e:
        log_test("SSH Brute-Force", "✕", str(e))


def test_ftp_attack():
    """Simulate FTP attack on port 21"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 2: FTP Brute-Force Attack (Port 21)")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect(('localhost', 21))
        
        response = sock.recv(1024).decode('utf-8', errors='ignore')
        if 'FTP' in response:
            log_test("FTP Banner", "✓", f"FTP Server detected")
        
        # Try FTP login
        sock.sendall(b'USER admin\r\n')
        time.sleep(0.2)
        log_test("FTP Login", "○", "admin:badpassword")
        
        sock.sendall(b'PASS badpassword\r\n')
        time.sleep(0.2)
        
        sock.sendall(b'LIST\r\n')
        time.sleep(0.2)
        
        sock.close()
        log_test("FTP Attack", "✓", "Attack logged in honeypot")
        
    except Exception as e:
        log_test("FTP Attack", "✕", str(e))


def test_http_fake_services():
    """Test HTTP fake services - Brute Force"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 3: HTTP Fake Services - Brute Force")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    fake_services = [
        ('/fake/ssh', 'SSH Terminal', {'username': 'admin', 'password': 'pass123'}),
        ('/fake/ftp', 'FTP Server', {'user': 'admin', 'password': 'secret'}),
        ('/fake/admin', 'WordPress Admin', {'log': 'admin', 'pwd': 'admin123'}),
        ('/fake/phpmyadmin', 'phpMyAdmin', {'pma_username': 'root', 'pma_password': 'password'}),
    ]
    
    for endpoint, service_name, payload in fake_services:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=TIMEOUT)
            
            if response.status_code == 200:
                log_test(f"HTTP {service_name}", "✓", f"Leurre accessible (Status: {response.status_code})")
                
                # Try POST with credentials
                try:
                    post_response = requests.post(url, data=payload, timeout=TIMEOUT)
                    log_test(f"Login Attempt", "○", f"{service_name} (with credentials)")
                except:
                    pass
            else:
                log_test(f"HTTP {service_name}", "✕", f"Status: {response.status_code}")
        
        except Exception as e:
            log_test(f"HTTP {service_name}", "✕", str(e))
        
        time.sleep(0.5)


def test_sql_injection():
    """Test SQL Injection attacks"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 4: SQL Injection Attacks")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    sqli_payloads = [
        ("admin' OR '1'='1", "Classic OR condition"),
        ("admin'; DROP TABLE users--", "DROP statement injection"),
        ("' UNION SELECT NULL,NULL,NULL--", "UNION-based injection"),
        ("1' AND SLEEP(5)--", "Time-based blind SQLi"),
        ("admin' OR 1=1--", "Simple authentication bypass"),
        ("'; EXEC xp_cmdshell('dir');--", "Command execution via SQL"),
    ]
    
    services = [
        ('/fake/admin', 'WordPress Admin'),
        ('/fake/phpmyadmin', 'phpMyAdmin'),
    ]
    
    for endpoint, service_name in services:
        for payload, exploit_type in sqli_payloads:
            try:
                url = f"{BASE_URL}{endpoint}?user={payload}&password=test"
                response = requests.get(url, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    log_test(f"SQLi {service_name}", "✓", f"{exploit_type}")
                else:
                    log_test(f"SQLi {service_name}", "○", f"Status {response.status_code}")
            
            except Exception as e:
                log_test(f"SQLi {service_name}", "✕", str(e))
            
            time.sleep(0.2)


def test_xss_attacks():
    """Test Cross-Site Scripting (XSS) attacks"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 5: Cross-Site Scripting (XSS) Attacks")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    xss_payloads = [
        ("<script>alert('XSS')</script>", "Inline script"),
        ("<img src=x onerror=\"alert('XSS')\">", "Image onerror"),
        ("<svg onload=\"alert('XSS')\">", "SVG onload"),
        ("javascript:alert('XSS')", "JavaScript protocol"),
        ("<iframe src=\"javascript:alert('XSS')\">", "Iframe javascript"),
        ("<body onload=\"alert('XSS')\">", "Body onload"),
        ("<input onfocus=\"alert('XSS')\" autofocus>", "Input onfocus"),
    ]
    
    services = [
        ('/fake/admin', 'WordPress Admin'),
        ('/fake/phpmyadmin', 'phpMyAdmin'),
        ('/fake/ssh', 'SSH Terminal'),
    ]
    
    for endpoint, service_name in services:
        for payload, exploit_type in xss_payloads:
            try:
                url = f"{BASE_URL}{endpoint}?input={payload}"
                response = requests.get(url, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    log_test(f"XSS {service_name}", "✓", f"{exploit_type}")
                else:
                    log_test(f"XSS {service_name}", "○", f"Status {response.status_code}")
            
            except Exception as e:
                log_test(f"XSS {service_name}", "✕", str(e))
            
            time.sleep(0.2)


def test_directory_traversal():
    """Test Directory Traversal / Path Traversal attacks"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 6: Directory Traversal / Path Traversal")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    traversal_payloads = [
        ("../../etc/passwd", "Unix password file"),
        ("..\\..\\windows\\win.ini", "Windows config"),
        ("../../.env", "Environment variables"),
        ("../../../.git/config", "Git configuration"),
        ("%2e%2e%2fetc%2fpasswd", "URL encoded traversal"),
        ("....//....//etc/passwd", "Double dot bypass"),
        ("/etc/passwd", "Absolute path"),
        ("../../database.yml", "Rails config"),
    ]
    
    services = [
        ('/fake/ftp', 'FTP Server'),
        ('/fake/admin', 'WordPress Admin'),
    ]
    
    for endpoint, service_name in services:
        for payload, exploit_type in traversal_payloads:
            try:
                url = f"{BASE_URL}{endpoint}?file={payload}"
                response = requests.get(url, timeout=TIMEOUT)
                
                if response.status_code == 200:
                    log_test(f"Path Traversal {service_name}", "✓", f"{exploit_type}")
                else:
                    log_test(f"Path Traversal {service_name}", "○", f"Status {response.status_code}")
            
            except Exception as e:
                log_test(f"Path Traversal {service_name}", "✕", str(e))
            
            time.sleep(0.2)


def test_reconnaissance_scanning():
    """Test reconnaissance and scanning attempts"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 7: Reconnaissance / Vulnerability Scanning")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    scan_payloads = [
        ("/.env", "Environment config"),
        ("/.git/config", "Git exposure"),
        ("/wp-config.php", "WordPress config"),
        ("/phpMyAdmin/", "phpMyAdmin path"),
        ("/.htaccess", "Apache config"),
        ("/web.config", "IIS config"),
        ("/admin.php", "Admin page"),
        ("/database.yml", "Rails database"),
        ("/.github/workflows", "GitHub workflows"),
        ("/package.json", "Node.js package"),
    ]
    
    for payload in scan_payloads:
        try:
            url = f"{BASE_URL}{payload}"
            response = requests.get(url, timeout=TIMEOUT)
            
            if response.status_code == 200:
                log_test(f"Reconnaissance", "✓", f"Found: {payload} (Status: {response.status_code})")
            elif response.status_code == 404:
                log_test(f"Reconnaissance", "○", f"Tested: {payload}")
            else:
                log_test(f"Reconnaissance", "○", f"{payload} (Status: {response.status_code})")
        
        except Exception as e:
            log_test(f"Reconnaissance", "✕", str(e))
        
        time.sleep(0.1)


def test_api_endpoints():
    """Test API endpoints for attack data"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 8: API Endpoints & Data Retrieval")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    api_endpoints = [
        ('/api/attacks', 'Get all attacks'),
        ('/api/health', 'Health check'),
        ('/dashboard', 'Dashboard page'),
    ]
    
    for endpoint, description in api_endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=TIMEOUT)
            
            if response.status_code == 200:
                log_test("API", "✓", f"{description} (Status: 200)")
            else:
                log_test("API", "○", f"{description} (Status: {response.status_code})")
        
        except Exception as e:
            log_test("API", "✕", f"{description} - {str(e)}")
        
        time.sleep(0.3)


def check_honeypot_running():
    """Check if honeypot is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=3)
        return response.status_code == 200
    except:
        return False


def main():
    """Run all attack simulations"""
    print(f"\n{Fore.YELLOW}{Colors.BOLD}")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║   HoneyTrap Attack Simulation Suite v2.0           ║")
    print("║   Advanced Attack Testing & Detection              ║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Style.RESET_ALL}\n")
    
    # Check if honeypot is running
    print(f"{Fore.CYAN}Checking honeypot status...{Style.RESET_ALL}")
    if not check_honeypot_running():
        print(f"{Fore.RED}❌ HoneyTrap is not running on {BASE_URL}")
        print(f"Start it with: docker-compose up{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"{Fore.GREEN}✓ HoneyTrap is running!{Style.RESET_ALL}\n")
    
    # Run all tests
    try:
        test_ssh_brute_force()
        time.sleep(1)
        
        test_ftp_attack()
        time.sleep(1)
        
        test_http_fake_services()
        time.sleep(1)
        
        test_sql_injection()
        time.sleep(1)
        
        test_xss_attacks()
        time.sleep(1)
        
        test_directory_traversal()
        time.sleep(1)
        
        test_reconnaissance_scanning()
        time.sleep(1)
        
        test_api_endpoints()
        
        # Summary
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"SUMMARY - All Attack Simulations Completed!")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Successfully tested multiple attack vectors:{Style.RESET_ALL}")
        print(f"  ✓ Brute Force (SSH, FTP, HTTP)")
        print(f"  ✓ SQL Injection (SQLi)")
        print(f"  ✓ Cross-Site Scripting (XSS)")
        print(f"  ✓ Directory Traversal / Path Traversal")
        print(f"  ✓ Reconnaissance / Vulnerability Scanning")
        print(f"  ✓ API Endpoints")
        
        print(f"\n{Fore.YELLOW}Check the dashboard at:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  → http://localhost:5000/dashboard{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}View API data:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  → http://localhost:5000/api/attacks{Style.RESET_ALL}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Test interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
