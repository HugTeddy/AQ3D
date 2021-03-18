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
from discord.ext import commands
from disputils import BotEmbedPaginator

wb = openpyxl.load_workbook('./data/AQ3DItemDatabase.xlsx')
ws = wb['Fish']

wiki_files = [os.path.basename(x) for x in glob.glob('./data/*.txt')]
cat_names = [x[:-4] for x in wiki_files]
help_msg = """`!char <name>` - Looks up character profile
`!link` - Links discord account to character profile
`!unlink` - Unlinked discord account from character profile


`!lookup <category> <search>` - Looks up various items from different categories
`!status` - Shows current playercount server status
`!news` - Shows latest events
`!time` - Shows current server time and refresh timer
More to come...

:coffee: [Like what you see? Buy me a Coffee](https://gluebear.xyz/HugTed)
"""
def getItem(row:int):
    global ws
    data=[]
    for item in ws[row+2]:
        data.append(item.value)
    return data

async def paginate(ctx, embeds):
    paginator = BotEmbedPaginator(ctx, embeds)
    await paginator.run()

def midnight_time(tz):
    now = datetime.now(tz)
    tomorrow = datetime.combine(datetime.now(tz).date(), time(0, 0)) + timedelta(1)
    delta = tomorrow.replace(tzinfo=tz)-now
    out = ':'.join(str(delta).split(':')).split('.')[0]
    return out

def account(link, id, name="None"):
    with open (f'./linked_users.txt', 'r') as f:
        data = json.load(f)
    if link == "in":
        if str(id) in data.keys() or name in data.values():
            return False
        else:
            data[str(id)] = name
    elif link == "out":
        if str(id) not in data.keys():
            return False
        else:
            del data[str(id)]
    elif link == "lookup":
        if str(id) in data.keys():
            return data[str(id)]
        else:
            return "Null"
    with open (f'./linked_users.txt', 'w') as f:
        json.dump(data, f)
    return True


def chunks(data, SIZE=10):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}

def createFishEmbed(data):
    embed = discord.Embed(title=f"{data[0].capitalize()}", color=0x00ff99)
    embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
    embed.add_field(name="Rarity:", value=f'{data[1]}', inline=False)
    embed.add_field(name="Node Power:", value=f'{data[2]}', inline=False)
    embed.add_field(name="Location:", value=f'{data[3]}', inline=False)
    if data[4]:
        embed.add_field(name="Exp Value:", value=f'{data[4]}', inline=False)
    else:
        embed.add_field(name="Exp Value:", value=f'Unknown', inline=False)
    return embed

def createLookupEmbed(cat, data):
    embeds = []
    data = chunks(data)
    for items in data:
        output = ""
        embed = discord.Embed(title=f"Lookup - {cat.capitalize()}", color=0x00ff11)
        embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
        for i in items:
            output += f'[{i}](http://aq-3d.wikidot.com{items[i]})\n'
        embed.add_field(name="Items:", value=output, inline=False)
        embeds.append(embed)
    return embeds

