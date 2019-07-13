![Libereus Banner](https://sc.s-ul.eu/nWBPZuZ6)
# Libereus
[![discord](https://lihi1.cc/7CBE7)](https://lihi1.cc/j2C5r)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-367/)

Libereus is a self-hosted only Discord moderation bot written in Python 3.6 that aims to make server moderators' lives easier. Initially created as a submission to participate in [Discord Hack Week 2019](https://blog.discordapp.com/discord-community-hack-week-build-and-create-alongside-us-6b2a7b7bba33) and received [second place](https://blog.discordapp.com/discord-community-hack-week-category-winners-bd0364360f92). Our original submission can be found [here](https://github.com/Tansc161/Libereus-DHW19).

It has the ability to:
> ✅ Prune inactive members via their last message's date  
> ✅ Disable or re-enable messaging permissions on a given channel for normal members (channel lockdown)  
> ✅ Detects bad word and give strike to the sender  
> ✅ Remove a prefix from members' nicknames (i.e. usage of `!` to hoist to the top of the member list)  
> ✅ 💣 GENERATE A COOL SPOILER-MINESWEEPER GAME 💣  
> ...and much more!

## Requirements
> 🐍 Python 3.4 or above (Python 3.6 recommended)

## Installation
### Registering an access token for your bot
1. Navigate to [Discord Developer Portal (Applications)](https://discordapp.com/developers/applications/).
1. Click on "New Application".  
![](https://i.imgur.com/5SSK14E.jpg)
1. Fill in a name for your bot (or just "Libereus"), and click on Create.
1. Click on "Bot" at the left navigation panel, and then "Add Bot".
1. Next, click on "Click to Reveal Token" in the "Build-A-Bot" section and write down the token somewhere, it is required for the installation later. (DO NOT SHARE YOUR TOKEN WITH ANY OTHER PEOPLE, NOT EVEN ANIMALS!)
1. Now click on "OAuth2" on the left navigation panel, scroll down to "Scopes" and then tick on "bot".
1. Scroll further down to find "Bot Permissions" and check on "Administrator".
1. You can now proceed to copy the generated link in the "Scopes" section and open the link in your web browser.
![](https://i.imgur.com/V5kwpNN.jpg)
1. Add the bot into your server through the page.

### Windows
1. Make sure you have Python 3 installed (We recommend python 3.6). (Download it via [python.org](https://www.python.org/downloads/release/python-367/))
1. Download and extract or clone this repository into your computer.
1. Create a copy of "settings.example.json" and rename it into "settings.json"
1. Open the file through your favourite text editor (Notepad may work too).
1. These are the settings for you to tweak. Scroll to the bottom and replace "your bot token here" with the bot token you just obtained from the previous step.
1. Save it. (<kbd>Ctrl</kbd>+<kbd>S</kbd> for most cases)
1. Now open up the Command Prompt by pressing <kbd>Win</kbd>+<kbd>R</kbd>, type in `cmd`, and then press the "OK" button.
1. In the black Command Prompt window, type in the following command. (Make sure you use `cd <your bot folder directory>` to navigate to your folder beforehand).  
`pip3 install -r requirements.txt`
1. To run the bot, double click "bot.py" or do the following command in the bot's directory.
`py -3 bot.py`

### 🍏 Mac
> Unfortunately, this bot requires Python 3 but Mac OS X / macOS ships with Python 2.7 out of the box, thus you need to install Python 3 seperately to run this bot.
1. Open the "Terminal" application.
1. Install [Homebrew](https://brew.sh/) via the following command.  
`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
1. Install Python 3 by entering the command.  
`brew install python3`
1. Clone this repository's master branch.  
`git clone https://github.com/Tansc161/Libereus.git --branch master`
1. Make a copy of settings.json from the example given.  
`cp settings.example.json settings.json`
1. Use your favourite text editor to edit settings.json or use nano in the Terminal.  
`nano settings.json`
1. Replace "your bot token here" with the bot token that you obtained from Step 5 in "Registering an access token for your bot" above. (Please note that you need to enclose your bot token with "quotation marks".)
1. Save the file. (For nano users, press <kbd>Ctrl</kbd>+<kbd>X</kbd>, and then hit <kbd>Y</kbd>, and then hit <kbd>Enter</kbd>.)
1. Now run this command to install the Python libraries required for the bot.  
`pip3 install -r requirements.txt`
1. Run the bot with the following command.  
`python3 bot.py`

### 🐧 Linux
Follow the installation steps for "Mac" above, starting from Step 4.

## Usage
Run `/help` in Discord to see a list of available commands.
All command usage information are in standard function signature syntax, which states `<>` as a required argument and `[]` as an optional argument.

## Developers & Contributors
[rixinsc](https://github.com/Tansc161) `Tansc#8171` [Lead Dev & Founder]

[Proladon](https://github.com/Proladon) `Proladon#7525` [Dev]

[NRockhouse](https://github.com/NRockhouse) `NRockhouse#4157` [Dev & QA]

RedBerrie `RedBerrie#3324` [QA]

## Commands Showcase
### 🔥 Prunemembers (Lack of messages / inactive)
![img](https://i.imgur.com/xIf3F05.gif)

> _*If your server has hundreds or thousands of members, it may take a very long time to search.*_

### 📅 Calculate Date
![img](https://i.imgur.com/qpIsyDg.gif)

### 💣 Minesweeper
![img](https://i.imgur.com/dMtjlVw.jpg)

