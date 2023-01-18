import os
import logging
import re

import requests

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import fire

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class Memos:
    def __init__(self, memo_api, chat_id) -> None:
        self.chat_id = int(chat_id)
        self.s = requests.session()
        str(memo_api).split()

        self.url = re.search(".*(?=/api/memo)", memo_api)[0]
        self.openId = re.search("(?<=openId=).*", memo_api)[0]
        print(self.url)
        print(self.openId)

    def _post(self, path, json):
        url = f"{self.url}/api/{path}?openId={self.openId}"
        r = self.s.post(url, json=json)
        print(f'{url} {r.status_code} {r.reason}')
        return r

    def post_tag(self, tag):
        data = {"name": f"{tag}"}
        return self._post('tag', data)

    def post_tags(self, content):
        tags = re.findall(r'(?<=#)\w+', content)
        for tag in tags:
            self.post_tag(tag)

    def post_memo(self, content):
        data = {"content": f"{content}",}
        return self._post('memo', data)

    async def text_memo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add the user message to float."""
        if update.message.chat.id != self.chat_id:
            print('You are not the owner of this bot. Only the owner can use this bot.')
            return
        r = self.post_memo(update.message.text)
        self.post_tags(update.message.text)
        await update.message.reply_text(f'{r.status_code} {r.reason}')

    # def media_memo(self, update, context):
    #     media_memo(update, context)


async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def run() -> None:
    """Start the bot."""

    # Init params
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    CHAT_ID = os.environ.get('CHAT_ID')
    MEMO_API = os.environ.get('MEMO_API')

    memos = Memos(chat_id=CHAT_ID, memo_api=MEMO_API)

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(f"{BOT_TOKEN}").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, memos.text_memo))


    application.add_error_handler(error)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

def test(bot_token, chat_id, memo_api, content=None, tag=None):
    memos = Memos(chat_id=chat_id, memo_api=memo_api)
    if content is not None:
        memos.post_memo('memo', content)
    if tag is not None:
        memos.post_tag(tag)

def tags(message):
    print(message)
    ret = re.findall(r'(?<=#)\w+', message)
    print(ret)

if __name__ == '__main__':
    fire.Fire({
        "run": run,
        "test": test,
        "tags": tags,
    })
