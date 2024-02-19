#!/usr/bin/env python
# pylint: disable=unused-argument

import logging
import os
import re

from komoot import KomootApi
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TOKEN")
REGEX = r"tour\/(?P<tour_id>[0-9]*).*share_token=(?P<share_token>.*)"

# Enable logging
logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Send a message when the command /start is issued."""
	user = update.effective_user
	logger.info("user: ", user)
	await update.message.reply_text('Welcome to the Komoot bot! I can help you '
	 'to download a Komoot tour as GPX. Send /help to know how I can help you')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Send a message when the command /help is issued."""
	await update.message.reply_text("Share with me a link to a Komoot tour")


async def get_komoot_GPX(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Get the GPX from Komoot"""
	# get the tour id and share token
	matches = re.search(REGEX, update.message.text)
	tour_id = share_token = None

	if not matches:
		await update.message.reply_text("Link not valid")
		return

	if matches.group("tour_id"):
		tour_id = matches.group("tour_id")
	if matches.group("share_token"):
		share_token = matches.group("share_token")

	if not tour_id:
		await update.message.reply_text("Tour id missing from the link")
		return
	if not share_token:
		await update.message.reply_text("Share token missing from the link")
		return

	api = KomootApi()
	status_code, tour = api.fetch_tour(tour_id, share_token)
	if status_code != 200:
		await update.message.reply_text(f"The tour with id {tour_id} can not be found")
		return
	gpx_str, filename = api.make_gpx(tour, add_date=True)

	chat_id = update.message.chat_id
	await context.bot.send_document(chat_id=chat_id, document=str.encode(gpx_str), filename=filename)


def main() -> None:
	"""Start the bot."""
	# Create the Application and pass it your bot's token.
	application = Application.builder().token(TOKEN).build()

	# on different commands - answer in Telegram
	application.add_handler(CommandHandler("start", start))
	application.add_handler(CommandHandler("help", help_command))

	# on non command i.e message - echo the message on Telegram
	application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_komoot_GPX))

	# Run the bot until the user presses Ctrl-C
	application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
	main()
