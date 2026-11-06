import discord
from discord.ext import commands
from aiohttp import web
import asyncio
import os

# 1. Set up the bot's intents
# You MUST enable BOTH "Message Content Intent" and "Presence Intent" in the Developer Portal
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True # This lets the bot see who is online/offline

# 2. Create the bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store the online statuses of your staff
staff_statuses = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("Bot is ready and listening for server status questions...")
    
    # Populate initial statuses when bot starts
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                staff_statuses[str(member.id)] = str(member.status)
    print("Tracking staff statuses for the website!")

# This event fires instantly when someone goes online/offline
@bot.event
async def on_presence_update(before, after):
    if not after.bot:
        # Saves as 'online', 'idle', 'dnd', or 'offline'
        staff_statuses[str(after.id)] = str(after.status)

# 3. Listen for messages
@bot.listen('on_message')
async def check_server_status(message):
    # Ignore messages sent by the bot itself to prevent infinite loops
    if message.author == bot.user:
        return

    # Convert the message to lowercase so it catches variations like "Are Servers Up"
    content = message.content.lower()

    # The phrases to look out for
    triggers = [
        "are servers down", 
        "are servers up", 
        "servers down?", 
        "servers up?",
        "is the server down",
        "is the server up"
    ]

    # Check if any of the trigger phrases are in the message
    if any(trigger in content for trigger in triggers):
        # Create a cool embed for the reply
        embed = discord.Embed(
            title="are the servers up?",
            description="look in website to see if the servers are up or down",
            color=0xc084fc # Your site's purple accent color
        )
        embed.set_footer(text="made by unity")
        embed.add_field(name="Website", value="[Click here to check the servers](https://milk-tagg.vercel.app/)")
        
        # Reply to the user
        await message.reply(embed=embed)

# ==========================================
# 4. WEB SERVER FOR THE WEBSITE STAFF DOTS
# ==========================================
async def handle_status(request):
    # Returns the dictionary of statuses as JSON and allows your website to read it
    response = web.json_response(staff_statuses)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

async def start_web_server():
    app = web.Application()
    app.router.add_get('/status', handle_status)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Uses port 8080 by default, or the port your host (Railway/Render) assigns
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server running on port {port} - ready for the website!")

async def main():
    # Start the web server first, then run the bot
    await start_web_server()
    
    # 👇 PASTE YOUR BOT TOKEN HERE 👇
    await bot.start('MTU2ODQwNTgyMzEyOTEyNTAzNQ.G0KT3I.naPO3R0aGXlxkvHVltmFgveXbf5PnDTsL8LGs0')

if __name__ == '__main__':
    asyncio.run(main())
