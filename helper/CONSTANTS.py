"""
Constants or regular expressions used in application.
"""

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
MAC_REGEX = r'^([0-9a-fA-F]{1,2})' + '[\:\-]([0-9a-fA-F]{1,2})'*5 + '$'
IP_REGEX = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)' \
           r'{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
USERNAME_REGEX = r'^[A-Za-z][A-Za-z0-9_.]*$'
