from unittest import TestCase, main
from unittest.mock import patch, MagicMock

from parameterized import parameterized
from src.MangabuffParser import MANGABUFF_URL, AUTHORIZATION_ERROR_CODE
from src.MangabuffParser import MangabuffParser, NotAuthorized, CardRank, CardInfo


VALID_EMAIL = "testmail@gmail.com"
VALID_PASSWORD = "password123"

class TestInitLoginMangabuffParser(TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_session.headers = dict()

        self.csrf_token = "test_token"

        self.mock_session.get.return_value.content = f"<meta name='csrf-token' content='{self.csrf_token}'>"
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
        cls.mock_session.get.return_value.content = f"<meta name='csrf-token' content='test_token'>"
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
        mock_parse_market.return_value = list()
        self.parser.get_cards_lots(query=query, want=want, rank=rank)
        mock_parse_market.assert_called_once_with(url=out_url, rank=[rank,] if rank else list(CardRank))
        mock_parse_cards_lots.assert_not_called()

    @patch.object(MangabuffParser, "_parse_market")
    @patch.object(MangabuffParser, "_parse_cards_lots")
    def test_parse_market_return_empty(self, mock_parse_cards_lots, mock_parse_market):
        mock_parse_market.return_value = [ ]
        self.assertEqual(self.parser.get_cards_lots(want=True), list())
        mock_parse_market.assert_called_once()
        mock_parse_cards_lots.assert_not_called()


class TestParseMarket(TestGetCardsLots):
    def setUp(self):
        lst = [
            MagicMock(content="<html></html>"),
            MagicMock(content="<html></html>"),
            MagicMock(content="<html></html>")
        ]
        self.mock_session.get = MagicMock(side_effect=lst)

if __name__ == '__main__':
    main()
