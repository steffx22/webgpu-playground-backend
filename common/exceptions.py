from enum import IntEnum

from rest_framework.exceptions import APIException


class ErrorCodes(IntEnum):
    REGISTER_EMAIL_IN_USE = 100
    REGISTER_USERNAME_IN_USE = 101
    PASSWORD_TOO_SHORT = 150
    LOGIN_INVALID_CREDENTIALS = 200
    FILE_NAME_IN_USER = 300
    INVALID_FILE_PATH = 400
    SAVE_FILE_NO_IMAGE = 500
    INVALID_RATING = 600
    PROFANITY_ERROR = 700
    USER_NOT_ADMIN = 800
    USER_DOES_NOT_EXIST = 801


class CustomAPIException(APIException):
    def __init__(self, detail, code):
        self.detail = {'error': detail, 'code': code}
