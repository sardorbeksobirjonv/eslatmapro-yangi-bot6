from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import asyncio

# ================= TOKEN =================
TOKEN = "8528647202:AAHQOrW3p8M0uLTTTDF_M2LKtSqVAs92Mvw"

# ================= STATES =================
(
    TIL,
    KONTAKT,
    MINTQA,
    TUR,
    TARGET_ID,
    VAQT,
    MATN,
    QAYTA,
    MENU,
    TAHRIR_ID,
    TAHRIR_TURI,
    TAHRIR_KIRITISH,
) = range(12)

users = {}

# ================= TIME ZONES =================
ZONE_MAP = {
    "toshkent": "Asia/Tashkent",
    "tashkent": "Asia/Tashkent",
    "ташкент": "Asia/Tashkent",

     # 🇷🇺 RUSIYA (Moskva)
    "moskva": "Europe/Moscow",
    "москва": "Europe/Moscow",

    # 🇺🇸 AQSH (New York)
    "new york": "America/New_York",
    "ny": "America/New_York",
    "нью-йорк": "America/New_York",

    # 🇹🇷 TURKIYA (Istanbul)
    "istanbul": "Europe/Istanbul",
    "истамбул": "Europe/Istanbul",

    # 🇯🇵 YAPONIYA (Tokyo)
    "tokio": "Asia/Tokyo",
    "tokyo": "Asia/Tokyo",
    "токио": "Asia/Tokyo",

    # 🇩🇪 GERMANIYA (Berlin)
    "berlin": "Europe/Berlin",
    "берлин": "Europe/Berlin",

    # 🇬🇧 ANGLIYA (London)
    "london": "Europe/London",
    "лондон": "Europe/London",

    # 🇫🇷 FRANSIYA (Paris)
    "paris": "Europe/Paris",
    "париж": "Europe/Paris",

    # 🇦🇪 BAA (Dubai)
    "dubai": "Asia/Dubai",
    "дубай": "Asia/Dubai",

    # 🇨🇳 XITOY (Beijing)
    "beijing": "Asia/Shanghai",
    "pekin": "Asia/Shanghai",
    "пекин": "Asia/Shanghai",
}

REPEAT = {
    "Hech qachon": None,
    "Har kun": timedelta(days=1),
    "Har 2 hafta": timedelta(weeks=2),        # ✅ YANGI
    "Har hafta": timedelta(weeks=1),
    "Har oy": timedelta(days=30),
    "Choraklik (3 oy)": timedelta(days=90), # ✅ YANGI
    "Har 6 oy": timedelta(days=180),        # ✅ YANGI
    "Har yil": timedelta(days=365),         # ✅ YANGI
}

# ================= HELPERS =================
def parse_chat_id(text: str):
    text = text.strip()

    # 1️⃣ Raqam bo‘lsa
    try:
        return int(text)
    except:
        pass

    # 2️⃣ @username bo‘lsa
    if text.startswith("@"):
        return text

    # 3️⃣ Ochiq guruh/kanal linki bo‘lsa → @username ga aylantiramiz
    if text.startswith("https://t.me/") and "+" not in text:
        username = text.replace("https://t.me/", "")
        return "@" + username

    # 4️⃣ Maxfiy invite link
    if text.startswith("https://t.me/+"):
        return "PRIVATE_LINK"

    return None


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # Agar foydalanuvchi allaqachon ro'yxatdan o'tgan bo'lsa
    if uid in users:
        await menu(update, context)  # to‘g‘ridan-to‘g‘ri menyuga o‘tadi
        return MENU

    # Yangi foydalanuvchi sifatida boshlash
    users[uid] = {
        "reminders": [],
        "tz": ZoneInfo("Asia/Tashkent"),
        "lang": "O‘zbekcha",
    }

    # Til tanlash menyusi
    await update.message.reply_text(
        "👋 Assalomu alaykum!\nMen sizga kerakli vaqtda eslatmalar yuboruvchi botman.\nQuyidagi tilni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            [["🇺🇿 O‘zbekcha", "🇷🇺 Русский"]],
            resize_keyboard=True
        )
    )

    return TIL
