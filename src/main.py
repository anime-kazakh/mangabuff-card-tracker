from pathlib import Path
from os import getenv, makedirs
import logging
from datetime import time

from TrackerBot import TrackerBot
from MangabuffParser import MangabuffParser


# ------------------- ENV - for debug mode ----------------------
DEBUG = getenv("DEBUG", "False").lower().strip() in ('true', '1')
DEBUG = True
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()
# ---------------------------------------------------------------

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s - %(message)s"

def main():
    log_file_path = PROJECT_ROOT / "logs"
    makedirs(log_file_path, exist_ok=True)
    log_file_name = "mangabuff-card-tracker.log"
    logging.basicConfig(filename=log_file_path / log_file_name, format=LOG_FORMAT, level=logging.INFO, encoding="utf-8")
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
            time(15,0,0)
        ]
    )

    print('START - MangaBuff Card Tracker Bot')

    tracker.run()

    logger.info(f"Finished mangabuff-card-tracker")

    print('STOP - MangaBuff Card Tracker Bot')


if __name__ == '__main__':
    main()
