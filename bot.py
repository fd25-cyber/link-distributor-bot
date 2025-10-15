import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_IDS

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
DATA_FILE = "data.json"

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@dp.message(Command("get"))
async def handle_get(msg: types.Message):
    data = load_data()
    if not data["available"]:
        await msg.answer("Нет доступных ссылок.")
        return

    link = data["available"].pop(0)
    user_id = msg.from_user.id
    username = msg.from_user.username or str(user_id)
    data["used"].append({
        "link": link,
        "user": username,
        "date": msg.date.isoformat()
    })
    save_data(data)

    await msg.answer(f"Ваша ссылка:\n{link}")
    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, f"{username} получил ссылку: {link}")

@dp.message(Command("list_used"))
async def handle_list(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    data = load_data()
    text = "\n".join([f"{u['date']} — {u['user']} — {u['link']}" for u in data["used"]]) or "Нет занятых ссылок."
    await msg.answer(text)

@dp.message(Command("delete"))
async def handle_delete(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Укажите ссылку для удаления.")
        return
    link_to_delete = parts[1]
    data = load_data()
    entry = next((u for u in data["used"] if u["link"] == link_to_delete), None)
    if entry:
        data["used"].remove(entry)
        save_data(data)
        await msg.answer("Ссылка удалена.")
        await bot.send_message(msg.from_user.id, f"Ссылка {link_to_delete} удалена.")
    else:
        await msg.answer("Ссылка не найдена.")

@dp.message(Command("add"))
async def handle_add(msg: types.Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Укажите ссылку для добавления.")
        return
    new_link = parts[1]
    data = load_data()
    data["available"].append(new_link)
    save_data(data)
    await msg.answer("Ссылка добавлена.")

@dp.message()
async def fallback(msg: types.Message):
    await msg.answer("Команды: /get, /list_used, /delete <ссылка>, /add <ссылка>")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
