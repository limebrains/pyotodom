#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
import pickle
import sys
from bs4 import BeautifulSoup

import otodom.category as category
import otodom.offer as offer
import otodom.utils as utils

if sys.version_info < (3, 3):
    from mock import mock
else:
    from unittest import mock
REGIONS_TO_TEST = [
    "Gdań", "Sop", "Oliw", "Wrzeszcz", "czechowice", "Nowa Wieś", "pomorskie", "Książąt pomor sopot", ""
]
ACTUAL_REGIONS = [
    {"city": "gdansk_40"}, {"city": "sopot_208"}, {"[district_id]": 51316, "city": "gdansk_40"},
    {"[district_id]": 30,"city": "gdansk_40"}, {"city": "czechowice-dziedzice_2258"}, {"city": "nowa-wies_6001"},
    {"voivodeship": "pomorskie"}, {"[street_id]": 15544, "city": "sopot_208"}, {}
]

@pytest.mark.parametrize(
    'text,dic,expected_value', [
        ('ala', {'a': 'b'}, 'blb'),
        ('Gdańsk', {'ń': 'n'}, 'Gdansk')
     ])
def test_replace_all(text, dic, expected_value):
    assert utils.replace_all(text, dic) == expected_value


@pytest.mark.parametrize(
    'text,expected_value', [
        ('ala MA KoTa', 'ala-ma-kota'),
        ('Gdańsk', 'gdansk')
     ])
def test_normalize_text(text, expected_value):
    assert utils.normalize_text(text) == expected_value


@pytest.mark.parametrize('filters,expected_value', zip(ACTUAL_REGIONS, ACTUAL_REGIONS))
def test_get_region_from_filters(filters, expected_value):
    assert utils.get_region_from_filters(filters) == expected_value


def test_get_region_from_autosuggest():
    with mock.patch("otodom.utils.json.loads") as json_loads:
        utils.get_region_from_autosuggest("gda")
        json_loads.called


@pytest.mark.parametrize("main_category", ["wynajem", "sprzedaz"])
@pytest.mark.parametrize("detail_category", [
    "mieszkanie", "dom", "pokoj", "dzialka", "lokal", "haleimagazyny", "garaz", ""])
@pytest.mark.parametrize("get_region_from_autosuggest_value", ACTUAL_REGIONS)
@pytest.mark.parametrize("region", REGIONS_TO_TEST)
def test_get_url(main_category, detail_category, region, get_region_from_autosuggest_value):
        with mock.patch("otodom.utils.get_region_from_autosuggest") as get_region_from_autosuggest:
            get_region_from_autosuggest.return_value = get_region_from_autosuggest_value
            assert utils.get_url(main_category, detail_category, region)


def test_get_response_for_url():
    with mock.patch("otodom.utils.requests.get") as get:
        utils.get_response_for_url("")
        assert get.called


@pytest.mark.skipif(sys.version_info <= (3, 1), reason="requires Python3")
@pytest.mark.parametrize(
    'markup_path,expected_value', [
        ("test_data/markup_no_offers", "95c3ad18f9c716209fdfc5d73b13f4a64fd12fc7ca9b6d0d4a5f60ce80b574b3"),
        ("test_data/markup_offers", "d6e9f6202c0fd68ddc539a54bd728d59aa27d7276470818a57ed7c3c2db5f612")
    ])
