import os
import logging

import scrape.category
from scrape.offer import get_offer_information

if os.getenv('DEBUG'):
    logging.basicConfig(level=logging.INFO)

BASE_URL = 'http://www.otodom.pl'
SCRAPE_LIMIT = os.environ.get('SCRAPE_LIMIT', None)

WHITELISTED_DOMAINS = [
    'otodom.pl',
    'www.otodom.pl',
]


if __name__ == '__main__':
    input_dict = {
        '[filter_float_price:to]': 1100,
    }

    parsed_category = scrape.category.get_category("wynajem", "mieszkanie", "gda", **input_dict)
    if SCRAPE_LIMIT:
        parsed_category = parsed_category[:SCRAPE_LIMIT]
    print(len(parsed_category))
    for offer in parsed_category:
        offer_detail = get_offer_information(offer['detail_url'], context=offer)
        print(offer_detail)
