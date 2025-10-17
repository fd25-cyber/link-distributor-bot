#!/bin/bash
set -e

echo "🔧 Установка Telegram-бота с безопасным хранением токена"

# Проверка существующего контейнера
if docker ps -a --format '{{.Names}}' | grep -q "^linkbot$"; then
  echo "🛑 Контейнер 'linkbot' уже существует. Перезапускаем..."
  docker stop linkbot || true
  docker rm -f linkbot || true
fi

# Создание .env
if [ -f .env ]; then
  echo "⚠️ Файл .env уже существует. Используем текущие значения."
else
  read -p "Введите Telegram Bot Token: " BOT_TOKEN
  read -p "Введите Telegram Admin ID (через запятую, если несколько): " ADMIN_IDS

  cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_IDS=$ADMIN_IDS
EOF
  echo "✅ Файл .env создан."
fi

# Проверка requirements.txt
if ! grep -q "python-dotenv" requirements.txt; then
  echo "📦 Добавляем python-dotenv в requirements.txt"
  echo "python-dotenv" >> requirements.txt
fi

# Сборка Docker-образа
docker build -t linkbot .

# Запуск контейнера
docker run -d \
  --name linkbot \
  --env-file .env \
  -v $(pwd):/app \
  -w /app \
  linkbot \
  python bot.py

# Настройка автозапуска через systemd
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
systemctl restart linkbot

echo -e "\n✅ Бот установлен и запущен. Проверь его в Telegram."
