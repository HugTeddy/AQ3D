import discord
import configparser
import json
from datetime import datetime
from discord.ext import commands
import traceback
import datetime

client = commands.Bot(command_prefix='!', case_insensitive=True)

config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('DEFAULT', 'Token')
bot_owner = int(config.get('DEFAULT', 'owner_id'))

@client.command()
async def reload(ctx, extension):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Nice Try')
        return
    client.unload_extension(f'extensions.{extension}')
    client.load_extension(f'extensions.{extension}')
    await ctx.message.add_reaction("✅")

@client.command()
async def load(ctx, extension):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Nice Try')
        return
    client.load_extension(f'extensions.{extension}')
    await ctx.message.add_reaction("✅")

@client.command()
async def unload(ctx, extension):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Nice Try')
        return
    client.unload_extension(f'extensions.{extension}')
    await ctx.message.add_reaction("✅")

@client.event
async def on_ready():
    await client.change_presence(
        activity=discord.Activity(
            name='with AQ3D', type=discord.ActivityType.playing))
    client.load_extension('extensions.AQCommands')
    client.load_extension('extensions.ItemCog')
    print('Bot is ready.')

@client.event
async def on_error(event, *args, **kwargs):
    embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c) #Red
    embed.add_field(name='Event', value=event)
    embed.description = '```py\n%s\n```' % traceback.format_exc()
    embed.timestamp = datetime.datetime.utcnow()
    AppInfo = await client.application_info()
    await AppInfo.owner.send(embed=embed)

@client.command()
async def botstop(ctx):
    if ctx.message.author.id != bot_owner:
        await ctx.send('Nice Try')
        return
    await ctx.send('Bye Bye')
    await client.logout()

client.run(token)
