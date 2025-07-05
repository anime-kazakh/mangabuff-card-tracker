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
        self.mock_response_get = MagicMock()
        self.mock_response_get.content = f"<html><head><meta name='csrf-token' content='{self.csrf_token}'></head></html>"
        self.mock_session.get = MagicMock(return_value=self.mock_response_get)

        self.mock_response_post = MagicMock()
        self.mock_response_post.status_code = 200
        self.mock_session.post = MagicMock(return_value=self.mock_response_post)

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
        self.mock_response_get.content = "<html><head></head></html>"
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
        self.mock_response_post.status_code = AUTHORIZATION_ERROR_CODE
        with patch("requests.Session", return_value=self.mock_session):
            with self.assertRaises(NotAuthorized):
                MangabuffParser(mail=VALID_EMAIL, password=VALID_PASSWORD)


class TestMarketParsingMangabuffParser(TestCase):
    @classmethod
    @patch("request.Session", MagicMock())
    def setUpClass(cls, mock_session):
        mock_session.headers = dict()

        mock_response_get = MagicMock()
        mock_response_get.content = f"<html><head><meta name='csrf-token' content='test_token'></head></html>"
        mock_session.get = MagicMock(return_value=mock_response_get)

        mock_response_post = MagicMock()
        mock_response_post.status_code = 200
        mock_session.post = MagicMock(return_value=mock_response_post)

        cls.parser = MangabuffParser(mail=VALID_EMAIL, password=VALID_PASSWORD)


if __name__ == '__main__':
    main()
