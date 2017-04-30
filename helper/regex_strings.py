"""
Constants or regular expressions used in application.
"""

EMAIL = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
MAC = r'^([0-9a-fA-F]{1,2})' + '[\:\-]([0-9a-fA-F]{1,2})'*5 + '$'
IP = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)' \
     r'{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
USERNAME = r'^[A-Za-z][A-Za-z0-9_.]*$'
POSTAL_CODE = r'^[a-zA-Z0-9-_]+$'
