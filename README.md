# AQ3D Discord Bot
AQ3D Discord Bot is a Python based Discord Bot to augment player experience with AQ3D

## Installation
#### Create a server
If you don't already have a server, create one free one at https://discordapp.com. Simply log in, and then click the plus sign on the left side of the main window to create a new server.

#### Create an app
Go to https://discordapp.com/developers/applications/me and create a new app. On your app detail page, save the Client ID. You will need it later to authorize your bot for your server.

#### Create a bot account for your app
After creating app, on the app details page, scroll down to the section named bot, and create a bot user. **Save the token**, you will need it later to run the bot.

#### Authorize the bot for your server
Visit the URL https://discordapp.com/oauth2/authorize?client_id=XXXXXXXXXXXX&scope=bot but replace XXXX with your app client ID. Choose the server you want to add it to and select authorize.

#### Install the python package discord.py
Run pip install from your system terminal/shell/command prompt.

```bash
python -m pip install discord.py
python -m pip install openpyxl
python -m pip install pytz
python -m pip install disputils
python -m pip install bs4
python -m pip install re
```

#### Download and extract source files
Download the compressed ZIP release from the sidebar. Copy main directory onto server.

Instructions Sourced from: [Dungeon Dev](https://www.devdungeon.com/content/make-discord-bot-python)

## Usage
To start your instance of the bot some changes are needed to the main python file.

Open `config.ini` with a text editor such as notepad, notepad++, etc.

On download, the file should look like:
```ini
[DEFAULT]
token = <DISCORD BOT TOKEN>
owner_id = <DISCORD OWNER ID>
```

You will need to change these values to:
1. Your personal **token** found when you created the bot account on discord (see Installation)
2. Your personal **client_id** which can be found by right clicking your username in any discord chat and selecting 'copy id' at the bottom (Discord Developer Mode must be enabled)

The resulting file should look something like this:
```ini
[DEFAULT]
token = aJsdGwf093.fsdvpMrighscsdf392ldFknD
owner_id = 1234567890
```

Once you have verified that the submitted information is correct, save and exit.
Run the bot by doing `python ./main.py`

## Commands
Command | Function
------------ | -------------
`!char <name>` | Looks up character profile
`!link` | Links discord account to character profile
`!unlink` | Unlinked discord account from character profile
`!lookup <category> <search>` | Looks up various items from different categories
`!fish <category> <fishname>` | Shows fishing information
`!status` | Shows current playercount server status
`!news` | Shows latest events
`!time` | Shows current server time and refresh timer

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
