# Telegram Link Distributor Bot

Бот для выдачи VPN/Proxy ссылок по кнопке в Telegram. Поддерживает нестандартные схемы (`vless://`, `ss://`, `trojan://`), админ-панель через кнопки, логирование выдачи и удаление.

## Команды

- `/start` — запуск
- `/add <название> <ссылка>` — добавить ссылку
- `/delete <номер>` — удалить выданную
- `/list_used` — список выданных
- `/status` — статистика

## Установка

```bash
docker run -d \
  --name linkbot \
  -v /root/link_bot:/app \
  -w /app \
  link_bot_linkbot \
  python bot.py