# ================= LANGUAGE =================
async def til(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid]["lang"] = update.message.text

    await update.message.reply_text(
        "🌍 Mintaqani yozing (masalan: Tashkent)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return MINTQA


# ================= CONTACT =================
async def kontakt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Mintaqani yozing (masalan: Tashkent)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return MINTQA

# ================= REGION =================
async def mintqa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.lower()

    if text in ZONE_MAP:
        users[uid]["tz"] = ZoneInfo(ZONE_MAP[text])
        return await menu(update, context)

    await update.message.reply_text("❌ Mintaqa topilmadi, qayta yozing")
    return MINTQA

# ================= MENU =================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Asosiy menyu",
        reply_markup=ReplyKeyboardMarkup(
            [["➕ Yangi eslatma"], ["📋 Ro‘yxat"]], resize_keyboard=True
        ),
    )
    return MENU

# ================= MENU HANDLER =================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users[uid]
    text = update.message.text

    if text == "➕ Yangi eslatma":
        await update.message.reply_text(
            "🔔 Еслатма турини танланг\nИлтимос, қуйидаги вариантлардан бирини танланг\n👤 Шахсий — еслатма фақат сизга кўринади\n👥 Гуруҳ — еслатма гуруҳда ишлайди/n📢 Канал — еслатма каналга юборилади\n📘 Қўлланма — ботдан қандай фойдаланишни билиш\nҚўлланмани очиш: https://t.me/your_manual_link",
            reply_markup=ReplyKeyboardMarkup(
                [["👤 Shaxsiy"], ["👥 Guruh"], ["📢 Kanal"]],
                resize_keyboard=True,
            ),
        )
        return TUR

    if text == "📋 Ro‘yxat":
        if not user["reminders"]:
            await update.message.reply_text("📭 Eslatmalar yo‘q")
            return MENU

        buttons = [
            [f"{r['text']} | {r['time'].strftime('%d.%m.%Y %H:%M')}"]
            for r in user["reminders"]
        ]
        await update.message.reply_text(
            "✏️ Eslatmani tahrirlash uchun quyidagilardan birini tanlang va osha eslatma taxrilandi:",
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True),
        )
        return TAHRIR_ID

    return MENU

# ================= TYPE =================
async def tur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users[uid]
    text = update.message.text.lower()

    if "shaxsiy" in text:
        user["current"] = {"type": "private"}
    elif "guruh" in text:
        user["current"] = {"type": "group"}
    elif "kanal" in text:
        user["current"] = {"type": "channel"}
    else:
        await update.message.reply_text("❌ Noto‘g‘ri tanlov")
        return TUR

    if user["current"]["type"] in ["group", "channel"]:
        await update.message.reply_text(
            "🆔 Guruh/Kanal ID yoki @username kiriting\n"
            "Masalan:\n-1001234567890\n@my_channel"
        )
        return TARGET_ID

    await update.message.reply_text("⏰ Eslatma qo‘yish\n📅 Sana va vaqtni quyidagi formatda kiriting:\nDD.MM.YYYY HH:MM\n📝 Qanday yozish kerak?\n— Kun.oy.yil va soat:daqiqa\n— 24 soatlik formatda\n📌 Misol:\n25.01.2026 18:30")
    return VAQT

# ================= TARGET =================
async def target_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    chat_id = parse_chat_id(text)

    if chat_id == "PRIVATE_LINK":
        await update.message.reply_text(
            "❌ Bu maxfiy guruh invite linki.\n\n"
            "📌 Bot invite link bilan ishlamaydi.\n"
            "✅ Botni guruhga qo‘shing va `-100...` ID kiriting."
        )
        return TARGET_ID

    if chat_id is None:
        await update.message.reply_text(
            "❌ Noto‘g‘ri format.\n"
            "Yuboring:\n"
            "• -100xxxxxxxxxx\n"
            "• @username\n"
            "• https://t.me/username"
        )
        return TARGET_ID

    users[uid]["current"]["target_id"] = chat_id

    await update.message.reply_text(
        "⏰ Sana va vaqtni kiriting:\nDD.MM.YYYY HH:MM\n\nMisol: 25.01.2026 18:30"
    )
    return VAQT

# ================= TIME =================
async def vaqt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        dt = datetime.strptime(update.message.text, "%d.%m.%Y %H:%M")
    except:
        await update.message.reply_text("❌ Format noto‘g‘ri")
        return VAQT

    users[uid]["current"]["time"] = dt
    await update.message.reply_text("✏️ Eslatma matnini kiriting")
    return MATN

