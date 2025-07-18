from os import getenv
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from MangabuffParser import MangabuffParser
from resources.messages import *
from src.MangabuffParser import CardInfo

logger = logging.getLogger(__name__)

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(START_MESSAGE)

async def card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mb_parser = MangabuffParser(
        mail=getenv("MANGABUFF_MAIL"),
        password=getenv("MANGABUFF_PASSWORD")
    )
    cards_list = list(mb_parser.get_cards_lots(want=True))
    await update.message.reply_markdown(CardInfo.out_list(cards_list))

def main():
    logging.basicConfig(filename="../logs/mangabuff-card-tracker.log", level=logging.INFO, encoding="utf-8")
    logger.info("Starting mangabuff-card-tracker")

    app = ApplicationBuilder().token(getenv("BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("card", card))

    app.run_polling()

    logger.info(f"Finished mangabuff-card-tracker")


if __name__ == '__main__':
    main()
