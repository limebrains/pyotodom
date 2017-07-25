#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging

from otodom.category import get_category
from otodom.offer import get_offer_information

log = logging.getLogger(__file__)

SCRAPE_LIMIT = os.environ.get('SCRAPE_LIMIT', None)

if __name__ == '__main__':
    input_dict = {'[filter_float_price:from]': 0, '[created_since]': 1}

    if os.getenv('PRICE_TO'):
        input_dict['[filter_float_price:to]'] = os.getenv('PRICE_TO')

    parsed_category = get_category("wynajem", "mieszkanie", "sopot", **input_dict)

    log.info("Offers in that category - {0}".format(len(parsed_category)))

    if SCRAPE_LIMIT:
        parsed_category = parsed_category[:int(SCRAPE_LIMIT)]
        log.info("Scarping limit - {0}".format(len(parsed_category)))

    for offer in parsed_category:
        log.info("Scarping offer - {0}".format(offer['detail_url']))
        offer_detail = get_offer_information(offer['detail_url'], context=offer)
        log.info("Scraped offer - {0}".format(offer_detail))
