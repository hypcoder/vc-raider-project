import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, HighQualityAudio
from config import SOURCE_CHAT, OWNER_ID

BOOSTED_FILTER = "-af volume=15.0,dynaudnorm=f=150:g=20"
SUDO_USERS = set()

@Client.on_message(filters.command("sudo", prefixes=["/", "!", "."]))
async def add_sudo(client, message):
    if message.from_user.id != OWNER_ID:
        return
    
    if not message.reply_to_message:
        await message.reply_text("Kisi bande ke message par reply karke .sudo likho bbu")
        return
        
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.first_name
    
    SUDO_USERS.add(user_id)
    await message.reply_text(f"Done! {user_name} ko sudo list me add kar diya hai.")

@Client.on_message(filters.command("join", prefixes=["/", "!", "."]))
async def bot_join_vc(client, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID and user_id not in SUDO_USERS:
        return

    args = message.command
    if len(args) < 2:
        await message.reply_text("Format: /join Target_Chat_ID")
        return

    target_chat = args[1]
    if target_chat.startswith("-") or target_chat.isdigit():
        target_chat = int(target_chat)

    status_msg = await message.reply_text("Connecting your String Session...")

    try:
        await client.userbot.vc_client.join_group_call(
            target_chat,
            AudioPiped(
                f"tgcalls://{SOURCE_CHAT}",
                HighQualityAudio(),
                options=BOOSTED_FILTER
            )
        )
        await status_msg.edit(f"Joined VC {target_chat}")
    except Exception as e:
        await status_msg.edit(f"Error Aaya: {str(e)}")

@Client.on_message(filters.command("leave", prefixes=["/", "!", "."]))
async def bot_leave_vc(client, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID and user_id not in SUDO_USERS:
        return
        
    try:
        await client.userbot.vc_client.leave_group_call(message.chat.id)
        await message.reply_text("Left VC")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
    
