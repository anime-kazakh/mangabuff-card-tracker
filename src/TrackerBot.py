from datetime import time

from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CallbackContext, CommandHandler

from resources.messages import *
from MangabuffParser import MangabuffParser


class TrackerBot:
    def __init__(self, *, token: str, chat_id: str, parser: MangabuffParser, timestamps: list[time]):
        self._chat_id = chat_id
        self._parser = parser
        self._timestamps = timestamps

        self._app = ApplicationBuilder()\
            .token(token)\
            .post_init(self._post_init_bot())\
            .build()

        self._app.add_handler(CommandHandler("start", self._start))

    def _message(self):
        async def callback(context: CallbackContext):
            try:
                await context.bot.send_message(
                    chat_id=self._chat_id,
                    text=self._parser.get_want_market_formatted(),
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(e)
        return callback

    def _post_init_bot(self):
        async def callback(application: Application):
            job_queue = application.job_queue

            for time_ in self._timestamps:
                job_queue.run_daily(
                    callback=self._message(),
                    time=time_,
                    name=f"daily_{time_.hour}hour_message_job",
                    chat_id=int(self._chat_id)
                )
        return callback

    @staticmethod
    async def _start(update: Update, _):
        await update.message.reply_text(START_MESSAGE)

    def run(self):
        self._app.run_polling()