#!/bin/bash

set -e

echo "🔧 Установка Telegram-бота для раздачи ссылок"

read -p "Введите Telegram Bot Token: " BOT_TOKEN
read -p "Введите Telegram Admin ID: " ADMIN_ID

git clone https://github.com/fd25-cyber/link-distributor-bot.git /opt/linkbot
cd /opt/linkbot

cat > config.py <<EOF
BOT_TOKEN = "$BOT_TOKEN"
ADMIN_IDS = [$ADMIN_ID]
DATA_FILE = "data.json"
EOF

docker build -t linkbot .

docker run -d \
  --name linkbot \
  -v /opt/linkbot:/app \
  -w /app \
  linkbot \
  python bot.py

cat > /etc/systemd/system/linkbot.service <<EOF
[Unit]
Description=Telegram Link Distributor Bot
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker start -a linkbot
ExecStop=/usr/bin/docker stop linkbot

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reexec
systemctl enable linkbot
systemctl start linkbot

echo -e "\n✅ Бот установлен и запущен. Проверь его в Telegram."
