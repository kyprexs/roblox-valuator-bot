# Roblox Valuator Bot

A Discord bot that calculates the value of a Roblox account using the `!value <username>` command.

---

## Features

- Calculates the Robux and USD value of a Roblox account
- Shows the number of limited items
- Easy to set up and run

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/roblox-valuator-bot.git
cd roblox-valuator-bot
```

### 2. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name
3. Go to the **"Bot"** tab and click **"Add Bot"**
4. Click **"Reset Token"** and copy your bot token

### 3. Invite the Bot to Your Server

1. Go to the **"OAuth2" > "URL Generator"** tab
2. Under **Scopes**, select `bot`
3. Under **Bot Permissions**, select `Send Messages` and any other permissions you want
4. Copy the generated URL, open it in your browser, and invite the bot to your server

### 4. Configure the Bot

1. Copy `.env.example` to `.env`
2. Paste your Discord bot token in the `.env` file:

   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

### 5. Run the Bot

Just double-click `bot.py` or run:

```bash
python bot.py
```

The bot will automatically set up everything it needs.

---

## Usage

In your Discord server, type:

## Commands
- `!value <username>` - Get the value of a Roblox account

## Note
This bot uses the Roblox API to fetch account information and calculates estimated values based on various factors including:
- Limited items
- Robux balance
- Account age
- Premium status

## License
MIT License 