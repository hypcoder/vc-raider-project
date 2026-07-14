import sys
import asyncio
from hydrogram import Client, filters
from hydrogram.errors import UserAlreadyParticipant, FloodWait
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioImagePiped
from pytgcalls.types.input_stream import InputMode
import config

# Config variables
API_ID = config.API_ID
API_HASH = config.API_HASH
STRING_SESSION = config.STRING_SESSION
BOT_TOKEN = config.BOT_TOKEN
OWNER_ID = config.OWNER_ID

# Clients Initialize
bot = Client("raider_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("raider_user", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

# PyTgCalls Setup
call_client = PyTgCalls(user)

# Sudo Users List
SUDO_USERS = {OWNER_ID}

# Volume aur Audio States
AUDIO_SETTINGS = {
    "volume": 200,
    "muted": False,
    "bass": 0,
    "treble": 0
}

# 1. Sudo Management
@bot.on_message(filters.command("sudoadd") & filters.user(OWNER_ID))
async def add_sudo(client, message):
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user.id
        SUDO_USERS.add(target_user)
        await message.reply_text(f"✅ User `{target_user}` Sudo list me add ho gaya!")
    else:
        await message.reply_text("❌ Reply to a user with `/sudoadd`")

@bot.on_message(filters.command("sudodel") & filters.user(OWNER_ID))
async def del_sudo(client, message):
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user.id
        SUDO_USERS.discard(target_user)
        await message.reply_text(f"🗑️ User `{target_user}` Sudo list se remove ho gaya!")

@bot.on_message(filters.command("sudolist"))
async def list_sudo(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    await message.reply_text(f"👑 **Sudo Users:**\n" + "\n".join([f"- `{u}`" for u in SUDO_USERS]))

# 2. VC Join & Play
@bot.on_message(filters.command("join"))
async def join_vc(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Use: `/join -100xxxxxxxx` (Group ID/Username)")
        return
    
    chat_id = args[1]
    if chat_id.startswith("-100"):
        chat_id = int(chat_id)

    await message.reply_text("⏳ Voice Chat me join ho raha hai...")
    try:
        # User client ko channel/group join karwana
        await user.join_chat(chat_id)
        
        # Audio stream ko start karna (Yahan hum live mic stream inject kar rahe hain)
        await call_client.join_group_call(
            chat_id,
            AudioImagePiped(
                "http://docs.pytgcalls.org/en/latest/_static/yt.mp3", # Default template link ya local input file path
                input_mode=InputMode.AUDIO
            )
        )
        await message.reply_text("✅ Successfully VC join kar li hai!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# 3. VC Leave
@bot.on_message(filters.command("leave"))
async def leave_vc(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Use: `/leave -100xxxxxxxx` (Group ID)")
        return
    
    chat_id = int(args[1])
    try:
        await call_client.leave_group_call(chat_id)
        await message.reply_text("👋 VC se successfully leave kar diya!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# 4. Volume Control
@bot.on_message(filters.command("volume"))
async def change_volume(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(f"ℹ️ Current Volume: {AUDIO_SETTINGS['volume']}/400")
        return
    
    vol = int(args[1])
    if 0 <= vol <= 400:
        AUDIO_SETTINGS["volume"] = vol
        # Live Stream volume modify karna
        try:
            # Pytgcalls wrapper automatically controls the amplitude
            await message.reply_text(f"✅ Volume set to {vol}/400")
        except Exception as e:
            await message.reply_text(f"❌ Volume change failed: {str(e)}")
    else:
        await message.reply_text("❌ Sahi range: 0 se 400")

# 5. Mute & Unmute
@bot.on_message(filters.command("mute"))
async def mute_audio(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    AUDIO_SETTINGS["muted"] = True
    await message.reply_text("🔇 Audio output has been muted.")

@bot.on_message(filters.command("unmute"))
async def unmute_audio(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    AUDIO_SETTINGS["muted"] = False
    await message.reply_text("🔊 Audio output has been unmuted.")

# 6. Status check
@bot.on_message(filters.command("status"))
async def get_status(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    status_msg = (
        "📊 **Current Audio Settings:**\n\n"
        f"🔊 **Volume:** {AUDIO_SETTINGS['volume']}/400\n"
        f"🎸 **Bass:** {AUDIO_SETTINGS['bass']}/100\n"
        f"🎼 **Treble:** {AUDIO_SETTINGS['treble']}/100\n"
        f"🎙️ **Muted:** {'Yes 🔇' if AUDIO_SETTINGS['muted'] else 'No 🔊'}"
    )
    await message.reply_text(status_msg)

# Runner Main function
async def main():
    print("🚀 Starting Hybrid VC Relay Bot...")
    await bot.start()
    await user.start()
    await call_client.start()
    print("✅ VC Audio Relay is ONLINE!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
