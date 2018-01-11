"""
    simple discord bot to understand discord api
    and web-scrapping and coroutines and etc...
"""
from bs4 import BeautifulSoup
import certifi
import urllib3
import asyncio
import random
import re
from datetime import datetime, date
from discord.ext import commands


TOKEN_FILE = '4jvuhvm1p34ji.txt'
RULE_FILE = 'rules.txt'
ERROR_READ = 'Error. Could not read data.'


def get_content(filename):
    with open(filename) as file:
        content = [line.strip(' ') for line in file.readlines() if not line.strip(' ') == '']
    file.close()
    return content


def get_bitcoin():
    global ERROR_READ
    url = 'https://cryptowat.ch/'
    page = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')
    try:
        bitcoin_price = soup.find('div', attrs={'class': 'rankings-col__header__segment'}).text.replace('BTCusd ', '$')
        bitcoin_change = soup.find('div', attrs={'class': 'rankings-col__header__segment'
                                                          ' rankings-col__header__segment--right'}).text
        return "BTC: {}, change: {}".format(bitcoin_price, bitcoin_change)
    except AttributeError:
        return ERROR_READ


currencies = {
    'bitcoin': get_bitcoin
}

TOKEN = get_content(TOKEN_FILE).pop()
bot = commands.Bot(command_prefix='?', description='general_command')


@bot.event
async def on_ready():
    """
    prints to the console when the bot becomes online
    :return:
    """
    print('Logged in as: {}'.format(bot.user.name))
    print('Bot user: {}'.format(bot.user))
    print('----------------------------')
    print('| created : 28/12/2017     |')
    print('| last updated: 06/01/2018 |')
    print('| author: Alex             |')
    print('----------------------------')


@bot.event
async def on_message(message):
    """
    prints a greet in the channel it was greeted
    :param message: MessageObject
    :return: None
    """
    await bot.process_commands(message)
    if message.author != bot.user and re.findall('[hH](ello|i|I) bot', message.content):
        await bot.send_message(message.channel, 'Hello {}!'.format(message.author))


@bot.event
async def on_member_join(member):
    """
    prints a message in the :default channel: whenever a member joins the server
    :param member: MemberObject
    :return:
    """
    default = member.server.default_channel
    await bot.send_message(default, 'Welcome to {}, {}!'.format(member.server, member.name))


@bot.command()
async def roll_dice(repeat: int=1):
    """
    rolling a dice for you
    roll_dice 'number' if you wish to roll 'number' times
    """
    for _ in range(repeat):
        await bot.say(random.choice([x for x in range(1, 7)]))


@bot.command()
async def price(interval: int = 2, currency='bitcoin', hour=datetime.now().hour, input_date=str(date.today())):
    """
        currency prints current price of euro at 2 min interval for 1 hours
        price 'currency' 'interval' 'hour' 'date' - prints 'currency' price every 'minutes' until 'hour', 'date'.
        If not specified hour, are current hour and date respectively date format 'yyyy-mm-dd' and 24h format
        """
    global ERROR_READ
    global currencies
    interval *= 60
    input_date = [int(item) for item in input_date.split('-')]
    try:
        input_date = date(*input_date)
    except ValueError:
        print('Invalid time format.')
    hour = int(hour)

    while date.today() <= input_date and datetime.now().hour <= hour:
        try:
            data = currencies[currency]()
            if not data == ERROR_READ:
                await bot.say(data)
                await asyncio.sleep(interval)
            else:
                await bot.say(ERROR_READ)
                break
        except KeyError:
            await bot.say('Invalid currency.')
            break


@bot.command()
async def rules(filename=RULE_FILE):
    """
    display rules for current server
    """
    await bot.say(rules)
    for rule in get_content(filename):
        await bot.say(rule)


bot.run(TOKEN)
