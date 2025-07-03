from os import getenv
import logging

from dotenv import load_dotenv

from MangabuffParser import MangabuffParser, CardRank


logger = logging.getLogger(__name__)

load_dotenv()

def main():
    logging.basicConfig(filename="mangabuff-card-tracker.log", level=logging.INFO)
    mail = getenv("MANGABUFF_MAIL")
    password = getenv("MANGABUFF_PASSWORD")
    mb_parser = MangabuffParser(mail=mail, password=password)
    print(mb_parser.get_cards_lots(query='Восхождение в тени', want=True, rank=CardRank.D))


if __name__ == '__main__':
    main()
