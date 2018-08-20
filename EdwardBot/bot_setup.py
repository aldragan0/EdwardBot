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


TOKEN_FILE = 'token_file.txt'
RULE_FILE = 'rules.txt'
ERROR_READ = 'Error. Could not read data.'


def get_content(filename):
    with open(filename) as file:
        content = [line.strip(' ') for line in file.readlines() if not line.strip(' ') == '']
    file.close()
    return content


def get_eur():
    global ERROR_READ
    url = 'https://www.xe.com/currencyconverter/convert/?Amount=1&From=EUR&To=USD'
    page = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')
    try:
        eur_price = soup.find('span', attrs={'class': 'uccResultAmount'}).text
        eur_price = '$' + eur_price
        print(eur_price)
        return "EUR: {}".format(eur_price)
    except AttributeError:
        return ERROR_READ


def get_bitcoin():
    global ERROR_READ
    url = 'https://www.worldcoinindex.com/coin/bitcoin'
    page = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')
    try:
        bitcoin_price = soup.find('div', attrs={'class': 'col-md-6 col-xs-6 coinprice'}).text
        bitcoin_price = re.sub("[^0-9.,$]", "", bitcoin_price)
        print(bitcoin_price)
        bitcoin_change = soup.find('div', attrs={'class': 'col-md-6 col-xs-6 coin-percentage'}).text
        bitcoin_change = re.sub("[^0-9.,%\-+]", "", bitcoin_change)
        print(bitcoin_change)
        return "BTC: {}, change: {}".format(bitcoin_price, bitcoin_change)
    except AttributeError:
        return ERROR_READ


def get_ethereum():
    global ERROR_READ
    url = 'https://www.worldcoinindex.com/coin/ethereum'
    page = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()).request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')
    try:
        eth_price = soup.find('div', attrs={'class': 'col-md-6 col-xs-6 coinprice'}).text
        eth_price = re.sub("[^0-9.,$]", "", eth_price)
        print(eth_price)
        eth_change = soup.find('div', attrs={'class': 'col-md-6 col-xs-6 coin-percentage'}).text
        eth_change = re.sub("[^0-9.,%\-+]", "", eth_change)
        print(eth_change)
        return "ETH: {}, change: {}".format(eth_price, eth_change)
    except AttributeError:
        return ERROR_READ


currencies = {
    'btc': get_bitcoin,
    'eur': get_eur,
    'eth': get_ethereum
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
async def roll_dice(dice_size=6, repeat: int=1):
    """
    rolling a dice for you
    roll_dice 'dice_size' if you wish tto roll a dice of size 'dice_size'
    roll_dice 'dice_size' 'number' if you wish to roll a dice of size 'dice_size' 'number' times
    """
    for i in range(repeat):
        await bot.say(random.choice([x for x in range(1, dice_size + 1)]))


@bot.command()
async def rules(filename=RULE_FILE):
    """
    display rules for current server
    """
    await bot.say(rules)
    for rule in get_content(filename):
        await bot.say(rule)


@bot.command()
async def price(currency='btc', interval: int = 2, hour=datetime.now().hour, input_date=str(date.today())):
    """
        currency prints current price of bitcoin at 2 min interval for 1 hours
        price 'currency' 'interval' 'hour' 'date' - prints 'currency' price every 'minutes' until 'hour', 'date'.
        If not specified hour, are current hour and date respectively date format 'yyyy-mm-dd' and 24h format
        """
    global ERROR_READ
    global currencies
    interval *= 60
    input_date = [int(item) for item in input_date.split('-')]
    try:
        print("Processing currency price")
        input_date = date(*input_date)
        print("Done processing currency")
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


bot.run(TOKEN)
