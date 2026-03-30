-- ============================================================
-- init_db.sql — HoneyTrap Database Initialization
-- Exécuté automatiquement par PostgreSQL au premier démarrage
-- ============================================================

-- ── Table principale : attaques ────────────────────────
CREATE TABLE IF NOT EXISTS attacks (
    id              SERIAL PRIMARY KEY,
    ip_address      VARCHAR(45)  NOT NULL,
    country         VARCHAR(100),
    city            VARCHAR(100),
    isp             VARCHAR(200),
    attack_type     VARCHAR(50)  NOT NULL DEFAULT 'other',
    target_service  VARCHAR(50),
    payload         TEXT,
    user_agent      TEXT,
    timestamp       TIMESTAMP    DEFAULT NOW(),
    severity        VARCHAR(10)  DEFAULT 'low'
);

-- Index pour accélérer les requêtes courantes
CREATE INDEX IF NOT EXISTS idx_attacks_ip        ON attacks(ip_address);
CREATE INDEX IF NOT EXISTS idx_attacks_type      ON attacks(attack_type);
CREATE INDEX IF NOT EXISTS idx_attacks_timestamp ON attacks(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_attacks_severity  ON attacks(severity);

-- ── Table : IPs bloquées ────────────────────────
CREATE TABLE IF NOT EXISTS blocked_ips (
    id          SERIAL PRIMARY KEY,
    ip_address  VARCHAR(45) UNIQUE NOT NULL,
    reason      VARCHAR(200),
    blocked_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_blocked_ip ON blocked_ips(ip_address);

-- ── Table : statistiques horaires agrégées ────────────────────────
CREATE TABLE IF NOT EXISTS attack_stats (
    id            SERIAL PRIMARY KEY,
    hour          TIMESTAMP    NOT NULL,
    attack_count  INTEGER      DEFAULT 0,
    top_country   VARCHAR(100),
    top_type      VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_stats_hour ON attack_stats(hour DESC);

-- ── Données de démonstration ────────────────────────
INSERT INTO attacks (ip_address, country, city, isp, attack_type, target_service, payload, user_agent, severity)
VALUES
  ('185.234.218.1',  'Russia',       'Moscow',     'Selectel',       'sqli',        'phpmyadmin', 'id=1 UNION SELECT 1,2,3--',              'sqlmap/1.8.3', 'high'),
  ('45.33.32.156',   'United States','Fremont',     'Linode',         'scan',        'admin',      '/wp-admin/../.env',                      'Nikto/2.1.6', 'medium'),
  ('103.21.244.10',  'China',        'Shenzhen',    'APNIC',          'brute_force', 'ssh',        'username=admin&password=admin123',       'python-requests/2.31', 'medium'),
  ('192.99.150.3',   'Canada',       'Montreal',    'OVH Hosting',    'xss',         'admin',      '<script>alert(document.cookie)</script>','Mozilla/5.0', 'high'),
  ('5.188.206.150',  'Netherlands',  'Amsterdam',   'Serverius',      'sqli',        'phpmyadmin', $$' OR '1'='1' --$$,                        'sqlmap/1.8', 'high'),
  ('91.240.118.22',  'Ukraine',      'Kyiv',        'DataGroup',      'scan',        'ftp',        '/etc/passwd',                            'Nmap Scripting Engine', 'medium'),
  ('149.28.84.100',  'United States','Los Angeles', 'Vultr',          'brute_force', 'admin',      'username=root&password=password',        'go-http-client/1.1', 'medium'),
  ('178.128.21.55',  'Germany',      'Frankfurt',   'DigitalOcean',   'xss',         'admin',      '<img src=x onerror=alert(1)>',           'curl/7.88.1', 'high'),
  ('162.243.167.58', 'United States','New York',    'DigitalOcean',   'other',       'phpmyadmin', 'GET /phpmyadmin/',                       'Mozilla/5.0', 'low'),
  ('104.236.23.110', 'United States','San Francisco','DigitalOcean',  'scan',        'ssh',        '/.git/config',                           'Gobuster/3.6', 'medium');

-- Statistiques horaires de démo
INSERT INTO attack_stats (hour, attack_count, top_country, top_type)
VALUES
  (NOW() - INTERVAL '3 hours', 12, 'Russia',        'sqli'),
  (NOW() - INTERVAL '2 hours',  8, 'China',          'brute_force'),
  (NOW() - INTERVAL '1 hour',  15, 'United States',  'scan'),
  (NOW(),                        3, 'Netherlands',    'xss');

-- Confirmation
DO $$ BEGIN
  RAISE NOTICE 'HoneyTrap DB initialisée avec succès — % attaques de démo insérées', (SELECT COUNT(*) FROM attacks);
END $$;
