from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, STRING_SESSION

app = Client(
    "raider_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
    plugins=dict(root="modules")
)

vc_client = PyTgCalls(app)
app.vc_client = vc_client

if __name__ == "__main__":
    app.run()
