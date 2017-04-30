"""
Module with helping functions to be used in the project at later stages.
"""
import random
import string
import re
from helper.regex_strings import EMAIL


def id_generator(length=8):
    """
    Generates a random string consisting of upper case characters and digits.
    e.g. 6U1S75, 4Z4UKK, U911K4
    :param: length of id (default=8)
    """
    return ''.join(random.choice(string.ascii_uppercase +
                                 string.digits) for _ in range(length))


def generate_secret_key(length=32):
    """
    Generates a secret key consisting of ascii characters, special characters
    and digits.
    e.g. IG0Z[00;QEq;Iy.sZp8>16dv)reQ(R8z
    :param: length of key (default=32)
    """
    return ''.join(random.choice(string.ascii_letters +
                                 string.digits +
                                 '!@#$%^&*().,;:[]{}<>?')
                   for _ in range(length))


def isEmail(email_address):
    """
    Checks if give string is a valid email address or not.
    :param email_address: String
    :return: True if valid otherwise false
    """
    return True \
        if re.compile(EMAIL_REGEX).match(email_address) \
        else False
