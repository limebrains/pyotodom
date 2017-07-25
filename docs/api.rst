Introduction
============
pyotodom supplies two methods that can be used to scrape data from OtoDom. They are designed to work in tandem, but they can also be used separately.

.. _categories:

======================
Scraping category data
======================
The following method should be used to scrape all the offers compliant with the supplied search parameters

.. autofunction:: otodom.category.get_category

It can be used like this:

::

    input_dict = {'[filter_float_price:to]': 1100}
    parsed_category = scrape.category.get_category("wynajem", "mieszkanie", "gda", **input_dict)

The above code will put a list of dictionaries(string, string) containing all the apartments found in the given category (apartments for rent, in a region starting with "gda", cheaper than 1100 PLN) into the parsed_category variable

===================
Scraping offer data
===================
The following method should be used to scrape all the information about an offer located under the given string. Context is used for phone number scraping. The corresponding field will be empty if it's not provided.

.. autofunction:: otodom.offer.get_offer_information

It can be used like this:

::

    offer_details = []
    for offer in parsed_category:
        offer_details.append(get_offer_information(offer['detail_url'], context=offer))

The above code will populate the offer_details list with all the information about apartments found in parsed_category
