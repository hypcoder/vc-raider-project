import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, HighQualityAudio

BOOSTED_FILTER = "-af volume=10.0,dynaudnorm=f=150:g=15"

@Client.on_message(filters.command("raid", prefixes=["/", "!", "."]) & filters.me)
async def start_raid(client, message):
    args = message.command
    if len(args) < 3:
        await message.edit("❌ Format: `/raid [Chat_ID] [Audio_Path]`")
        return

    target_chat = args[1]
    audio_file = args[2]

    try:
        await client.vc_client.join_group_call(
            target_chat,
            AudioPiped(
                audio_file,
                HighQualityAudio(),
                options=BOOSTED_FILTER
            )
        )
        await message.edit("🔥 VC Raid shuru ho chuki hai! Volume: 200% + Boosted Gain.")
    except Exception as e:
        await message.edit(f"❌ Error aaya: {str(e)}")

@Client.on_message(filters.command("stop", prefixes=["/", "!", "."]) & filters.me)
async def stop_raid(client, message):
    try:
        await client.vc_client.leave_group_call(message.chat.id)
        await message.edit("🛑 Raid rok di gayi hai.")
    except Exception as e:
        await message.edit(f"❌ Rokne me dikkat aayi: {str(e)}")
  
