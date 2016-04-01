import telebot
from telebot import apihelper, types
import dpath
import random
import datetime
import requests
import json
import os

from dblib import sqlite as database

API_TOKEN = "213661307:AAGolL2Zwow7oO890p2-q2Z29BNizJGYIfE"

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['flashcard',])
def show_flashcard(message):
    chat_id = message.chat.id
    question = questions.random_question('E2_2014')
    #store question ID for this chat for next reply

    #TODO: random answer order
    text_body = """({id}) {text}
*A.* {answers[A]}
*B.* {answers[B]}
*C.* {answers[C]}
*D.* {answers[D]}""".format(**question)

    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add('A', 'B', 'C', 'D', "I don't know")
    bot.send_message(chat_id, text_body, reply_markup=markup, parse_mode="Markdown")

class QuestionPools(object):
    def __init__(self):
        path = os.path.join(getScriptPath(), "pools.json")
        self.pools = None
        try:
            with open(path, 'rb') as f:
                json_raw = f.read().decode('utf-8')
                pools = json.loads(json_raw)
        except FileNotFoundError:
            print("Unable to open {0}".format(path))
            # Try downloading the pools:
            self.cache_pools()

        if self.pools is None:
            # load the pools
            with open(path, 'rb') as f:
                json_raw = f.read().decode('utf-8')
                self.pools = json.loads(json_raw)

        self.pool_ids = []
        for pool in self.pools:
            for row in self.pools[pool]:
                self.pool_ids.append(row['id'])

        self.questions = {}        
        for pool in self.pool_ids:
            path = os.path.join(getScriptPath(), 'pools', "{0}.json".format(pool))
            with open(path, 'rb') as f:
                json_raw = f.read().decode('utf-8')
                self.questions[pool] = json.loads(json_raw)

            # Build an index of questions from ID -> question
            self.questions[pool]['question_index'] = {}
            for q in dpath.util.search(self.questions[pool],
                                       'pool/*/sections/*/questions/*',
                                       yielded=True):
                self.questions[pool]['question_index'][q[1]['id']] = q[1]
                        

    def random_question(self, pool, subelement=None):
        # Fetch a random question from a particular pool
        if pool not in self.pool_ids:
            raise KeyError("No such pool: {0}".format(pool))
        question_pool = self.questions[pool]

        if subelement is None:
            sections = random.choice(question_pool['pool'])['sections']
        else:
            sections = question_pool['pool'][subelement]['sections']
        
        section = random.choice(sections)
        question = random.choice(section['questions'])
        question['section'] = section['id']

        return question

    def get_next_refresh(self, pools):
        minimum = None
        for pool in pools:
            for row in pools[pool]:
                if row['expires'] is not None:
                    current = datetime.datetime.strptime(row['expires'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if minimum is None or current < minimum:
                        minimum = current
        return minimum

    def fetch_pool_id(self, id):
        # TODO: Handle requests errors (404, etc)
        r = requests.get("https://hamstudy.org/pools/{0}".format(id), verify=False)
        resp = r.json()
        if u'code' in resp.keys() and resp['code'] > 400:
            print("Error fetching pool index from server: {0}".format(resp['message']))
            return

        return r.text

    def cache_pools(self):
        # Fetch each available pool and write them to disc:
        pools_index = requests.get("https://hamstudy.org/pools/", verify=False)
        pools = pools_index.json()
        if u'code' in pools.keys() and pools['code'] > 400:
            print("Error fetching pool index from server: {0}".format(pools['message']))
            return

        path = os.path.join(getScriptPath(), "pools.json")
        with open(path, 'wb') as f:
          f.write(pools_index.text.encode('utf-8'))

        pool_ids = []
        for pool in pools:
            for row in pools[pool]:
                pool_ids.append(row['id'])

        for pool in pool_ids:
            path = os.path.join(getScriptPath(), 'pools', "{0}.json".format(pool))
            with open(path, 'wb') as f:
                f.write(self.fetch_pool_id(pool).encode('utf-8'))

        self.pools = pools
        return pools

def getScriptPath():
   return os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
    questions = QuestionPools()
    questions.random_question('E2_2014')
    #bot.polling()
    #cache_pools()
    #db = database.Database()
    #db.set_meta('next_refresh', None)
    #db['next_refresh'] = 'something'
    #db.commit()

    #db['next_refresh'] = None
    #db.commit()
    # (User is responsible for committing the database changes)

    #print(questions.random_question('E2_2014'))

