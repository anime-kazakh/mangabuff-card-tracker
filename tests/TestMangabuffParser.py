from unittest import TestCase, main
from unittest.mock import patch, MagicMock, call

from parameterized import parameterized
from src.MangabuffParser import MANGABUFF_URL, AUTHORIZATION_ERROR_CODE
from src.MangabuffParser import MangabuffParser, NotAuthorized, CardRank, CardInfo


VALID_EMAIL = "testmail@gmail.com"
VALID_PASSWORD = "password123"

MARKET_LIST_CARDS_SELECTOR = "market-list__cards market-list__cards--all manga-cards"
MARKET_CARDS_WRAPPER_SELECTOR = "manga-cards__item-wrapper"

CARD_SHOW_SELECTOR = "card-show"
CARD_SHOW_ITEM_SELECTOR = "market-show__item"
CARD_SHOW_ITEM_PRICE_SELECTOR = "market-show__item-price"


class TestInitLoginMangabuffParser(TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_session.headers = dict()

        self.csrf_token = "test_token"

        self.mock_session.get.return_value.content = f"<meta name=\"csrf-token\" content=\"{self.csrf_token}\">"
        self.mock_session.post.return_value.status_code = 200


    @patch.object(MangabuffParser, "_login")
    def test_init_valid_credentials(self, mock_login):
        """Тест инициализации валидных реквизитов для входа"""
        MangabuffParser(mail=VALID_EMAIL, password=VALID_PASSWORD)
        mock_login.assert_called_once_with(VALID_EMAIL, VALID_PASSWORD)

    @patch.object(MangabuffParser, "_login")
    def test_init_valid_request_delay(self, mock_login):
        """Тест инициализации валидного request delay"""
        valid_req_del = 2.0
        parser = MangabuffParser(
            mail=VALID_EMAIL,
            password=VALID_PASSWORD,
            request_delay=valid_req_del
        )
        self.assertEqual(parser._request_delay, valid_req_del)
        mock_login.assert_called_once_with(VALID_EMAIL, VALID_PASSWORD)

    @parameterized.expand([
        ("   ", VALID_PASSWORD, 2.0, ValueError),
        ("notvalidemail", VALID_PASSWORD, 2.0, ValueError),
        (123, VALID_PASSWORD, 2.0, TypeError),
        (VALID_EMAIL, "   ", 2.0, ValueError),
        (VALID_EMAIL, 123, 2.0, TypeError),
        (VALID_EMAIL, VALID_PASSWORD, 3 + 5j, TypeError),
        (VALID_EMAIL, VALID_PASSWORD, (3, 5), TypeError),
        (VALID_EMAIL, VALID_PASSWORD, -1, ValueError),
        (VALID_EMAIL, VALID_PASSWORD, -2.1, ValueError),
    ])
    @patch.object(MangabuffParser, "_login")
    def test_init_invalid_input_data(self, email, password, req_delay, exc_raise, mock_login):
        """Тест на проверку невалидных данных инициализации"""
        with self.assertRaises(exc_raise):
            MangabuffParser(mail=email, password=password, request_delay=req_delay)
        mock_login.assert_not_called()

    def test_csrf_not_found(self):
        """Тест на отсутствие CSRF токена"""
        self.mock_session.get.return_value.content = "<html></html>"
        with patch("requests.Session", return_value=self.mock_session):
            with self.assertRaises(ValueError):
                MangabuffParser(mail=VALID_EMAIL, password=VALID_PASSWORD)
            self.mock_session.post.assert_not_called()


    def test_login_success(self):
        """Тест успешной авторизации"""
        with patch("requests.Session", return_value=self.mock_session):
            MangabuffParser(mail=VALID_EMAIL, password=VALID_PASSWORD)
            self.mock_session.post.assert_called_once_with(
                MANGABUFF_URL + "/login/",
                headers={"X-Csrf-Token": self.csrf_token},
                data={
                    "email": VALID_EMAIL,
                    "password": VALID_PASSWORD
                }
            )

    def test_login_fail(self):
        """Тест провальной авторизации"""
        self.mock_session.post.return_value.status_code = AUTHORIZATION_ERROR_CODE
        with patch("requests.Session", return_value=self.mock_session):
            with self.assertRaises(NotAuthorized):
                MangabuffParser(mail=VALID_EMAIL, password=VALID_PASSWORD)


class TestGetCardsLots(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_session = MagicMock()
        cls.mock_session.headers = dict()
        cls.mock_session.get.return_value.content = f"<meta name=\"csrf-token\" content=\"test_token\">"
        cls.mock_session.post.return_value.status_code = 200

        with patch("requests.Session", return_value=cls.mock_session):
            cls.parser = MangabuffParser(mail=VALID_EMAIL, password=VALID_PASSWORD)

    @parameterized.expand([
        (1, True, CardRank.X, TypeError),
        ("test query", dict(), CardRank.X, TypeError),
        ("test query", True, set(), TypeError),
        (None, False, CardRank.X, ValueError),
        ("", False, CardRank.X, ValueError),
        ("  ", False, CardRank.X, ValueError),
    ])
    @patch.object(MangabuffParser, "_parse_market")
    @patch.object(MangabuffParser, "_parse_cards_lots")
    def test_get_cards_lots_except(self, query, want, rank, exc_raise, mock_parse_cards_lots, mock_parse_market):
        """Тест входных данных функции get_cards_lots"""
        with self.assertRaises(exc_raise):
            self.parser.get_cards_lots(query=query, want=want, rank=rank)
        mock_parse_market.assert_not_called()
        mock_parse_cards_lots.assert_not_called()

    @parameterized.expand([
        ("test query", True, CardRank.X, f"{MANGABUFF_URL}/market?q=test+query&want=1"),
        (None, True, None, f"{MANGABUFF_URL}/market?want=1"),
        ("  ", True, None, f"{MANGABUFF_URL}/market?want=1"),
        ("test query", False, None, f"{MANGABUFF_URL}/market?q=test+query")
    ])
    @patch.object(MangabuffParser, "_parse_market")
    @patch.object(MangabuffParser, "_parse_cards_lots")
    def test_get_cards_lots_url_build(self, query, want, rank, out_url, mock_parse_cards_lots, mock_parse_market):
        """Тест построения url"""
        mock_parse_market.return_value = list()
        self.parser.get_cards_lots(query=query, want=want, rank=rank)
        mock_parse_market.assert_called_once_with(url=out_url, rank=[rank,] if rank else list(CardRank))
        mock_parse_cards_lots.assert_not_called()

    @patch.object(MangabuffParser, "_parse_market")
    @patch.object(MangabuffParser, "_parse_cards_lots")
    def test_parse_market_return_empty(self, mock_parse_cards_lots, mock_parse_market):
        """Тест возвращаемого пустого списка функцией _parse_market"""
        mock_parse_market.return_value = [ ]
        self.assertEqual(self.parser.get_cards_lots(want=True), list())
        mock_parse_market.assert_called_once()
        mock_parse_cards_lots.assert_not_called()


class TestParseMarket(TestGetCardsLots):
    def setUp(self):
        self.mock_session.get.reset_mock(return_value=True, side_effect=True)
    
    @parameterized.expand([
        ("url?q=q", [CardRank.X,]),
        ("url?q=q", list(CardRank))
    ])
    def test_prase_market_url_build(self, input_url, input_rank):
        """Тест построения url"""
        self.mock_session.get.return_value = MagicMock(content="<html></html>")

        calls = list()
        for rank in input_rank:
            calls.append(call(f"{input_url}&rank={rank}&page=1", timeout=10))
            calls.append(call().raise_for_status())

        self.parser._parse_market(url=input_url, rank=input_rank)
        self.mock_session.get.assert_has_calls(calls)

    @parameterized.expand([
        (
            [
                f"<div class=\"{MARKET_LIST_CARDS_SELECTOR}\">"
                f"<div class=\"{MARKET_CARDS_WRAPPER_SELECTOR}\" data-id=\"1\"></div>"
                f"<div class=\"{MARKET_CARDS_WRAPPER_SELECTOR}\" data-id=\"2\"></div>"
                f"</div>",
                f"<div class=\"{MARKET_LIST_CARDS_SELECTOR}\">"
                f"<div class=\"{MARKET_CARDS_WRAPPER_SELECTOR}\" data-id=\"3\"></div>"
                f"<div class=\"{MARKET_CARDS_WRAPPER_SELECTOR}\" data-id=\"3\"></div>"
                f"<div class=\"{MARKET_CARDS_WRAPPER_SELECTOR}\" data-id=\"4\"></div>"
                f"<div class=\"{MARKET_CARDS_WRAPPER_SELECTOR}\"></div>"
                f"</div>",
                f"<div class=\"{MARKET_LIST_CARDS_SELECTOR}\">"
                f"</div>"
            ],
            [
                CardInfo(data_id="1", rank=CardRank(CardRank.X)),
                CardInfo(data_id="2", rank=CardRank(CardRank.X)),
                CardInfo(data_id="3", rank=CardRank(CardRank.X)),
                CardInfo(data_id="4", rank=CardRank(CardRank.X))
            ]
        ),
        ([f"<html></html>",], []),
    ])
    def test_parse_market(self, mock_content, expect_result):
        """Тест функции _parse_market"""
        content_side_effect = list()
        for content in mock_content:
            content_side_effect.append(MagicMock(content=content))
        self.mock_session.get.side_effect = content_side_effect
        result = self.parser._parse_market(url="url?q=q", rank=[CardRank(CardRank.X),])

        result = set(result)
        expect_result = set(expect_result)

        self.assertEqual(result, expect_result)


class TestParseCardsLots(TestGetCardsLots):
    def setUp(self):
        self.mock_session.get.reset_mock(return_value=True, side_effect=True)

    def test_url_build(self):
        """Тест построения url"""
        self.mock_session.get.return_value = MagicMock(content="<html></html>")
        input_data = [
            CardInfo(data_id="1", rank=CardRank(CardRank.X)),
            CardInfo(data_id="2", rank=CardRank(CardRank.X)),
            CardInfo(data_id="3", rank=CardRank(CardRank.X)),
            CardInfo(data_id="4", rank=CardRank(CardRank.X))
        ]

        calls = list()
        for card in input_data:
            calls.append(call(f"{MANGABUFF_URL}/market/card/{card.data_id}", timeout=10))
            calls.append(call().raise_for_status())

        self.parser._parse_cards_lots(cards_list=input_data)
        self.mock_session.get.assert_has_calls(calls)

    @parameterized.expand([
        (
            [
                CardInfo(data_id="1", rank=CardRank(CardRank.X)),
                CardInfo(data_id="2", rank=CardRank(CardRank.X)),
                CardInfo(data_id="3", rank=CardRank(CardRank.X))
            ],
            [
                CardInfo(data_id="1", rank=CardRank(CardRank.X), name='1', lots=['2X', '3X']),
                CardInfo(data_id="2", rank=CardRank(CardRank.X), name='2', lots=['2X']),
                CardInfo(data_id="3", rank=CardRank(CardRank.X), name='3', lots=[]),
            ],
            [
                f"<div class=\"{CARD_SHOW_SELECTOR}\" data-name=\"1\">"
                f"<div class=\"{CARD_SHOW_ITEM_SELECTOR}\">"
                f"<div class=\"{CARD_SHOW_ITEM_PRICE_SELECTOR}\">2X</div>"
                f"</div>"
                f"<div class=\"{CARD_SHOW_ITEM_SELECTOR}\">"
                f"<div class=\"{CARD_SHOW_ITEM_PRICE_SELECTOR}\">  3X  </div>"
                f"</div>"
                f"</div>",
                f"<div class=\"{CARD_SHOW_SELECTOR}\" data-name=\"2\">"
                f"<div class=\"{CARD_SHOW_ITEM_SELECTOR}\">"
                f"<div class=\"{CARD_SHOW_ITEM_PRICE_SELECTOR}\">2X</div>"
                f"</div>"
                f"</div>",
                f"<div class=\"{CARD_SHOW_SELECTOR}\" data-name=\"3\">"
                f"</div>",
            ]
        ),
        (
            [ CardInfo(data_id="1", rank=CardRank(CardRank.X)) ],
            [ CardInfo(data_id="1", rank=CardRank(CardRank.X), name='1', lots=[]) ],
            [
                f"<div class=\"{CARD_SHOW_SELECTOR}\" data-name=\"1\">"
                f"<div class=\"{CARD_SHOW_ITEM_SELECTOR}\">"
                f"<div class=\"{CARD_SHOW_ITEM_PRICE_SELECTOR}\"></div>"
                f"</div>"
                f"</div>"
            ]
        ),
        (
            [ CardInfo(data_id="1", rank=CardRank(CardRank.X)) ],
            [ CardInfo(data_id="1", rank=CardRank(CardRank.X)) ],
            [ f"<html></html>" ]
        )
    ])
    def test_parse_cards_lots(self, input_data, expect_result, mock_content):
        """Тест функции _parse_cards_lots"""
        content_side_effect = list()
        for content in mock_content:
            content_side_effect.append(MagicMock(content=content))
        self.mock_session.get.side_effect = content_side_effect

        result = self.parser._parse_cards_lots(cards_list=input_data)

        result = set(result)
        expect_result = set(expect_result)

        self.assertEqual(len(result), len(expect_result))

        for card1, card2 in zip(result, expect_result):
            self.assertEqual(card1.data_id, card2.data_id)
            self.assertEqual(card1.rank, card2.rank)
            self.assertEqual(card1.name, card2.name)
            self.assertListEqual(card1.lots, card2.lots)


if __name__ == '__main__':
    main()
