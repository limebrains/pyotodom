import os

import logging

BASE_URL = 'http://www.otodom.pl'

WHITELISTED_DOMAINS = [
    'otodom.pl',
    'www.otodom.pl',
]


if os.getenv('DEBUG'):
    logging.basicConfig(level=logging.INFO)