# ================= TEXT =================
async def matn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid]["current"]["text"] = update.message.text

    await update.message.reply_text(
    "🔁 Takrorlansinmi?",
    reply_markup=ReplyKeyboardMarkup(
        [
            ["Hech qachon", "Har kun", "Har 2 hafta"],
            ["Har hafta", "Har oy"],
            ["Choraklik (3 oy)", "Har 6 oy"],
            ["Har yil"],
        ],
        resize_keyboard=True,
    ),
)
    return QAYTA

# ================= SAVE =================
async def qayta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users[uid]
    cur = user["current"]

    cur["repeat"] = REPEAT.get(update.message.text)
    cur["id"] = len(user["reminders"]) + 1
    cur["task"] = asyncio.create_task(schedule(uid, cur, context))

    user["reminders"].append(cur)
    user.pop("current")

    await update.message.reply_text("✅ Eslatma saqlandi")
    return await menu(update, context)

# ================= SCHEDULE =================
async def schedule(uid, r, context):
    if uid not in users:
        return

    while True:
        if uid not in users:
            return

        tz = users[uid]["tz"]
        now = datetime.now(tz)
        target = r["time"].replace(tzinfo=tz)

async def schedule(uid, r, context):
    tz = users[uid]["tz"]

    while True:
        now = datetime.now(tz)
        target = r["time"].replace(tzinfo=tz)

        if target <= now:
            if not r["repeat"]:
                return
            target += r["repeat"]

        await asyncio.sleep(max(1, (target - now).total_seconds()))


        chat_id = uid if r["type"] == "private" else r["target_id"]

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⏰ Eslatma:\n\n{r['text']}",
            )
        except Exception as e:
            print("XATOLIK:", e)

        if not r["repeat"]:
            return

        r["time"] = target

# ================= EDIT =================
async def tahrir_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    for r in users[uid]["reminders"]:
        if r["text"] in text:
            users[uid]["edit"] = r
            break
    else:
        return await menu(update, context)

    await update.message.reply_text(
        "✏️ Nimani o‘zgartiramiz?",
        reply_markup=ReplyKeyboardMarkup(
            [["Matn"], ["Vaqt"], ["O‘chirish"]],
            resize_keyboard=True,
        ),
    )
    return TAHRIR_TURI

async def tahrir_turi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    choice = update.message.text.lower()

    if "o‘chirish" in choice:
        users[uid]["edit"]["task"].cancel()
        users[uid]["reminders"].remove(users[uid]["edit"])
        users[uid].pop("edit")
        return await menu(update, context)

    users[uid]["edit_type"] = choice
    await update.message.reply_text("Yangi qiymatni kiriting", reply_markup=ReplyKeyboardRemove())
    return TAHRIR_KIRITISH

async def tahrir_kirit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    r = users[uid]["edit"]

    if "vaqt" in users[uid]["edit_type"]:
        r["time"] = datetime.strptime(update.message.text, "%d.%m.%Y %H:%M")
    else:
        r["text"] = update.message.text

    r["task"].cancel()
    r["task"] = asyncio.create_task(schedule(uid, r, context))

    users[uid].pop("edit")
    return await menu(update, context)

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        TIL: [MessageHandler(filters.TEXT, til)],  # start emas, til funksiyasi
        MINTQA: [MessageHandler(filters.TEXT, mintqa)],
        MENU: [MessageHandler(filters.TEXT, menu_handler)],
        TUR: [MessageHandler(filters.TEXT, tur)],
        TARGET_ID: [MessageHandler(filters.TEXT, target_id)],
        VAQT: [MessageHandler(filters.TEXT, vaqt)],
        MATN: [MessageHandler(filters.TEXT, matn)],
        QAYTA: [MessageHandler(filters.TEXT, qayta)],
        TAHRIR_ID: [MessageHandler(filters.TEXT, tahrir_id)],
        TAHRIR_TURI: [MessageHandler(filters.TEXT, tahrir_turi)],
        TAHRIR_KIRITISH: [MessageHandler(filters.TEXT, tahrir_kirit)],
    },
    fallbacks=[CommandHandler("start", start)],
    allow_reentry=True,
)
    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()
