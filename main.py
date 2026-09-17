# KaroDevGroup
# Josh Karo 

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from supabase_client import supabase


load_dotenv("/home/container/.env")

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 908868924488171540

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable is not set.")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

async def load_commands():
    await bot.load_extension("commands.version")
    await bot.load_extension("commands.joincall")
    await bot.load_extension("commands.download")
    await bot.load_extension("commands.ban")
    await bot.load_extension("commands.unban")
    await bot.load_extension("commands.kick")
    await bot.load_extension("commands.timeout")
    await bot.load_extension("commands.warn")
    await bot.load_extension("commands.warnings")
    await bot.load_extension("commands.warn_remove")
    await bot.load_extension("commands.lock")
    await bot.load_extension("commands.unlock")
    await bot.load_extension("commands.clear")
    await bot.load_extension("commands.slowmode")
    await bot.load_extension("commands.moderation_bridge")
    await bot.load_extension("commands.embed")
    await bot.load_extension("commands.tickets")
    await bot.load_extension("commands.logging")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    print("DaBoyzBot is online!")

    guild = discord.Object(id=GUILD_ID)

    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Failed to synchronize slash commands: {e}")

async def main():
    async with bot:
        await load_commands()
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())