import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import BOT_TOKEN, ADMIN_IDS, DATA_FILE

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@dp.message(Command("start"))
async def handle_start(msg: Message):
    if msg.from_user.id in ADMIN_IDS:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📋 Список", callback_data="list_used")],
                [InlineKeyboardButton(text="➕ Добавить", callback_data="add_link")],
                [InlineKeyboardButton(text="❌ Удалить", callback_data="delete_link")],
                [InlineKeyboardButton(text="📊 Статус", callback_data="status")]
            ]
        )
        await msg.answer("Вы администратор. Выберите действие:", reply_markup=kb)
    else:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Получить", callback_data="get_link")]]
        )
        await msg.answer("Нажмите кнопку, чтобы получить ссылку:", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "get_link")
async def handle_get_callback(callback: CallbackQuery):
    data = load_data()
    if not data["available"]:
        await callback.message.answer("Нет доступных ссылок.")
        return

    entry = data["available"].pop(0)
    name = entry["name"]
    link = entry["link"]
    username = callback.from_user.username or str(callback.from_user.id)

    data["used"].append({
        "name": name,
        "link": link,
        "user": username,
        "date": callback.message.date.isoformat()
    })
    save_data(data)

    await callback.message.answer(f"🔗 *{name}*\n`{link}`", parse_mode="Markdown")

    for admin_id in ADMIN_IDS:
        await bot.send_message(admin_id, f"{username} получил ссылку: {name}")

@dp.callback_query(lambda c: c.data == "list_used")
async def handle_list_callback(callback: CallbackQuery):
    data = load_data()
    text = "\n".join([
        f"{i+1}. {u['date']} — {u['user']} — {u['name']}"
        for i, u in enumerate(data["used"])
    ]) or "Нет выданных ссылок."
    await callback.message.answer(text)

@dp.callback_query(lambda c: c.data == "status")
async def handle_status_callback(callback: CallbackQuery):
    data = load_data()
    total_available = len(data["available"])
    total_used = len(data["used"])
    last_entry = data["used"][-1] if data["used"] else None

    text = f"📊 Статус:\n• Доступно: {total_available}\n• Выдано: {total_used}"
    if last_entry:
        text += f"\n🕓 Последняя выдача:\n{last_entry['date']} — {last_entry['user']} — {last_entry['name']}"
    await callback.message.answer(text)

@dp.callback_query(lambda c: c.data == "add_link")
async def prompt_add_link(callback: CallbackQuery):
    await callback.message.answer("Отправьте ссылку для добавления в формате:\n`/add <название> <ссылка>`", parse_mode="Markdown")

@dp.message(Command("add"))
async def handle_add(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    parts = msg.text.split(maxsplit=2)
    if len(parts) < 3:
        await msg.answer("Формат: /add <название> <ссылка>")
        return
    name, link = parts[1], parts[2]
    data = load_data()
    data["available"].append({"name": name, "link": link})
    save_data(data)
    await msg.answer(f"Добавлено: {name}")

@dp.callback_query(lambda c: c.data == "delete_link")
async def prompt_delete_link(callback: CallbackQuery):
    await callback.message.answer("Отправьте номер для удаления:\n`/delete <номер>`", parse_mode="Markdown")

@dp.message(Command("delete"))
async def handle_delete(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    parts = msg.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await msg.answer("Используй: /delete <номер>")
        return
    index = int(parts[1]) - 1
    data = load_data()
    if 0 <= index < len(data["used"]):
        entry = data["used"].pop(index)
        save_data(data)
        await msg.answer(f"Удалено: {entry['name']}")
    else:
        await msg.answer("Неверный номер.")

@dp.message(lambda msg: not msg.text.startswith("/"))
async def fallback(msg: Message):
    if msg.from_user.id in ADMIN_IDS:
        await handle_start(msg)
    else:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Получить", callback_data="get_link")]]
        )
        await msg.answer("Нажмите кнопку, чтобы получить ссылку:", reply_markup=kb)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
