import os
import sys
import subprocess
import platform

# --- VENV AUTO-SETUP SECTION ---
def in_venv():
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

def ensure_venv():
    if in_venv():
        return  # Already in venv

    # Create venv if it doesn't exist
    if not os.path.exists('venv'):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)

    # Find venv python
    if platform.system() == 'Windows':
        python_path = os.path.join('venv', 'Scripts', 'python.exe')
    else:
        python_path = os.path.join('venv', 'bin', 'python')

    # Install requirements if needed
    try:
        import discord  # noqa: F401
    except ImportError:
        print("Installing requirements...")
        # Suppress pip output
        subprocess.run(
            [python_path, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # Relaunch script in venv
    print("Restarting in virtual environment...")
    os.execv(python_path, [python_path, __file__])

ensure_venv()
# --- END VENV AUTO-SETUP SECTION ---

# --- Suppress discord.py info logs ---
import logging
logging.getLogger("discord").setLevel(logging.WARNING)
# -------------------------------------

import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import json
from datetime import datetime
import traceback

def check_environment():
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in .env file!")
        print("Please create a .env file with your Discord bot token.")
        print("You can use .env.example as a template.")
        input("Press Enter to exit...")
        sys.exit(1)
    return token

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Constants
ROBUX_TO_USD_RATE = 0.0035  # Approximate rate: 1 Robux = $0.0035

# Roblox API endpoints
USER_LOOKUP_URL = "https://users.roblox.com/v1/usernames/users"
INVENTORY_URL = "https://inventory.roblox.com/v1/users/{user_id}/assets/collectibles?sortOrder=Asc&limit=100"
CURRENTLY_WEARING_URL = "https://avatar.roblox.com/v1/users/{user_id}/currently-wearing"
ASSET_DETAILS_URL = "https://economy.roblox.com/v2/assets/{asset_id}/details"
CATALOG_DETAILS_URL = "https://catalog.roblox.com/v1/assets/details?assetIds={asset_id}"
ROLIMONS_ITEM_API = "https://www.rolimons.com/itemapi/itemdetails"

async def get_account_value(username):
    try:
        # Step 1: Get userId from username
        resp = requests.post(USER_LOOKUP_URL, json={"usernames": [username], "excludeBannedUsers": False})
        if resp.status_code != 200:
            return None, "Failed to contact Roblox API."
        data = resp.json()
        if not data.get("data") or len(data["data"]) == 0:
            return None, "Roblox user not found."
        user_id = data["data"][0]["id"]
        # Step 2: Get collectibles (limited items)
        inv_resp = requests.get(INVENTORY_URL.format(user_id=user_id))
        if inv_resp.status_code != 200:
            return None, "Failed to fetch inventory."
        inv_data = inv_resp.json()
        collectibles = inv_data.get("data", [])
        total_robux = 0
        for item in collectibles:
            rap = item.get("recentAveragePrice")
            if rap:
                total_robux += rap
        total_usd = total_robux * ROBUX_TO_USD_RATE
        return {
            "username": username,
            "robux_value": total_robux,
            "usd_value": total_usd,
            "limited_items_count": len(collectibles)
        }, None
    except Exception as e:
        print(f"Error fetching value for {username}: {e}")
        traceback.print_exc()
        return None, str(e)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("Bot is ready to use! You can now use the !value command in your Discord server.")
    print("Press Ctrl+C to stop the bot.")

@bot.command(name='value')
async def value(ctx, username: str):
    """Get the value of a Roblox account"""
    message = await ctx.send(f"🔍 Calculating value for {username}...")
    result, error = await get_account_value(username)
    if error or result is None:
        await message.edit(content=f"❌ Error: {error or 'Unknown error.'}")
        return
    embed = discord.Embed(
        title=f"💰 Account Value for {result['username']}",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Robux Value",
        value=f"{result['robux_value']:,.0f} R$",
        inline=True
    )
    embed.add_field(
        name="USD Value",
        value=f"${result['usd_value']:,.2f}",
        inline=True
    )
    embed.add_field(
        name="Limited Items",
        value=str(result['limited_items_count']),
        inline=True
    )
    embed.set_footer(text="Note: Values are approximate and based on recent sales")
    await message.edit(content=None, embed=embed)

if __name__ == "__main__":
    token = check_environment()
    try:
        bot.run(token)
    except KeyboardInterrupt:
        print("\nBot has been stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...") 