class AQ3DCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def link(self, ctx, *, name):
        if account("in", ctx.author.id, name):
            await ctx.send(f'{ctx.author.mention} has been linked to `{name}`')
        else:
            await ctx.send("Account previously linked or username already taken")

    @commands.command()
    async def unlink(self, ctx):
        if account("out", ctx.author.id):
            await ctx.send(f'{ctx.author.mention} has been unlinked')
        else:
            await ctx.send("Account was not previously linked")

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Commands & Useage", color=0x9988FF)
        embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
        embed.add_field(name="Commands: ", value=help_msg, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def time(self, ctx):
        tz = timezone('EST')
        embed = discord.Embed(title="Server Time", description=f'Server Time: `{datetime.now(tz).ctime()}`\nTime to Reset: `{midnight_time(tz)}`', color=0x9900FF)
        embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def lookup(self, ctx, category="None", search="None"):
        if category == "None":
            options = "`"
            embed = discord.Embed(title="Lookup Categories", description='`!lookup <category> <search>`', color=0x00ff00)
            embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
            options += "`, `".join(cat_names) + "`"
            embed.add_field(name="Item Categories:", value=options, inline=False)
            await ctx.send(embed=embed)
            return
        else:
            cat = category.lower()
            if cat in cat_names:
                with open(f'./data/{cat}.txt', 'r') as f:
                    data = json.load(f)
                if search != "None":
                    results={}
                    for item in data.keys():
                        if item.lower().startswith(search.lower()):
                             results[item] = data[item]
                    if len(results) == 0:
                        await ctx.send("Unable to find item.")
                        return
                    else:
                        embeds = createLookupEmbed(cat, results)
                else:
                    embeds = createLookupEmbed(cat, data)
                await paginate(ctx, embeds)
                return
            else:
                await ctx.send("Unknown Category.")
                return

    @commands.command()
    async def fish(self, ctx, option="None", *, fish="None"):
        option_list = ["rods", "levels", "fish"]
        if option == "None":
            options = "`rods`, `levels`, `fish`"
            embed = discord.Embed(title="Lookup Categories", description='`!fish <category>` or `!fish fish <Fish Name>`', color=0x00ff00)
            embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
            embed.add_field(name="Fish Categories:", value=options, inline=False)
            await ctx.send(embed=embed)
            return
        elif option in option_list:
            if option == "rods":
                with open(f'./data/fish/rods.txt', "r") as f:
                    output = f.read()
                embed = discord.Embed(title="Fishing Rods", description=f'```{output}```', color=0x00ff00)
                embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
                await ctx.send(embed=embed)
                return
            elif option == "levels":
                with open(f'../data/fish/10_exp.txt', "r") as f:
                    output1 = f.read()
                with open(f'../data/fish/20_exp.txt', "r") as f:
                    output2 = f.read()
                with open(f'../data/fish/30_exp.txt', "r") as f:
                    output3 = f.read()
                with open(f'../data/fish/40_exp.txt', "r") as f:
                    output4 = f.read()
                with open(f'../data/fish/50_exp.txt', "r") as f:
                    output5 = f.read()
                embed = discord.Embed(title="Fishing Exp", color=0x00ff00)
                embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
                embed.add_field(name="__**Levels 1-10:**__", value=f'```{output1}```', inline=False)
                embed.add_field(name="__**Levels 11-20:**__", value=f'```{output2}```', inline=False)
                embed.add_field(name="__**Levels 21-30:**__", value=f'```{output3}```', inline=False)
                embed.add_field(name="__**Levels 31-40:**__", value=f'```{output4}```', inline=False)
                embed.add_field(name="__**Levels 41-50:**__", value=f'```{output5}```', inline=False)
                await ctx.send(embed=embed)
                return
            else:
                format_fish = []
                with open(f'./data/fish/fish.txt', "r") as f:
                    fish_list = f.readlines()
                if fish == "None":
                    output = ""
                    for fish in fish_list:
                        format_fish.append(fish.capitalize())
                    for i in format_fish:
                        output += f'`{i[:-1]}`\n'
                    embed = discord.Embed(title="Fishes", description=output, color=0x00ff00)
                    embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
                    await ctx.send(embed=embed)
                    return
                else:
                    for fishes in fish_list:
                        format_fish.append(fishes.lower()[:-1])
                    fish = fish.lower()
                    if fish in format_fish:
                        row = format_fish.index(fish)
                        data = getItem(row)
                        embed = createFishEmbed(data)
                        await ctx.send(embed=embed)
                        return
                    else:
                        await ctx.send("Unable to find fish.")
        else:
            await ctx.send("Unknown Category, See `!fish` for Categories.")

    @commands.command()
    async def status(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://game.aq3d.com/api/game/ServerList") as response:
                parsed = json.loads(await response.text())
                embed = discord.Embed(title="AQ3D Server Status", description="Artix Entertainment :copyright:", color=0x00ff00)
                total = 0
                for item in parsed:
                    if item["Name"] != "Localhost":
                        embed.add_field(name=item["Name"], value=f'Users: {item["Connections"]}/{item["MaxUsers"]}', inline=False)
                        total += item["Connections"]
                embed.add_field(name="Total Online :earth_americas:", value=total, inline=False)
                embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
                await ctx.send(embed=embed)

    @commands.command()
    async def news(self, ctx):
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

                output = ""
                for item in formatted_articles.keys():
                    output += f'[{item}](https://aq3d.com{formatted_articles[item]})\n'
                    if len(output) > 700:
                        output += "...\n"
                        break
                embed = discord.Embed(title=f"AQ3D News", url=url, color=0x463dfc)
                embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
                embed.add_field(name="Recent News:", value=output)
                embed.set_footer(text=f'Command Called by {ctx.author.name}')
                await ctx.send(embed=embed)

    @commands.command()
    async def char(self, ctx, *, char="None"):
        if char == "None":
            char = account("lookup", ctx.author.id)
            if char == "Null":
                await ctx.send("Account not Linked")
                return
        string = char
        new_string = string.replace(" ", "%20")
        url = "https://game.aq3d.com/account/Character?id=" + new_string

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                if 'placeholder="Character Name"' in html:
                    return await ctx.send(":x: That character could not be found.")

                soup = BeautifulSoup(html, "html.parser")

                main = soup.find("div", attrs={"class":["text-center", "nopadding"]})
                char = main.find("h1").text
                level = main.find("p").text.split()[1]
                class_img_attr = [img for img in soup.find_all("img", attrs={"class": ["img-responsive", "center-block"]}) if "/classesbg" in img["src"]][0]
                class_name = class_img_attr["alt"]

                badge_category = soup.find_all("div", attrs={"role": "tabpanel"})
                badges = {}
                for category in badge_category:
                    badges_in_cat = category.find_all("h3", attrs={"class": "h4"})
                    badges[category["id"]] = badges_in_cat

                embed = discord.Embed(title=f"{char}" + "'s Profile", url=url, color=0x463dfc)
                embed.set_thumbnail(url="https://aq3d.com/media/1507/aq3d-full-logo760.png")
                embed.set_image(url=f"{class_img_attr['src']}")
                embed.add_field(name="Level", value=f"{level}")
                embed.add_field(name="Class", value=f"{class_name}")
                if len(badges) > 0:
                    for category in badges.keys():
                        output = ''
                        for badge in badges[category]:
                            raw = str(badge)
                            if len(output) > 500:
                                output += '...\n'
                                break
                            else:
                                output += f'{raw[15:-5]}\n'
                        output += "\n"
                        embed.add_field(name=f"**__{category}__** - {len(badges[category])}", value=output, inline=False)
                else:
                    embed.add_field(name="Badges", value=formatted_badges if len(badges) > 0 else "--No badges--")
                embed.set_footer(text=f'Command Called by {ctx.author.name}')
                await ctx.send(embed=embed)

def setup(client):
    client.remove_command("help")
    client.add_cog(AQ3DCog(client))
