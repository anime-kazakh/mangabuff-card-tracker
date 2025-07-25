from datetime import time
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CallbackContext, CommandHandler

from resources.messages import *
from MangabuffParser import MangabuffParser


logger = logging.getLogger(__name__)

class TrackerBot:
    """Класс для инициации Telegram бота"""
    def __init__(
            self,
            *,
            token: str,
            chat_id: str,
            parser: MangabuffParser,
            timestamps: list[time]
    ):
        self._chat_id = chat_id
        self._parser = parser
        self._timestamps = timestamps

        self._app = ApplicationBuilder()\
            .token(token)\
            .post_init(self._post_init_bot())\
            .build()

        self._app.add_handler(CommandHandler("start", self._start))

        logger.info("Bot created")

    def _message(self):
        """Функция замыкание для отправки сообщения
        :return:
        Асинхронная функция для планировщика задач
        """
        async def callback(context: CallbackContext):
            logger.info("Started parsing for message")
            try:
                await context.bot.send_message(
                    chat_id=self._chat_id,
                    text=self._parser.get_want_market_formatted(),
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(e)
            logger.info("Finished parsing for message")
        return callback

    def _post_init_bot(self):
        """post_init функция для Telegram бота
        :return:
        Асинхронная функция для настройки планировщика
        """
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
        """Обработчик команды /start"""
        user = update.effective_user
        logger.debug(f"Received start command: {user.first_name}, id: {user.id}")
        await update.message.reply_text(START_MESSAGE)

    def run(self):
        """Функция run_polling"""
        logger.info("Bot running...")
        self._app.run_polling()