import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, HighQualityAudio
from config import SOURCE_CHAT

BOOSTED_FILTER = "-af volume=15.0,dynaudnorm=f=150:g=20"

@Client.on_message(filters.command("raid", prefixes=["/", "!", "."]) & filters.me)
async def start_shortcut_raid(client, message):
    args = message.command
    if len(args) < 2:
        await message.edit("❌ Format: `/raid [Target_Chat_ID_Ya_Username]`")
        return

    target_chat = args[1]

    try:
        await client.vc_client.join_group_call(
            target_chat,
            AudioPiped(
                f"tgcalls://{SOURCE_CHAT}",
                HighQualityAudio(),
                options=BOOSTED_FILTER
            )
        )
        await message.edit(f"🔥 Raid Shuru! Target: {target_chat}\nAudio Source: {SOURCE_CHAT}")
    except Exception as e:
        await message.edit(f"❌ Error aaya: {str(e)}")

@Client.on_message(filters.command("stop", prefixes=["/", "!", "."]) & filters.me)
async def stop_shortcut_raid(client, message):
    try:
        await client.vc_client.leave_group_call(message.chat.id)
        await message.edit("🛑 Raid rok di gayi hai.")
    except Exception as e:
        await message.edit(f"❌ Rokne me dikkat aayi: {str(e)}")
    
