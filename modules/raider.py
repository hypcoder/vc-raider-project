import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, HighQualityAudio

BOOSTED_FILTER = "-af volume=15.0,dynaudnorm=f=150:g=20"

@Client.on_message(filters.command("liveraid", prefixes=["/", "!", "."]) & filters.me)
async def start_live_raid(client, message):
    args = message.command
    if len(args) < 3:
        await message.edit("❌ Format: `/liveraid [Source_Chat_ID] [Target_Chat_ID]`")
        return

    source_chat = args[1]
    target_chat = args[2]

    try:
        # Pehle source VC (jahan aap bologe) se connect hona
        # Fir wahan ka live stream target VC me forward karna
        await client.vc_client.join_group_call(
            target_chat,
            AudioPiped(
                f"tgcalls://{source_chat}",
                HighQualityAudio(),
                options=BOOSTED_FILTER
            )
        )
        await message.edit("🔥 Live VC Relay Shuru! Aap source me boliye, target me gaaon gunjega.")
    except Exception as e:
        await message.edit(f"❌ Error aaya: {str(e)}")

@Client.on_message(filters.command("stopraid", prefixes=["/", "!", "."]) & filters.me)
async def stop_live_raid(client, message):
    try:
        await client.vc_client.leave_group_call(message.chat.id)
        await message.edit("🛑 Live Raid rok di gayi hai.")
    except Exception as e:
        await message.edit(f"❌ Rokne me dikkat aayi: {str(e)}")
        
