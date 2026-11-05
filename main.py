import asyncio
import json
import logging
import os
import discord
from quart import Quart, render_template, request, redirect, url_for
from hypercorn.config import Config
from hypercorn.asyncio import serve

# Configure console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Quart(__name__)
CONFIG_PATH = "config.json"
active_clients = {}

def read_config():
    """Safely load JSON configuration file."""
    if not os.path.exists(CONFIG_PATH):
        return {"accounts": []}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def write_config(data):
    """Safely write updated config data back to disk."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class CustomUserBot(discord.Client):
    def __init__(self, account_data: dict, account_index: int):
        self.account_data = account_data
        self.account_index = account_index
        
        # Read proxy and mobile spoof parameters natively supported by dolfies/discord.py-self
        proxy_url = account_data.get("proxy", "").strip() or None
        device_type = account_data.get("device", "desktop").lower()
        
        super().__init__(
            proxy=proxy_url,
            mobile=(device_type == "mobile")
        )

    async def apply_rpc_presence(self):
        """Applies online status and custom rich presence activity."""
        status_mapping = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible,
        }
        target_status = status_mapping.get(
            self.account_data.get("status", "online"), 
            discord.Status.online
        )

        rpc_config = self.account_data.get("rpc", {})
        type_mapping = {
            "playing": discord.ActivityType.playing,
            "streaming": discord.ActivityType.streaming,
            "listening": discord.ActivityType.listening,
            "watching": discord.ActivityType.watching,
        }
        activity_type = type_mapping.get(
            rpc_config.get("type", "playing").lower(), 
            discord.ActivityType.playing
        )

        custom_activity = discord.Activity(
            type=activity_type,
            name=rpc_config.get("name", "Custom App"),
            details=rpc_config.get("details", ""),
            state=rpc_config.get("state", "")
        )

        await self.change_presence(activity=custom_activity, status=target_status)
        logging.info(f"[{self.account_data.get('label')}] Presence profile updated successfully.")

    async def on_ready(self):
        logging.info(f"[{self.account_data.get('label')}] Authenticated successfully as {self.user}!")
        await self.apply_rpc_presence()

async def launch_bot_instance(index: int, account_info: dict):
    """Initializes and runs a self-bot client task asynchronously."""
    token = account_info.get("token")
    if not token or "YOUR_USER_TOKEN" in token:
        return

    # Close existing instance if running to prevent duplication
    if index in active_clients:
        try:
            await active_clients[index].close()
        except Exception:
            pass

    bot_client = CustomUserBot(account_info, index)
    active_clients[index] = bot_client
    
    asyncio.create_task(bot_client.start(token))

@app.route("/")
async def dashboard_home():
    config_data = read_config()
    return await render_template("index.html", accounts=config_data.get("accounts", []))

@app.route("/update", methods=["POST"])
async def dashboard_update():
    form_data = await request.form
    account_idx = int(form_data.get("index"))
    config_data = read_config()

    if account_idx < len(config_data["accounts"]):
        acc = config_data["accounts"][account_idx]
        acc["token"] = form_data.get("token")
        acc["proxy"] = form_data.get("proxy")
        acc["status"] = form_data.get("status")
        acc["device"] = form_data.get("device")
        acc["rpc"]["type"] = form_data.get("rpc_type")
        acc["rpc"]["name"] = form_data.get("rpc_name")
        acc["rpc"]["details"] = form_data.get("rpc_details")
        acc["rpc"]["state"] = form_data.get("rpc_state")

        write_config(config_data)
        
        # Hot-reload connection with updated configurations
        await launch_bot_instance(account_idx, acc)

    return redirect(url_for("dashboard_home"))

async def main():
    config_data = read_config()
    
    # Start all accounts concurrently
    for idx, account in enumerate(config_data.get("accounts", [])):
        await launch_bot_instance(idx, account)

    # Bind web app server for hosting panels (Port 8080 default)
    server_port = int(os.environ.get("PORT", 8080))
    hypercorn_options = Config()
    hypercorn_options.bind = [f"0.0.0.0:{server_port}"]
    
    logging.info(f"Starting management web server on port {server_port}...")
    await serve(app, hypercorn_options)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down controller gracefully.")
