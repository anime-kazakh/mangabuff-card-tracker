from datetime import time

from telegram.ext import ApplicationBuilder, Application, CallbackContext

from MangabuffParser import MangabuffParser


class TrackerBot:
    def __init__(self, *, token, chat_id, parser: MangabuffParser, timestamps: list[time]):
        self._chat_id = chat_id
        self._parser = parser
        self._timestamps = timestamps

        self._app = ApplicationBuilder()\
            .token(token)\
            .post_init(self._post_init_bot())\
            .build()

    def message(self):
        async def callback(context: CallbackContext):
            try:
                await context.bot.send_message(
                    chat_id=self._chat_id,
                    text=self._parser.get_want_market_formatted()
                )
            except Exception as e:
                print(e)
        return callback

    def _post_init_bot(self):
        async def callback(application: Application):
            job_queue = application.job_queue

            for time_ in self._timestamps:
                job_queue.run_daily(
                    callback=self.message(),
                    time=time_,
                    name=f"daily_{time.hour}hour_message_job",
                    chat_id=self._chat_id
                )
        return callback

    def run(self):
        self._app.run_polling()