import sys
import asyncio

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from hydrogram import Client, filters
from hydrogram.errors import UserAlreadyParticipant, FloodWait
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioImagePiped
from pytgcalls.types.input_stream import InputMode
import config

API_ID = config.API_ID
API_HASH = config.API_HASH
STRING_SESSION = config.STRING_SESSION
BOT_TOKEN = config.BOT_TOKEN
OWNER_ID = config.OWNER_ID

bot = Client("raider_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("raider_user", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
call_client = PyTgCalls(user)

SUDO_USERS = {OWNER_ID}
AUDIO_SETTINGS = {
    "volume": 200,
    "gain": 5,
    "muted": False,
    "bass": 0,
    "treble": 0
}

@bot.on_message(filters.command("sudoadd", prefixes="/") & filters.user(OWNER_ID))
async def add_sudo(client, message):
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user.id
        SUDO_USERS.add(target_user)
        await message.reply_text(f"✅ User `{target_user}` ko Sudo list me jod diya gaya hai!")
    else:
        await message.reply_text("❌ Kisi ke message par reply karke `/sudoadd` likho!")

@bot.on_message(filters.command("sudodel", prefixes="/") & filters.user(OWNER_ID))
async def del_sudo(client, message):
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user.id
        SUDO_USERS.discard(target_user)
        await message.reply_text(f"🗑️ User `{target_user}` ko Sudo list se hata diya gaya hai!")
    else:
        await message.reply_text("❌ Kisi ke message par reply karke `/sudodel` likho!")

@bot.on_message(filters.command("sudolist", prefixes="/") & filters.incoming)
async def list_sudo(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    mentions = "\n".join([f"- `{u}`" for u in SUDO_USERS])
    await message.reply_text(f"👑 **Sudo Users List:**\n{mentions}")

@bot.on_message(filters.command("join", prefixes="/") & filters.incoming)
async def join_vc(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Sahi tarika: `/join [Target_Chat_ID]`\nExample: `/join -1003501428752`")
        return
    
    target = args[1]
    status_msg = await message.reply_text(f"⏳ Process start ho raha hai target: `{target}` ...")
    
    chat_id = None

    # Step 1: ID ko number me convert karna
    try:
        chat_id = int(target)
    except ValueError:
        # Agar galti se link de diya
        try:
            chat = await user.join_chat(target)
            chat_id = chat.id
        except UserAlreadyParticipant:
            if not target.startswith("http"):
                chat = await user.get_chat(target)
                chat_id = chat.id
            else:
                await status_msg.edit_text("⚠️ Userbot is private group me pehle se hai.\n👉 **Bhai, link ki jagah us group ki ID (-100...) use karo.**")
                return
        except Exception as e:
            await status_msg.edit_text(f"❌ Error: {str(e)}")
            return

    # Step 2: PEER_ID_INVALID Cache Fix (Yahi asli jad thi)
    try:
        await user.get_chat(chat_id)
    except Exception as e:
        if "PEER_ID_INVALID" in str(e):
            await status_msg.edit_text("🔄 Memory refresh kar rahe hain (PEER Fix)...")
            async for _ in user.get_dialogs(limit=50):
                pass 
            try:
                await user.get_chat(chat_id)
            except Exception as e2:
                await status_msg.edit_text(f"❌ Refresh ke baad bhi ID nahi mili. Userbot ko group me thoda active karo ya message bhejo. Error: {e2}")
                return
        else:
            await status_msg.edit_text(f"❌ Chat find error: {str(e)}")
            return

    # Step 3: PyTgCalls VC Connection
    try:
        try:
            await call_client.leave_group_call(chat_id)
        except:
            pass

        await call_client.join_group_call(
            chat_id,
            AudioImagePiped(
                "https://raw.githubusercontent.com/userland-org/assets/main/silent.mp3",
                input_mode=InputMode.AUDIO
            )
        )
        await status_msg.edit_text(f"🎉 **Boom!** Userbot smoothly target `{chat_id}` ki VC me join ho gaya hai!")
        
    except FloodWait as e:
        await status_msg.edit_text(f"⚠️ Telegram ne rok diya! {e.value} seconds baad try karna.")
    except Exception as vc_err:
        await status_msg.edit_text(f"❌ VC Join me dikkat aayi!\nError: `{str(vc_err)}`\n\n**Tip:** Ensure karo VC manually started hai.")

@bot.on_message(filters.command("leave", prefixes="/") & filters.incoming)
async def leave_vc(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("❌ Sahi tarika: `/leave [Chat_ID]`")
        return
    
    target = args[1]
    try:
        chat_id = int(target)
        await call_client.leave_group_call(chat_id)
        await message.reply_text(f"👋 Userbot ne VC ({chat_id}) se leave kar diya hai.")
    except ValueError:
        await message.reply_text("❌ Sirf ID number (-100...) daalo!")
    except Exception as e:
        await message.reply_text(f"❌ Error aaya: {str(e)}")

@bot.on_message(filters.command("volume", prefixes="/") & filters.incoming)
async def change_volume(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(f"ℹ️ Current Volume: {AUDIO_SETTINGS['volume']}/400")
        return
    try:
        vol = int(args[1])
        if 0 <= vol <= 400:
            AUDIO_SETTINGS["volume"] = vol
            await message.reply_text(f"✅ Volume set to {vol}/400")
        else:
            await message.reply_text("❌ Range 0 se 400 rakhein.")
    except ValueError:
        await message.reply_text("❌ Sahi number daalo!")

@bot.on_message(filters.command("gain", prefixes="/") & filters.incoming)
async def change_gain(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(f"ℹ️ Current Gain: {AUDIO_SETTINGS['gain']}/10")
        return
    try:
        gain = int(args[1])
        if 1 <= gain <= 10:
            AUDIO_SETTINGS["gain"] = gain
            await message.reply_text(f"⚡ Gain set to {gain}/10")
        else:
            await message.reply_text("❌ Range 1 se 10 rakhein.")
    except ValueError:
        await message.reply_text("❌ Sahi number daalo!")

@bot.on_message(filters.command("bass", prefixes="/") & filters.incoming)
async def change_bass(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(f"🎸 Current Bass: {AUDIO_SETTINGS['bass']}/100")
        return
    try:
        bass = int(args[1])
        if 0 <= bass <= 100:
            AUDIO_SETTINGS["bass"] = bass
            await message.reply_text(f"🎸 Bass set to {bass}/100")
        else:
            await message.reply_text("❌ Range 0 se 100 rakhein.")
    except ValueError:
        await message.reply_text("❌ Sahi number daalo!")

@bot.on_message(filters.command("treble", prefixes="/") & filters.incoming)
async def change_treble(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text(f"🎼 Current Treble: {AUDIO_SETTINGS['treble']}/100")
        return
    try:
        trb = int(args[1])
        if 0 <= trb <= 100:
            AUDIO_SETTINGS["treble"] = trb
            await message.reply_text(f"🎼 Treble set to {trb}/100")
        else:
            await message.reply_text("❌ Range 0 se 100 rakhein.")
    except ValueError:
        await message.reply_text("❌ Sahi number daalo!")

@bot.on_message(filters.command("mute", prefixes="/") & filters.incoming)
async def mute_audio(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    AUDIO_SETTINGS["muted"] = True
    await message.reply_text("🔇 Audio output has been muted!")

@bot.on_message(filters.command("unmute", prefixes="/") & filters.incoming)
async def unmute_audio(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    AUDIO_SETTINGS["muted"] = False
    await message.reply_text("🔊 Audio output has been unmuted!")

@bot.on_message(filters.command("status", prefixes="/") & filters.incoming)
async def get_status(client, message):
    if message.from_user.id not in SUDO_USERS:
        return
    status_msg = (
        "📊 **Current Live Audio Settings:**\n\n"
        f"🔊 **Volume:** {AUDIO_SETTINGS['volume']}/400\n"
        f"⚡ **Gain Boost:** {AUDIO_SETTINGS['gain']}/10\n"
        f"🎸 **Bass:** {AUDIO_SETTINGS['bass']}/100\n"
        f"🎼 **Treble:** {AUDIO_SETTINGS['treble']}/100\n"
        f"🎙️ **Muted:** {'Yes 🔇' if AUDIO_SETTINGS['muted'] else 'No 🔊'}"
    )
    await message.reply_text(status_msg)

async def main():
    print("🚀 Starting Bot & Userbot...")
    await bot.start()
    await user.start()
    await call_client.start()
    print("✅ Userbot is ONLINE & Ready for VC Commands!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Stopping...")
    
