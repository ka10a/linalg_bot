from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import scipy


def start(bot, update):
    update.message.reply_text('Hi, @{}!'.format(update.effective_user.username))


def echo(bot, update):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(open('token').read())
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("add_mark", add_mark, pass_args=True))
    # dp.add_handler(CommandHandler("show_marks", show_marks, pass_args=True))

    # # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
