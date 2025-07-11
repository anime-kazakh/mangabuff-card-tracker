from enum import Enum
from dataclasses import dataclass
from typing import Type, Optional, Iterable

from requests import Session


MARKET_MAX_PAGES: int

AUTHORIZATION_ERROR_CODE: int

MANGABUFF_URL: str

SELECTOR_META_CSRF: str

SELECTOR_MARKET_CARDS_LIST: str
SELECTOR_MARKET_CARDS_WRAPPER: str

SELECTOR_MARKET_SHOW: str
SELECTOR_MARKET_SHOW_ITEM: str
SELECTOR_MARKET_SHOW_ITEM_PRICE: str

SCRIPT_USER_ID_TEXT: str = ...
SCRIPT_USER_ID_RE: str = ...

SELECTOR_WISH_LIST_CARDS: str = ...

class CardRank(Enum):
    """Перечисления рангов карточек"""

    X: str
    S: str
    A: str
    P: str
    G: str
    B: str
    C: str
    D: str
    E: str
    H: str
    N: str
    V: str
    L: str
    Q: str

    def __str__(self) -> str: ...


@dataclass
class CardInfo:
    """Информация о карточке и активных лотах

    Attributes:
        data_id (str)   : ID карты
        rank (CardRank) : Ранг карты
        name (str)      : Название карточки
        manga_name (str): Название тайтла
        lots (list[str]): Список цен на лоты
    """

    data_id: str
    rank: CardRank
    name: str = ...
    manga_name: str = ...
    lots: list[str] = ...

    def __init__(self,
                 data_id: str,
                 rank: CardRank,
                 name: str=...,
                 manga_name: str=...,
                 lots: list[str]=...
                 ) -> None: ...

    def __str__(self) -> str: ...

    def __hash__(self) -> int: ...

    def __eq__(self, other: "CardInfo") -> bool: ...

    @staticmethod
    def out_list(cards_list: list[CardInfo]) -> str:
        """Вывод списка карт в стрку, в md формате
        Parameters:
            cards_list (list[CardInfo]): Список карт
        """
        ...


class NotAuthorized(Exception):
    """Вызывается когда не авторизован"""
    pass


class MangabuffParser:
    """Парсер торговой площадки mangabuff.ru

    Example:
        >>> with MangabuffParser(mail='user@example.com', password='pass') as parser:
        ...     cards = parser.get_cards_lots(query='тайтл', want=True, rank=CardRank.S)

        >>> parser = MangabuffParser(mail='user@example.com', password='pass')
        >>> cards = parser.get_cards_lots(want=True)
    """

    _request_delay: float|int
    _session: Session
    _user_id: str

    def __init__(self, *, mail: str, password: str, request_delay: float|int = 2.0) -> None:
        """Инициализатор

        Parameters:
            mail (str): Электронная почта для авторизации
            password (str): Пароль от аккаунта
            request_delay (float|int): Задержка перед запросами

        Raises:
            TypeError: Неверные типы аргументов
            ValueError: Пустые строки в электронной почте или пароле
            EmailNotValidError: Почта не прошла валидацию
            NotAuthorized: Не авторован
            HTTPError: Проблемы сетевого характера, ID, CSRF не найден. Проблемы с HTML
        """
        ...

    def __enter__(self) -> "MangabuffParser":
        """Вход в контекстынй менеджер

        Returns:
            MangabuffParser: Экземпляр класса
        """
        ...

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[object]
    ) -> Optional[bool]:
        ...

    def __del__(self) -> None: ...

    def _get_user_id(self) -> None:
        """Получение id пользователя на сайте

        Raises:
            HTTPError: ID не найден. Проблемы с HTTP или со HTML страницей
        """
        pass

    def _login(self, mail: str, password: str) -> None:
        """Авторизация на mangabuff.ru

        Parameters:
            mail (str): Электронная почта для авторизации
            password (str): Пароль от аккаунта

        Raises:
            HTTPError: Не найден CSRF токен либо ошибка в обработке ответа
            NotAuthorized: Не авторован
        """
        ...

    def _close(self) -> None:
        """Закрытие сессии"""
        ...

    def _parse_market(self, *, url: str, rank: Iterable[CardRank]) -> Iterable[CardInfo]:
        """Парсинг основной страницы торговой площадки

        Parameters:
            url (str): URL страницы с параметрами
            rank (Iterable[CardRank]): Выбранный ранг

        Returns:
            list[CardInfo]: ID карточкек, Ранг карточки
        """
        ...

    def _parse_wish_list(self) -> Iterable[CardInfo]:
        """Парсинг списка желаемых карточек

        :return:
            list[CardInfo]: Список всех желаемых пользователем карточек с названиями тайтлов
        """
        ...

    def _parse_cards_lots(self, *, cards_list: Iterable[CardInfo]) -> Iterable[CardInfo]:
        """Парсинг страниц лотов кард

        Parameters:
            cards_list (Iterable[CardInfo]): Список кард

        Returns:
            list[CardInfo]: Входной список карт с именем карточки и лотами
        """
        ...

    def get_cards_lots(
            self,
            *,
            query: Optional[str]=None,
            want: bool=False,
            rank: Optional[CardRank]=None
    ) -> Iterable[CardInfo]:
        """Получает информацию о карточках и лотах

        Parameters:
            query (Optional[str]): Запрос посика
            want (bool): Флаг желаемых карточек
            rank (Optional[CardRank]): Ранг карточки

        Returns:
            list[CardInfo]: ID, Ранг, Название, Название тайтла, Лоты карточек

        Examples:
            >>> parser = MangabuffParser(mail='user@example.com', password='pass')
            >>> parser.get_cards_lots(query='Тайтл', want=True, rank=CardRank.C)
        """
        ...
