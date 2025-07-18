import os
import json


START_MESSAGE: str

MANGA_NAME_OUTPUT_STRING: str
CARD_OUTPUT_STRING: str

def message_init():
    current_dir = os.path.dirname(__file__)
    bot_message_file = "bot_commands_messages.json"
    cards_output_file = "cards_output.json"

    bot_message_file = os.path.join(current_dir, bot_message_file)
    cards_output_file = os.path.join(current_dir, cards_output_file)

    global START_MESSAGE

    with open(bot_message_file, encoding="utf-8") as f:
        messages = json.load(f)
        START_MESSAGE = messages["start"]

    global MANGA_NAME_OUTPUT_STRING
    global CARD_OUTPUT_STRING

    with open(cards_output_file, encoding="utf-8") as f:
        strings = json.load(f)
        MANGA_NAME_OUTPUT_STRING = strings["manga_name"]
        CARD_OUTPUT_STRING = strings["card_line"]

message_init()

__all__ = ["START_MESSAGE", "MANGA_NAME_OUTPUT_STRING", "CARD_OUTPUT_STRING"]