from pathlib import Path
from os import getenv
import logging
from datetime import time

from dotenv import load_dotenv

from TrackerBot import TrackerBot
from MangabuffParser import MangabuffParser


logger = logging.getLogger(__name__)

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s - %(message)s"

def main():
    log_file_path = PROJECT_ROOT / "logs" / "mangabuff-card-tracker.log"
    logging.basicConfig(filename=log_file_path, format=LOG_FORMAT, level=logging.INFO, encoding="utf-8")
    logger.info("Starting mangabuff-card-tracker")

    parser = MangabuffParser(
        mail=getenv("MANGABUFF_MAIL"),
        password=getenv("MANGABUFF_PASSWORD")
    )

    tracker = TrackerBot(
        token=getenv("BOT_TOKEN"),
        chat_id=getenv("CHAT_ID"),
        parser=parser,
        timestamps=[
            time(11,0,0),
            time(15, 0, 0)
        ]
    )

    tracker.run()

    logger.info(f"Finished mangabuff-card-tracker")


if __name__ == '__main__':
    main()
