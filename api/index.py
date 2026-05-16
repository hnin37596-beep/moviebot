import os
import json
import requests
from flask import Flask, request
from pymongo import MongoClient

app = Flask(__name__)

API_TOKEN = '8979764017:AAGN1zIQ7rChC0cCOOebD1zIZlBMg0Y2THQ'  # သင့် Bot Token ပြောင်းရန်
ADMIN_ID = 5935978007  # သင့် Telegram ID ပြောင်းရန်
MONGO_URI = 'mongodb+srv://mybotadmin:pass1237867@cluster0.apznmvp.mongodb.net/?appName=Cluster0'  # MongoDB မှ ရလာသော လင့်ခ်

BASE_URL = f"https://api.telegram.org/bot{API_TOKEN}"

# 🔌 MongoDB ချိတ်ဆက်ခြင်း
try:
    client = MongoClient(MONGO_URI)
    db = client['telegram_bot_db']
    users_collection = db['users']
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

# Database ထဲ User ID သိမ်းခြင်း
def add_user(user_id):
    try:
        if not users_collection.find_one({"user_id": user_id}):
            users_collection.insert_one({"user_id": user_id})
    except Exception as e:
        print(f"Error adding user: {e}")

# User အားလုံးကို Database ထဲမှ ဆွဲထုတ်ခြင်း
def get_all_users():
    try:
        return [row['user_id'] for row in users_collection.find({}, {"_id": 0, "user_id": 1})]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup: payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

def send_photo(chat_id, photo_id, caption, reply_markup=None):
    url = f"{BASE_URL}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_id, "caption": caption, "parse_mode": "Markdown"}
    if reply_markup: payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

@app.route('/', methods=['POST'])
def webhook():
    update = request.get_json()
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        
        # ----------------------------------------------------
        # (၁) စာသား ရောက်လာလျှင် (/start နှိပ်လျှင်)
        # ----------------------------------------------------
        if "text" in message:
            text = message["text"]
            if text == "/start":
                add_user(chat_id)
                
                # ပုံထဲကအတိုင်း Inline Buttons ခလုတ်များ ပြင်ဆင်ခြင်း
                welcome_buttons = {
                    "inline_keyboard": [
                        [{"text": "🔗 Join Channel 🍓", "url": "https://t.me/your_channel_username"}],
                        [{"text": "🔄 Try Again", "url": f"https://t.me/your_bot_username?start=retry"}]
                    ]
                }
                
                welcome_text = "✨ **𝖶𝖾𝗅𝖼𝗈𝗆𝖾 𝗍𝗈 𝖬𝗈𝗏𝗂𝖾𝖡𝗈𝗍 𝗀𝗂𝗋𝗅𝗌** 💖

**မင်္ဂလာပါရှင်... ရုပ်ရှင်ချစ်ပရိသတ်တို့ရေ** 🎬🍿
ရုပ်ရှင်အသစ်စက်စက်လေးတွေနဲ့ စိတ်လှုပ်ရှားစရာ **Movie Link** တွေကို ဒီ Bot လေးထဲမှာ အမြဲတမ်း တင်ပေးသွားမှာမို့လို့ စောင့်မျှော်ပေးကြပါဦးနော် 🥰✨

**စိတ်ချမ်းသာစရာ ရုပ်ရှင်ကြည့်ချိန်လေး ဖြစ်ပါစေရှင်** 🎀🧸
"
                
                # အစ်ကိုပြထားတဲ့ ပုံစံအတိုင်း Welcome Message မှာ ပြချင်တဲ့ပုံရဲ့ File ID ကို အောက်ကနေရာမှာ ထည့်ပါမယ်
                # လောလောဆယ် စမ်းသပ်ရန် အလှပုံလင့်ခ်တစ်ခု ထည့်ပေးထားပါတယ်
                sample_photo = "https://i.ibb.co/R4G6VCG5/IMG-20260516-213712.png"
                send_photo(chat_id, sample_photo, welcome_text, reply_markup=welcome_buttons)
                
            elif text.startswith("/post"):
                if chat_id == ADMIN_ID:
                    post_text = text.partition(' ')[2]
                    if post_text:
                        user_list = get_all_users()
                        for u_id in user_list: send_message(u_id, post_text)
                        send_message(chat_id, f"✅ စာသား Post ကို User {len(user_list)} ယောက်ဆီ ပို့ပြီးပါပြီ။")
                        
        # ----------------------------------------------------
        # (၂) Admin က ပုံနှင့်စာတွဲလျက် Post တင်လာလျှင်
        # ----------------------------------------------------
        elif "photo" in message:
            caption = message.get("caption", "")
            photo_id = message["photo"][-1]["file_id"]
            if chat_id == ADMIN_ID and caption.startswith("/post"):
                post_text = caption.partition(' ')[2]
                user_list = get_all_users()
                for u_id in user_list: send_photo(u_id, photo_id, post_text)
                send_message(chat_id, f"✅ ပုံ Post ကို User {len(user_list)} ယောက်ဆီ ပို့ပြီးပါပြီ။")
                
    return "OK", 200
