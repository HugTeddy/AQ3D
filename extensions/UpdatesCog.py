import discord
import configparser
import aiohttp
import json
import math
import glob
import os
import openpyxl
from datetime import datetime, date, time, timedelta
from pytz import timezone
from itertools import islice
from bs4 import BeautifulSoup
from discord.ext import tasks, commands
from disputils import BotEmbedPaginator


config = configparser.ConfigParser()
config.read('config.ini')
bot_owner = int(config.get('DEFAULT', 'owner_id'))

with open(f'./data/channels/status_channels.txt', 'r') as f:
    status_channels = json.load(f)
with open(f'./data/channels/news_channels.txt', 'r') as f:
    news_channels = json.load(f)
messages = []

async def createServerEmbed():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://game.aq3d.com/api/game/ServerList") as response:
            parsed = json.loads(await response.text())
            embed = discord.Embed(title="AQ3D Server Status", description="Artix Entertainment :copyright:", color=0x00ff00)
            total = 0
            tz = timezone('EST')
            for item in parsed:
                if item["Name"] != "Localhost":
                    embed.add_field(name=item["Name"], value=f'Users: {item["Connections"]}/{item["MaxUsers"]}', inline=False)
                    total += item["Connections"]
            embed.add_field(name="Total Online :earth_americas:", value=total, inline=False)
            embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
            embed.set_footer(text=f'Updated {datetime.now(tz).ctime()} EST')

            return embed

async def updateNews():
    url = "https://aq3d.com/news"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            article = soup.find_all("div", attrs={"class": "caption"})
            formatted_articles = {}

            for title in article:
                formal_title = str(title.find_all("h2", attrs={"class": "text-uppercase"})[0])[27:-5]
                news_url = str(title.find_all("a")[1]["href"])
                formatted_articles[formal_title] = news_url

            with open(f'./data/channels/news.txt', 'r') as f:
                last_update = f.read()

            output = ""
            for item in formatted_articles.keys():
                if item != last_update:
                    output += f'{item}\nhttps://aq3d.com{formatted_articles[item]}\n'
                else:
                    break

            with open(f'./data/channels/news.txt', 'w') as f:
                f.write(f'{list(formatted_articles.keys())[0]}')

            return output

class UpdatesCog(commands.Cog):
    def __init__(self, client):
        self.index = 0
        self.client = client
        self.printEmbeds.start()

    @tasks.loop(minutes=5.0)
    async def printEmbeds(self):
        global status_channels
        global news_channels
        global messages

        output = await updateNews()
        embed = await createServerEmbed()

        if self.index == 0:
            for i in status_channels:
                try:
                    channel = self.client.get_channel(int(i))
                    messages.append(await channel.send(embed=embed))
                except:
                    pass
        else:
            for id in messages:
                try:
                    await id.edit(embed=embed)
                except:
                    pass

        if output != "":
            for i in news_channels:
                try:
                    channel = self.client.get_channel(int(i))
                    await channel.send(output)
                except:
                    pass
        self.index += 1

    @commands.command()
    async def toggleNews(self, ctx):
        global news_channels
        global messages
        if ctx.channel.id not in news_channels:
            news_channels.append(ctx.channel.id)
            await ctx.send(f'Adding {ctx.channel.mention} to news list!', delete_after=5)
            self.printEmbeds.cancel()
            for i in messages:
                try:
                    await i.delete()
                except:
                    continue
            messages = []
            await ctx.message.delete()
            self.index = 0
            await self.printEmbeds.start()
        else:
            news_channels.remove(ctx.channel.id)
            await ctx.send(f'removing {ctx.channel.mention} from news list!', delete_after=5)
            await ctx.message.delete()
        with open(f'./data/channels/news_channels.txt', 'w') as f:
            json.dump(news_channels, f)


    @commands.command()
    async def toggleStatus(self, ctx):
        global status_channels
        global messages
        if ctx.channel.id not in status_channels:
            status_channels.append(ctx.channel.id)
            await ctx.send(f'Adding {ctx.channel.mention} to status list!', delete_after=5)
            self.printEmbeds.cancel()
            for i in messages:
                try:
                    await i.delete()
                except:
                    continue
            messages = []
            await ctx.message.delete()
            self.index = 0
            await self.printEmbeds.start()
        else:
            status_channels.remove(ctx.channel.id)
            await ctx.send(f'removing {ctx.channel.mention} from status list!', delete_after=5)
            await ctx.message.delete()
        with open(f'./data/channels/status_channels.txt', 'w') as f:
            json.dump(status_channels, f)

    @commands.command()
    async def stopUpdate(self, ctx):
        global messages
        global status_channels
        global news_channels
        if ctx.author.id != bot_owner:
            await ctx.message.add_reaction("❌")
        self.printEmbeds.cancel()
        for i in messages:
            try:
                await i.delete()
            except:
                continue
        messages = []
        await ctx.message.delete()
        self.index = 0

def setup(client):
    client.add_cog(UpdatesCog(client))
