# KaroDevGroup

import discord


RED = discord.Color.from_rgb(220, 20, 20)
GREEN = discord.Color.from_rgb(40, 200, 80)
ORANGE = discord.Color.from_rgb(255, 165, 0)
BLUE = discord.Color.from_rgb(60, 140, 255)
DARK = discord.Color.from_rgb(30, 30, 30)

def success_embed(title: str, description: str):
    return discord.Embed(
        title=title,
        description=description,
        color=GREEN
    )

def error_embed(title: str, description: str):
    return discord.Embed(
        title=title,
        description=description,
        color=RED
    )

def warning_embed(title: str, description: str):
    return discord.Embed(
        title=title,
        description=description,
        color=ORANGE
    )

def info_embed(title: str, description: str):
    return discord.Embed(
        title=title,
        description=description,
        color=BLUE
    )