import re

from app.core import error_code, message
from app.helpers.exception_handler import CustomException

REGEX_PHONE_NUMBER = r'(84|0[3|5|7|8|9])+([0-9]{8,9})\b'
REGEX_CARD = r'([0-9]{12}|[0-9]{9})\b'
REGEX_EMAIL = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'


def validate_phone_number(value):
    rule = re.compile(REGEX_PHONE_NUMBER)

    if not rule.search(value):
        raise CustomException(http_code=400, code=error_code.ERROR_132_PHONE_NUMBER_INVALID,
                              message=message.MESSAGE_132_PHONE_NUMBER_INVALID)


def validate_phone(value):
    rule = re.compile(REGEX_PHONE_NUMBER)
    return rule.search(value)


def validate_card(card):
    rule = re.compile(REGEX_CARD)

    if not rule.search(card) or (len(card) != 9 and (len(card) != 12)):
        raise CustomException(http_code=400, code=error_code.ERROR_128_IDENTITY_CARD,
                              message=message.MESSAGE_128_IDENTITY_CARD)


def validate_email(email):
    if (re.search(REGEX_EMAIL, email)):
        return True
    return False

def validate_team_name(team_name):
    if len(team_name) > 255:
        return False
    return True