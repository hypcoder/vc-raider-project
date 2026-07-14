import sys
import asyncio

# Python 3.14+ loop issue fix strictly before importing hydrogram
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from hydrogram import Client, filters
from hydrogram.errors import UserAlreadyParticipant, FloodWait

# Config file ko import karna
import config

# Config se direct data load karna
API_ID = config.API_ID
API_HASH = config.API_HASH
STRING_SESSION = config.STRING_SESSION
BOT_TOKEN = config.BOT_TOKEN
OWNER_ID = config.OWNER_ID
SOURCE_CHAT = config.SOURCE_CHAT

# Clients Initialize karna (Ab ye direct config se correct details uthayenge)
bot = Client("raider_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("raider_user", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

# Sudo Users List (By default Owner add hai)
SUDO_USERS = {OWNER_ID}

# 1. .sudo Command (Reply karke kisi ko sudo dene ke liye)
@bot.on_message(filters.command("sudo", prefixes=".") & filters.user(OWNER_ID))
async def add_sudo(client, message):
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user.id
        SUDO_USERS.add(target_user)
        await message.reply_text(f"✅ User `{target_user}` ko Sudo list me jod diya gaya hai bbu!")
    else:
        await message.reply_text("❌ Kisi ke message par reply karke `.sudo` likho!")

# 2. /join Command (Target group ki VC join karne ke liye)
@bot.on_message(filters.command("join") & filters.incoming)
async def join_vc(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Sahi tarika: `/join [Group_Username_Ya_Link]`")
        return
    
    target = args[1]
    await message.reply_text("⏳ Userbot ko join karwaya jaa raha hai...")
    
    try:
        await user.join_chat(target)
        await message.reply_text("✅ Userbot successfully group me join ho gaya hai!")
    except UserAlreadyParticipant:
        await message.reply_text("ℹ️ Userbot pehle se hi us group me hai.")
    except FloodWait as e:
        await message.reply_text(f"⚠️ FloodWait error! {e.value} seconds baad try karein.")
    except Exception as e:
        await message.reply_text(f"❌ Error aaya: {str(e)}")

# 3. /leave Command (Group chhodne ke liye)
@bot.on_message(filters.command("leave") & filters.incoming)
async def leave_chat(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Sahi tarika: `/leave [Group_Username_Ya_ID]`")
        return
    
    target = args[1]
    try:
        await user.leave_chat(target)
        await message.reply_text(f"👋 Userbot ne `{target}` group chhod diya hai.")
    except Exception as e:
        await message.reply_text(f"❌ Error aaya: {str(e)}")

# Dono clients ko ek sath start karne ka main function
async def main():
    print("🚀 Starting Bot and Userbot...")
    await bot.start()
    await user.start()
    print("✅ Bot and Userbot are now ONLINE!")
    # Keep running until interrupted
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Stopping...")
                                                       
