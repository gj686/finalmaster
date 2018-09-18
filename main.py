#Author Andrea Sessa, 2016

import os, logging
from telegram.ext import Updater, CommandHandler, Job
from twitter import *
from user import *

INTERVAL = 1 #15 mins

# Telegram TOKEN
TOKEN = '695404392:AAHt5Th2xSiD-lGkiN4tOA9IcbN0xoicWqg'

# Twitter access data
# Consumer Key (API Key)
CONS_KEY = 'eB1aTOyqYKtvVQc2iVlyg1CL3'
# Consumer Secret (API Secret)
CONS_SECRET = 'hqEkZaJk0yittXWYkWa2Hx72YophngEL6z7nPWBFQGfEBuwxlv'
# Access Token
ACCESS_TOKEN = '941030573128040448-oR3K81rCUTO54ZZOg5Z5WA3SoTrYhEq'
# Access Token Secret
ACCESS_TOKEN_SECRET = 'PLG99Rq2dGgfegADHzFQrJo40nCqD9ah5ygEHWgdKhiWI'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Monitored users
users = [User('atm_informa'), User('TRENORD_treVA')]

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update, job_queue):
    chat_id = update.message.chat_id
    bot.sendMessage(update.message.chat_id, text='Hi! Use /add [username] to monitor a new user')
    if len(users) != 0:
        bot.sendMessage(update.message.chat_id, text='Starting monitoring for: ')
        for u in users:
            bot.sendMessage(update.message.chat_id, text=u.name)

        job = Job(getLastTweets, INTERVAL, repeat=True, context=chat_id)
        job_queue.put(job)

# Add a new twitter user to the monitored user list
def add(bot, update, args):
    chat_id = update.message.chat_id
    users.append(User(args[1]))

def help_handler(bot, update):
    chat_id = update.message.chat_id
    bot.sendMessage(chat_id, text='Use /start to start(or restart) the bot')
    bot.sendMessage(chat_id, text='Use /add [username] to start monitoring a new user')
    bot.sendMessage(chat_id, text='Use /help to get some help :)')

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def getLastTweets(bot, job):
    # Log into twitter
    t = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONS_KEY, CONS_SECRET))
    for u in users:
        tweets = list(reversed(t.statuses.user_timeline(screen_name=u.name)))
        for tweet in tweets:
            if not(tweet['id'] in u.last_tweets):
                bot.sendMessage(job.context, text=tweet['text'])
                u.last_tweets.append(tweet['id'])

def startTelegramBot():
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, pass_job_queue=True))
    dp.add_handler(CommandHandler("add", add, pass_args=True))
    dp.add_handler(CommandHandler("help", help_handler))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

def main():
    startTelegramBot()

if __name__ == '__main__':
    main()
