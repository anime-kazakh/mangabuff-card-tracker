from unittest import TestCase, main
from unittest.mock import patch

from parameterized import parameterized

from src.MangabuffParser import MangabuffParser, NotAuthorized, CardRank, CardInfo


class TestMangabuffParser(TestCase):
    VALID_EMAIL = "testmail@example.com"
    VALID_PASSWORD = "password123"

    @patch.object(MangabuffParser, "_login")
    def test_init_valid_credentials(self, mock_login):
        """Тест инициализации валидных реквизитов для входа"""
        parser = MangabuffParser(mail=self.VALID_EMAIL, password=self.VALID_PASSWORD)
        self.assertEqual(parser._mail, self.VALID_EMAIL)
        self.assertEqual(parser._password, self.VALID_PASSWORD)
        mock_login.assert_called()

    @patch.object(MangabuffParser, "_login")
    def test_init_invalid_email(self, mock_login):
        """Тест невалидного email"""
        with self.assertRaises(ValueError):
            MangabuffParser(mail="not valid email", password=self.VALID_PASSWORD)
        mock_login.assert_not_called()

    @parameterized.expand([
        ("  ", VALID_PASSWORD),
        (VALID_EMAIL, "  ")
    ])
    @patch.object(MangabuffParser, "_login")
    def test_init_empty_credentials(self, email, password, mock_login):
        """Тест пустых email и password"""
        with self.assertRaises(ValueError):
            MangabuffParser(mail=email, password=password)
        mock_login.assert_not_called()


    @patch.object(MangabuffParser, "_login")
    def test_init_typesafe_credentials(self, mock_login):
        """Тест на проверку типов данных email и password"""
        with self.assertRaises(TypeError):
            MangabuffParser(mail=int(123), password=self.VALID_PASSWORD)
        mock_login.assert_not_called()
        with self.assertRaises(TypeError):
            MangabuffParser(mail=self.VALID_EMAIL, password=int(123))
        mock_login.assert_not_called()




if __name__ == '__main__':
    main()
