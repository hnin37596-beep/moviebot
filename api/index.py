import os
import json
import requests
from flask import Flask, request
from pymongo import MongoClient

app = Flask(__name__)

API_TOKEN = '8979764017:AAGN1zIQ7rChC0cCOOebD1zIZlBMg0Y2THQ'
ADMIN_ID = 5935978007
MONGO_URI = 'mongodb+srv://mybotadmin:pass1237867@cluster0.apznmvp.mongodb.net/?appName=Cluster0'

BASE_URL = f"https://api.telegram.org/bot{API_TOKEN}"

try:
    client = MongoClient(MONGO_URI)
    db = client['telegram_bot_db']
    users_collection = db['users']
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

def add_user(user_id):
    try:
        if not users_collection.find_one({"user_id": user_id}):
            users_collection.insert_one({"user_id": user_id})
    except Exception as e:
        print(f"Error adding user: {e}")

def get_all_users():
    try:
        return [row['user_id'] for row in users_collection.find({}, {"_id": 0, "user_id": 1})]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup: payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

@app.route('/', methods=['POST'])
def webhook():
    update = request.get_json()
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        
        if "text" in message:
            text = message["text"]
            if text == "/start":
                add_user(chat_id)
                
                welcome_buttons = {
                    "inline_keyboard": [
                        [{"text": "🔗 Join Channel 🍓", "url": "https://t.me/your_channel_username"}],
                        [{"text": "🔄 Try Again", "url": f"https://t.me/your_bot_username?start=retry"}]
                    ]
                }
                
                # 📝 စာသားထဲက 🔥 နေရာတွေမှာ Premium Emoji အစားထိုးဝင်ပါလိမ့်မယ်
                welcome_text = (
                    "🔥 Welcome to MovieBot 🔥\n\n"
                    "မင်္ဂလာပါရှင် ရုပ်ရှင်ချစ်ပရိသတ်တို့ရေ 🎬🍿\n"
                    "ရုပ်ရှင်အသစ်စက်စက်လေးတွေနဲ့ Movie Link တွေကို ဒီမှာ အမြဲတင်ပေးသွားမှာမို့လို့ စောင့်မျှော်ပေးကြပါဦးနော် 🥰✨\n\n"
                    "လင့်ခ်တွေကို အမြန်ဆုံးသိရအောင် အောက်က 👉 Join Channel ကိုနှိပ်ပြီး Channel ထဲဝင်ထားပေးပါဦးရှင် ချစ်မွတ်စ် 💋"
                )
                
                # 🚀 YouTube Shorts ထဲကအတိုင်း Entities စနစ်ကို သုံးပြီး Premium Emoji ပို့ခြင်း
                payload = {
                    "chat_id": chat_id,
                    "photo": "https://i.ibb.co/R4G6VCG5/IMG-20260516-213712.png",
                    "caption": welcome_text,
                    "caption_entities": [
                        {
                            "type": "custom_emoji",
                            "offset": 0,          # ပထမဆုံး '🔥' နေရာ
                            "length": 2,
                            "custom_emoji_id": "5445284000302111844"  # Premium Star Emoji ID
                        },
                        {
                            "type": "custom_emoji",
                            "offset": 28,         # ဒုတိယ '🔥' နေရာ (girls ပြီးရင် လာမယ့်နေရာ)
                            "length": 2,
                            "custom_emoji_id": "5415840243299392211"  # Premium Heart Emoji ID
                        }
                    ],
                    "reply_markup": welcome_buttons
                }
                
                # sendPhoto API ထံ တိုက်ရိုက် လှမ်းပို့လိုက်ခြင်း
                requests.post(f"{BASE_URL}/sendPhoto", json=payload)
                
            elif text.startswith("/post"):
                if chat_id == ADMIN_ID:
                    post_text = text.partition(' ')[2]
                    if post_text:
                        user_list = get_all_users()
                        for u_id in user_list: send_message(u_id, post_text)
                        send_message(chat_id, f"✅ စာသား Post ကို ပို့ပြီးပါပြီ။")
                        
        elif "photo" in message:
            caption = message.get("caption", "")
            photo_id = message["photo"][-1]["file_id"]
            if chat_id == ADMIN_ID and caption.startswith("/post"):
                post_text = caption.partition(' ')[2]
                user_list = get_all_users()
                url = f"{BASE_URL}/sendPhoto"
                for u_id in user_list:
                    requests.post(url, json={"chat_id": u_id, "photo": photo_id, "caption": post_text})
                send_message(chat_id, f"✅ ပုံ Post ကို ပို့ပြီးပါပြီ။")
                
    return "OK", 200
