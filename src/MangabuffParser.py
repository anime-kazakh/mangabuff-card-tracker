import logging
from time import sleep
from enum import Enum
from urllib.parse import urlencode
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup
from email_validator import validate_email, EmailNotValidError


MARKET_MAX_PAGES = 100

AUTHORIZATION_ERROR_CODE = 422

MANGABUFF_URL = "https://mangabuff.ru"

SELECTOR_META_CSRF = "meta[name='csrf-token']"

SELECTOR_MARKET_CARDS_LIST = "div.market-list__cards.market-list__cards--all.manga-cards"
SELECTOR_MARKET_CARDS_WRAPPER = "div.manga-cards__item-wrapper"

SELECTOR_MARKET_SHOW = "div.card-show"
SELECTOR_MARKET_SHOW_ITEM = "div.market-show__item"
SELECTOR_MARKET_SHOW_ITEM_PRICE = "div.market-show__item-price"

class CardRank(Enum):
    X = "x"
    S = "s"
    A = "a"
    P = "p"
    G = "g"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    H = "h"
    N = "n"
    V = "v"
    L = "l"
    Q = 'q'

    def __str__(self):
        return self.value


@dataclass
class CardInfo:
    data_id: str
    rank: CardRank
    name: str = ''
    lots: list[str] = field(default_factory=list)

    def __str__(self):
        return f"{self.name}: {self.rank} - лоты: {self.lots}"


class NotAuthorized(Exception):
    pass


logger = logging.getLogger(__name__)

class MangabuffParser:
    def __init__(self, *, mail, password, request_delay=2.0):
        logger.info(f"MangabuffParser init called with mail: {mail}, request_delay: {request_delay}")

        try:
            if not isinstance(mail, str) or not isinstance(password, str):
                raise TypeError("mail и password должны быть строками")
            if not mail.strip() or not password.strip():
                raise ValueError("mail и password пустые строки")

            try:
                validate_email(mail)
            except EmailNotValidError:
                raise ValueError("mail не валидный")

            if not isinstance(request_delay, float|int):
                raise TypeError("request_delay должен быть числом")
            if request_delay < 0:
                raise ValueError("request_delay должен быть положительным числом")

            self._request_delay = request_delay
            self._session = requests.Session()

            headers = {
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"
            }
            self._session.headers.update(headers)

            self._login(mail, password)
        except Exception as e:
            logger.critical(e)
            raise e

    def __enter__(self):
        return self

    def _close(self):
        logger.info(f"MangabuffParser session closed")
        try:
            if hasattr(self, "_session"):
                self._session.close()
        except Exception as close_error:
            logger.error(close_error)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
        return False

    def __del__(self):
        self._close()

    def _login(self, mail, password):
        logger.info(f"{mail} - try login")
        url = f"{MANGABUFF_URL}/login/"

        login_page = self._session.get(url, timeout=10)
        login_page.raise_for_status()

        soup = BeautifulSoup(login_page.content, features="html.parser")

        csrf_meta = soup.select_one(SELECTOR_META_CSRF)
        if not csrf_meta:
            raise ValueError("CSRF Token не найден")
        csrf_token = csrf_meta.get("content")

        headers = {
            "X-Csrf-Token": csrf_token
        }

        login_data = {
            "email": mail,
            "password": password,
        }

        response = self._session.post(MANGABUFF_URL + "/login/", headers=headers, data=login_data)
        if response.status_code == AUTHORIZATION_ERROR_CODE:
            raise NotAuthorized("Логин или пароль неверны")
        response.raise_for_status()
        logger.info(f"{mail} - login success")
        logger.info("Session opened")

    def _parse_cards_lots(self, *, cards_list):
        logger.info("Parsing cards lots")
        for card in cards_list:
            url = f"{MANGABUFF_URL}/market/card/{card.data_id}"
            logger.debug(f"url: {url}")

            sleep(self._request_delay) # block safety
            response = self._session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, features="html.parser")

            card_show = soup.select_one(SELECTOR_MARKET_SHOW)
            if not card_show: continue
            card.name = card_show.get("data-name")

            lots_divs = soup.select(SELECTOR_MARKET_SHOW_ITEM)
            if not lots_divs: continue

            for lot in lots_divs:
                price = lot.select_one(SELECTOR_MARKET_SHOW_ITEM_PRICE)
                if not price: continue
                card.lots.append(price.text.strip())

        return cards_list

    def _parse_market(self, *, url, rank):
        logger.info("Parsing market page")
        result = list()

        for current_rank in rank:
            for page in range(1, MARKET_MAX_PAGES + 1):
                url_req = url + f"&rank={current_rank}&page={page}"
                logger.debug(f"Parsing {url_req}")

                sleep(self._request_delay)  # block safety
                response = self._session.get(url_req, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, features="html.parser")

                market_list_cards = soup.select_one(SELECTOR_MARKET_CARDS_LIST)
                if not market_list_cards: break

                cards_wrappers = market_list_cards.select(SELECTOR_MARKET_CARDS_WRAPPER)
                if not cards_wrappers: break

                for wrapper in cards_wrappers:
                    data_id = wrapper.get("data-id")
                    if not data_id and not isinstance(data_id, str): continue
                    result.append(CardInfo(
                        data_id=data_id,
                        rank=current_rank
                    ))

        return result

    def get_cards_lots(self, *, query=None, want=False, rank=None):
        logger.info(f"get_cards_lots called with query: {query}, want: {want}, rank: {rank}")

        try:
            if query:
                if not isinstance(query, str):
                    raise TypeError("Запрос должен быть строкой")

                query = query.strip()

            if not isinstance(want, bool):
                raise TypeError("Флаг want должен быть только True или False")

            if not query and not want:
                raise ValueError("Нет возможности парсить основную страниуц торговой площадки")

            if not isinstance(rank, CardRank|None):
                raise TypeError("rank должен быть CardRank типом")

            rank = list(CardRank) if not rank else [rank,]

            params = {
                "q": query,
                "want": int(want)
            }

            # url = https://mangabuff.ru/market?q=...&want=1
            url = f"{MANGABUFF_URL}/market?{urlencode({k: v for k, v in params.items() if v})}"
            logger.debug(f"Try parse url: {url}")

            result = self._parse_market(url=url, rank=rank)

            if not result: return []

            result = self._parse_cards_lots(cards_list=result)

            return result
        except Exception as e:
            logger.error(e)
            raise e


# __all__ = ["MangabuffParser", "CardRank", "CardInfo", "NotAuthorized"]