def test_get_csrf_token(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert utils.get_csrf_token(pickle.load(markup_file)) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize(
    'markup_path,expected_value', [
        ("test_data/markup_offer", {
            'detail_url': "https://www.otodom.pl/oferta/wrzeszcz-garnizon-3-pokoje-65-m-kw-ID3j9gi.html#9dd7c45485",
            'offer_id': '3j9gi',
            'poster': ""
        })
    ])
def test_parse_category_offer(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert category.parse_category_offer(pickle.load(markup_file)) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [("test_data/markup_offer", [])])
def test_parse_category_content(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert category.parse_category_content(pickle.load(markup_file)) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value',
                         [("test_data/markup_offers", 12), ("test_data/markup_no_offers", 1)])
def test_get_category_number_of_pages(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert category.get_category_number_of_pages(pickle.load(markup_file)) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value',
                         [("test_data/markup_offers", True), ("test_data/markup_no_offers", False)])
def test_was_category_search_successful(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert category.was_category_search_successful(pickle.load(markup_file)) == expected_value


def test_get_category():
    with mock.patch("otodom.category.get_url") as get_url,\
            mock.patch("otodom.category.get_response_for_url") as get_response_for_url,\
            mock.patch("otodom.category.was_category_search_successful") as was_category_search_successful,\
            mock.patch("otodom.category.parse_category_content") as parse_category_content,\
            mock.patch("otodom.category.get_category_number_of_pages", return_value=1) as get_category_number_of_pages:
        category.get_category("", "", "")
        assert get_url.called
        assert get_response_for_url.called
        assert was_category_search_successful.called
        assert parse_category_content.called
        assert get_category_number_of_pages.called


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [
    (
        "test_data/offer",
        'Zobacz to 3 pokojowe mieszkanie na wynajem w miejscowości Gdańsk, Oliwa,  Aleksandra Majkowskiego, '
        'za cenę 379 zł/miesiąc. To mieszkanie na wynajem  na parter piętrze ma 92 m² powierzchni użytkowej i '
        '92 m² powierzchni całkowitej. Właściciel jako najważniejsze zalety mieszkania wymienia: piwnica, '
        'oddzielna kuchnia, telewizja kablowa. Otodom 48721860'
    )
])
def test_get_offer_facebook_description(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        loaded_data = BeautifulSoup(pickle.load(markup_file), "html.parser")
        assert offer.get_offer_facebook_description(loaded_data) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [("test_data/offer", '0')])
def test_get_offer_floor(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_floor(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [("test_data/offer", '')])
def test_get_offer_total_floors(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_total_floors(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [("test_data/offer", 'Joanna')])
def test_get_offer_poster_name(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_poster_name(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [("test_data/offer", '')])
def test_get_offer_3d_walkaround_link(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_3d_walkaround_link(
            BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [
    ("test_data/offer", 'Gdańsk Apartament OlivaSeaside mieszkanie na doby')
])
def test_get_offer_title(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_title(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [
    ("test_data/offer", 'Gdańsk, Oliwa,  Aleksandra Majkowskiego')
])
def test_get_offer_address(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_address(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [
    ("test_data/offer", [
        {'Nr oferty w Otodom': '48721860'},
        {'Liczba wyświetleń strony': '1143'},
        {'Data dodania': 'ponad 14 dni temu'},
        {'Data aktualizacji': 'ponad 14 dni temu'}
    ])
])
def test_get_offer_details(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_details(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [("test_data/offer", ('54.4092043', '18.570687700000008'))])
def test_get_offer_geographical_coordinates(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_geographical_coordinates(
            BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [("test_data/offer", "")])
def test_get_offer_video_link(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_video_link(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [
    ("test_data/offer", [
        'https://img41.otodom.pl/images_otodompl/16961046_6_1280x1024_gdansk-apartament-'
        'olivaseaside-mieszkanie-na-doby-.jpg',
        'https://img40.otodom.pl/images_otodompl/16961046_4_1280x1024_gdansk-apartament-'
        'olivaseaside-mieszkanie-na-doby-wynajem.jpg',
        'https://img42.otodom.pl/images_otodompl/16961046_5_1280x1024_gdansk-apartament-'
        'olivaseaside-mieszkanie-na-doby-pomorskie.jpg',
        'https://img40.otodom.pl/images_otodompl/16961046_8_1280x1024_gdansk-apartament-'
        'olivaseaside-mieszkanie-na-doby-.jpg',
        'https://img40.otodom.pl/images_otodompl/16961046_7_1280x1024_gdansk-apartament-'
        'olivaseaside-mieszkanie-na-doby-.jpg',
        'https://img41.otodom.pl/images_otodompl/16961046_9_1280x1024_gdansk-apartament-'
        'olivaseaside-mieszkanie-na-doby-.jpg',
        'https://img41.otodom.pl/images_otodompl/16961046_1_1280x1024_gdansk-apartament-'
        'olivaseaside-mieszkanie-na-doby-gdansk.jpg',
        'https://img41.otodom.pl/images_otodompl/16961046_3_1280x1024_gdansk-apartament-'
        'olivaseaside-mieszkanie-na-doby-mieszkania.jpg',
        'https://img42.otodom.pl/images_otodompl/16961046_2_1280x1024_gdansk-apartament-'
        'olivaseaside-mieszkanie-na-doby-dodaj-zdjecia.jpg'
    ])
])
def test_get_offer_photos_links(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_photos_links(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [
    ("test_data/offer", [
        'zmywarka', 'lodówka', 'meble', 'kuchenka', 'telewizor', 'pralka', 'domofon / wideofon',
        'telewizja kablowa', 'internet', 'piwnica', 'oddzielna kuchnia'
    ])
])
def test_get_offer_additional_assets(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_additional_assets(
            BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [
    ("test_data/offer", [{'kaucja': '800 zł'}, {'rodzaj zabudowy': 'kamienica'}])
])
def test_get_offer_apartment_details(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_apartment_details(
            BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [
    (
        "test_data/offer",
        ' Apartament 3-pokojowy z oddzielną kuchnią dla maksymalnie 8 osób, wynajem na doby od 28.06.2017!! '
        'Cena za dobę wynosi: a) 4 osoby- 379 PLN/ doba b) 5 osób- 439 PLN/ doba c) 6 osób- 499 PLN/ doba d) '
        '7 osób - 549 PLN/ doba e) 8 osób- 599 PLN/ doba  Minimalna długość pobytu to 3 dni.  Przy rezerwacji '
        'pobytu powyżej 7 dni oferujemy 10% zniżki na cały pobyt!!! Całe mieszkanie przy wynajmie jest do Państwa '
        'dyspozycji to również całkowita niezależność oraz prywatność.  Apartament Oliva Seaside położony jest w '
        'Gdańsku Oliwie, najpiękniejszej i pełnej zieleni części Gdańska, w pobliżu sławnej Katedry Oliwskiej, '
        'Parku Botanicznego, Ogrodu Oliwskiego z Pałacem, Największego ZOO w Polsce i rozległego leśnego '
        'Trójmiejskiego Parku Krajobrazowego ze wzgórzami, dolinami, strumieniami i pomnikami przyrody.  '
        'Mieszkanie znajduje się w odległości 9km do Starówki Gdańskiej (około 12 minut drogi '
        'Szybką Koleją Miejską SKM), pod samą granicą z Sopotem. Jednocześnie jest stąd łatwe i '
        'szybkie połączenie do Gdyni i Centrum Gdańska (jesteśmy praktycznie w samym środku Trójmiasta '
        'i w odległości 100m znajduje się pętla tramwajowa oraz postój taksówek)a także 10 min drogi autem '
        'od jednej z najpiękniejszych plaż w Trójmieście- Jelitkowa. W pobliżu restauracje, biblioteka, '
        'centrum handlowe, MC Donald itd.  Apartament jest duży i przestronny, jest świeżo po remoncie, '
        'urządzony w nowoczesnej skandynawskiej stylistyce i w wyższym standardzie. . Składa się z '
        '3 pokoi (3-osobowy, 2-osobowy oraz 3-osobowy), 2 łazienek oraz dużej przestronnej kuchni z '
        'dwiema lodówkami. Jest idealny na pobyt czterech dorosłych osób z małymi dziećmi. W każdym '
        'pokoju znajduje się telewizor LCD z dostępem do kanałów kablowych,biurko do pracy, pojemne '
        'szafy zamykane na kluczyk, pond to w lokalu 2 łazienki z kabiną prysznicową, jak również pościel '
        'oraz ręczniki. Goście mogą korzystać z bezpłatnego WiFi. W mieszkaniu znajduje się całe niezbędne '
        'wyposażenie kuchenne (lodówki, zmywarka, czajnik, sztućce, garnki, mikrofala) oraz dwie pralki i pościel '
        'Na Państwa życzenie, dla małego dziecka i po wcześniejszych ustaleniach możemy zaoferować łóżeczko '
        'turystyczne.   Polecamy na dłuższy pobyt wakacyjny!  24.08-27.08 ZAREZERWOWANE  '
    )
])
def test_get_offer_description(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_description(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


def test_get_offer_phone_numbers():
    with mock.patch("otodom.offer.requests.request") as request,\
            mock.patch("otodom.offer.json.loads") as json_loads:
        assert offer.get_offer_phone_numbers("", "", "")
        assert request.called
        assert json_loads.called


@pytest.mark.skipif(sys.version_info < (3, 1), reason="requires Python3")
@pytest.mark.parametrize('markup_path,expected_value', [
    (
        "test_data/offer",
        {
            "language": "pl_PL",
            "platform": "desktop",
            "trackPage": "ad_page",
            "event_type": "pv",
            "action_type": "ad_page",
            "user_status": "unlogged",
            "category": 102,
            "cat_l1_id": 102,
            "cat_l1_name": "Flat",
            "business": "rent",
            "ad_id": 48721860,
            "ad_impressions": [48703160],
            "ad_position": [1],
            "ad_photo": 9,
            "poster_type": "private",
            "seller_id": "769139",
            "ad_price":379,
            "price_currency": "PLN",
            "region_id": "11",
            "region_name": "pomorskie",
            "city_id": "40",
            "city_name": "Gdańsk",
            "district_id": "16",
            "district_name": "Oliwa",
            "surface": "92",
            "rooms": "3",
            "ad_packages": "paid_for_post_30"
        }
    )
])
def test_get_offer_ninja_pv(markup_path, expected_value):
    with open(markup_path, "rb") as markup_file:
        assert offer.get_offer_ninja_pv(BeautifulSoup(pickle.load(markup_file), "html.parser")) == expected_value


@pytest.mark.parametrize("url,context", [
    (
        "https://www.otodom.pl/oferta/gdansk-apartament-olivaseaside-mieszkanie-na-doby-ID3iqMs.html",
        {
            'detail_url': 'https://www.otodom.pl/oferta/'
                          'gdansk-apartament-olivaseaside-mieszkanie-na-doby-ID3iqMs.html#a7099545ba',
            'offer_id': '3iqMs',
            'poster': 'Oferta prywatna'
        }
    )
])
def test_get_offer_information(url, context):
        with mock.patch("otodom.offer.get_response_for_url") as get_response_for_url,\
                mock.patch("otodom.offer.BeautifulSoup") as BeautifulSoup,\
                mock.patch("otodom.offer.get_cookie_from") as get_cookie_from, \
                mock.patch("otodom.offer.get_csrf_token") as get_csrf_token, \
                mock.patch("otodom.offer.get_offer_phone_numbers") as get_offer_phone_numbers, \
                mock.patch("otodom.utils.replace_all") as replace_all, \
                mock.patch("otodom.offer.get_offer_ninja_pv") as get_offer_ninja_pv, \
                mock.patch("otodom.offer.get_offer_total_floors"), \
                mock.patch("otodom.offer.get_offer_apartment_details"):
            assert offer.get_offer_information(url, context)
            assert get_response_for_url.called
            assert BeautifulSoup.called
            assert get_cookie_from.called
            assert get_csrf_token.called
            assert get_offer_phone_numbers
            assert replace_all
            assert get_offer_ninja_pv


