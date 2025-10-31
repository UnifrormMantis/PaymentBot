#!/bin/bash

# Скрипт деплоя Payment Bot на VPS
# Выполните на VPS после git pull

echo "=== ДЕПЛОЙ PAYMENT BOT НА VPS ==="

cd /opt/fondklik/payment_bot || exit 1

# Обновление базы данных
sqlite3 payments.db << 'SQL'
INSERT OR REPLACE INTO users (user_id, username)
VALUES (8489431460, 'мартин');

CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    api_key TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO api_keys (api_key, is_active)
VALUES ('QGCHTq8vAjaeeSAXdzkH2OQMmyzfirvVKOxxxivNzyc', 1);
SQL

# Перезапуск
systemctl restart payment-bot.service

echo "✅ Payment Bot обновлен!"

