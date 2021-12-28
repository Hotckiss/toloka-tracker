import os

from telegram.ext import Updater, CommandHandler

from toloka_tracker.bot.commands import unread_count_command, read_last_message_command, accept_command, \
    reply_text_command


class TolokaTrackerBot:
    def __init__(self):
        self.updater = Updater(os.environ['BOT_TOKEN'])
        self.updater.dispatcher.add_handler(CommandHandler('unread_count', unread_count_command))
        self.updater.dispatcher.add_handler(CommandHandler('read_last_message', read_last_message_command))
        self.updater.dispatcher.add_handler(CommandHandler('accept', accept_command))
        self.updater.dispatcher.add_handler(CommandHandler('reply_text', reply_text_command))


    def run(self):
        self.updater.start_polling()
        self.updater.idle()


if __name__ == "__main__":
    bot = TolokaTrackerBot()
    bot.run()
