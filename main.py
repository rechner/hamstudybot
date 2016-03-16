import telebot
from telebot import apihelper
from dblib import sqlite as database
import requests
import os

API_TOKEN = "213661307:AAGolL2Zwow7oO890p2-q2Z29BNizJGYIfE"

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['flashcard',])
def show_flashcard():
    pass

def fetch_pool_id(id):
    # TODO: Handle requests errors (404, etc)
    r = requests.get("https://hamstudy.org/pools/{0}".format(id), verify=False)
    resp = r.json()
    if u'code' in resp.keys() and resp['code'] > 400:
        print("Error fetching pool index from server: {0}".format(resp['message']))
        return

    return r.text

def cache_pools():
    # Fetch each available pool and write them to disc:
    pools_index = requests.get("https://hamstudy.org/pools/", verify=False)
    pools = pools_index.json()
    if u'code' in pools.keys() and pools['code'] > 400:
        print("Error fetching pool index from server: {0}".format(pools['message']))
        return

    pool_ids = []
    for pool in pools:
        for row in pools[pool]:
            pool_ids.append(row['id'])

    for pool in pool_ids:
        path = os.path.join(getScriptPath(), 'pools', "{0}.json".format(pool))
        with open(path, 'w') as f:
            f.write(fetch_pool_id(pool).encode('utf-8'))

def getScriptPath():
   return os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
    cache_pools()
