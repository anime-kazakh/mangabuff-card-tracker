from unittest import TestCase ,main

from src.MangabuffParser import CardInfo, CardRank


class TestCardInfo(TestCase):
    def test_out_list(self):
        input_data = [
            CardInfo(
                data_id="1",
                rank=CardRank(CardRank.X),
                name="test_name",
                manga_name="first manga",
                lots=["1A", "2A"]
            ),
            CardInfo(
                data_id="2",
                rank=CardRank(CardRank.B),
                name="test_name",
                manga_name="second manga",
                lots=["1A", "2A"]
            ),
            CardInfo(
                data_id="3",
                rank=CardRank(CardRank.A),
                name="test_name",
                manga_name="first manga",
                lots=["1A", "2A"]
            ),
            CardInfo(
                data_id="4",
                rank=CardRank(CardRank.X),
                name="test_name",
                manga_name="first manga",
                lots=["1A", "2A"]
            ),
            CardInfo(
                data_id="5",
                rank=CardRank(CardRank.B),
                name="test_name",
                manga_name="second manga",
                lots=["1A", "2A"]
            ),
            CardInfo(
                data_id="6",
                rank=CardRank(CardRank.S),
                name="test_name",
                manga_name="first manga",
                lots=["1A", "2A"]
            ),
        ]
        expect_result = "🥭**first manga**\n"
        for card in filter(lambda x: x.manga_name == "first manga", input_data):
            expect_result += f"\t{card}\n"
        expect_result += "🥭**second manga**\n"
        for card in filter(lambda x: x.manga_name == "second manga", input_data):
            expect_result += f"\t{card}\n"

        self.assertEqual(expect_result, CardInfo.out_list(input_data))


if __name__ == '__main__':
    main()
