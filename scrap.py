import json
import random
import time
from enum import StrEnum
from typing import Optional, Any
from urllib.parse import urlencode
from datetime import datetime, timedelta
import inquirer
import requests
from dotenv import dotenv_values

from models.items import VintedItemsSearchResponse, VintedItem, MatchingItem
from models.profiles import VintedProfileResponse, VintedProfile

config = dotenv_values(".env")

ALL_ITEMS_BASE_URL = 'https://www.vinted.fr/api/v2/catalog/items'
PROFILE_BASE_URL = 'https://www.vinted.fr/api/v2/users/'
WEBSITE_BASE_URL = 'https://www.vinted.fr'

class SearchMode(StrEnum):
    RELEVANCY = 'relevancy'
    MOST_RECENT = 'most_recent'

class PublicationTime(StrEnum):
    LAST_HOUR = 'last_hour'
    TODAY = 'today'
    LAST_THREE_DAYS = 'last_three_days'
    LAST_SEVEN_DAYS = 'last_seven_days'
    LAST_MONTH = 'last_month'
    ALL_TIME = 'all_time'

def _random_sleep() -> None:
    """Sleep for a random duration between 1 and 3 seconds to mimic human browsing behavior."""
    sleep_duration = random.uniform(1, 3)
    time.sleep(sleep_duration)


def _build_items_search_query(mode: SearchMode, search_value: str, min_price: float, max_price: float, brand_ids: list[int]) -> str:
    """Build the search query URL using a query builder."""
    query_params = {
        'search_text': search_value,
        'order': 'newest_first' if mode == SearchMode.MOST_RECENT else 'relevance'
    }

    if min_price > 0:
        query_params['price_from'] = str(min_price)

    if max_price > 0:
        query_params['price_to'] = str(max_price)

    base_query = urlencode(query_params)

    brand_params = '&'.join(f'brand_ids[]={brand_id}' for brand_id in brand_ids)

    if brand_params:
        return f'{ALL_ITEMS_BASE_URL}?{base_query}&{brand_params}'

    return f'{ALL_ITEMS_BASE_URL}?{base_query}'


def _get_user_input() -> Optional[dict]:
    """Prompt user for search parameters. Returns None if cancelled."""
    # Load brands from JSON file
    with open('mappers/brands.json', 'r') as f:
        brands_data = json.load(f)

    brand_choices = [(brand['brand_name'], brand['brand_id']) for brand in brands_data]
    brand_choices.sort(key=lambda x: x[0])

    questions = [
        inquirer.Text('search_value', message='Search value'),
        inquirer.List('mode',
                     message='Search mode',
                     choices=[
                         ('Most Recent', SearchMode.MOST_RECENT),
                         ('Relevancy', SearchMode.RELEVANCY)
                     ]),
        inquirer.List('publication_time',
                      message='Item publication time',
                      choices=[
                          ('Last hour', PublicationTime.LAST_HOUR),
                          ('Today', PublicationTime.TODAY),
                          ('Last 3 Days', PublicationTime.LAST_THREE_DAYS),
                          ('Last 7 Days', PublicationTime.LAST_SEVEN_DAYS),
                          ('Last Month', PublicationTime.LAST_MONTH),
                          ('All Time', PublicationTime.ALL_TIME)
                      ]),
        inquirer.Checkbox('brands',
                         message='Choose brands to search',
                         choices=brand_choices),
        inquirer.Text('min_favorites',
                     message='Minimum number of favourites',
                     validate=lambda _, x: x.isdigit() and int(x) >= 0,
                     default='0'),
        inquirer.Text('min_discount',
                     message='Minimum discount (in %)',
                     validate=lambda _, x: x.isdigit() and 0 <= int(x) <= 100,
                     default='0'),
        inquirer.Text('min_price',
                      message='Minimal price (in €)',
                      validate=lambda _, x: x.isdigit() and float(x) >= 0,
                      default='0'),
        inquirer.Text('max_price',
                      message='Maximum price (in €)',
                      validate=lambda _, x: x.isdigit() and float(x) >= 0,
                      default='9999'),
    ]
    return inquirer.prompt(questions)


def _fetch_items(search_value: str, min_price: float, max_price: float, mode: SearchMode, headers: dict, brand_ids: list[int]) -> list[VintedItem]:
    """Fetch items from Vinted API. Returns None on error."""
    url = _build_items_search_query(search_value=search_value, mode=mode, min_price=min_price, max_price=max_price, brand_ids=brand_ids)
    response = requests.get(url, headers=headers)

    if not response.ok:
        raise Exception("Error while retrieving items", response.json())

    return VintedItemsSearchResponse.model_validate(response.json()).items


def _fetch_profile(owner_id: str, headers: dict) -> VintedProfile:
    """Fetch user profile from Vinted API. Returns None on error."""
    response = requests.get(PROFILE_BASE_URL + owner_id, headers=headers)

    if not response.ok:
        raise Exception("Error while retrieving profile:", response.json())

    return VintedProfileResponse.model_validate(response.json()).user


def _get_highest_discount(profile: VintedProfile) -> float:
    """Get the highest discount percentage from profile. Returns 0 if no discounts available."""
    if profile.bundle_discount is None or not profile.bundle_discount.enabled:
        return 0.0

    if not profile.bundle_discount.discounts:
        return 0.0

    return max(float(discount.fraction) for discount in profile.bundle_discount.discounts) * 100


def _is_item_too_old(item: VintedItem, publication_time: PublicationTime) -> bool:
    """Check if item is older than the specified publication time threshold."""
    if publication_time == PublicationTime.ALL_TIME:
        return False

    item_date = datetime.fromtimestamp(item.photo.high_resolution.timestamp)
    now = datetime.now()

    time_thresholds = {
        PublicationTime.LAST_HOUR: timedelta(hours=1),
        PublicationTime.TODAY: timedelta(days=1),
        PublicationTime.LAST_THREE_DAYS: timedelta(days=3),
        PublicationTime.LAST_SEVEN_DAYS: timedelta(days=7),
        PublicationTime.LAST_MONTH: timedelta(days=30),
    }

    threshold = time_thresholds.get(publication_time)
    return threshold is not None and (now - item_date) > threshold


def _process_item(item: VintedItem, min_favorites: int, min_discount: int, headers: dict[str, Any], publication_time: PublicationTime) -> MatchingItem | None:
    """Process a single item: check favorites, fetch profile, and check discounts."""
    highest_discount = 0.0
    profile_path = "N/A"

    if item.favourite_count < min_favorites:
        print('Skipping item, not enough favourites...')
        return None

    if _is_item_too_old(item, publication_time):
        item_date = datetime.fromtimestamp(item.photo.high_resolution.timestamp)
        print(f'Skipping item, published too long ago ({item_date.strftime("%Y-%m-%d %H:%M:%S")})...')
        return None

    if min_discount > 0:
        _random_sleep()
        owner_id = str(item.user.id)
        profile = _fetch_profile(owner_id, headers)
        profile_path = profile.path
        if profile is None:
            return None

        highest_discount = _get_highest_discount(profile)
        if highest_discount < min_discount:
            print(f"Skipping profile, no discount enabled or not enough discounts (discount: {highest_discount:.0f}%)...")
            return None

    print("Matching item found!")
    return MatchingItem(
        title=item.title,
        amount=item.price.amount,
        currency_code=item.price.currency_code,
        publication_time=datetime.fromtimestamp(item.photo.high_resolution.timestamp),
        highest_discount=highest_discount,
        profile_url=f"{WEBSITE_BASE_URL}{profile_path}",
        item_url=f"{WEBSITE_BASE_URL}{item.path}",
    )


def main() -> None:
    """Main function to orchestrate the Vinted scraping process."""
    headers = {
        'Accept': config["ACCEPT"],
        'Cookie': config["AUTH_COOKIE"],
        'User-Agent': config["USER_AGENT"],
        'Cache-Control': config["CACHE_CONTROL"]
    }

    answers = _get_user_input()
    if answers is None:
        print("\nOperation cancelled.")
        return

    search_value = answers['search_value']
    mode = answers['mode']
    min_favorites = int(answers['min_favorites'])
    min_discount = int(answers['min_discount'])
    min_price = float(answers['min_price'])
    max_price = float(answers['max_price'])
    brand_ids = answers['brands']
    publication_time = answers['publication_time']

    items = _fetch_items(search_value=search_value, min_price=min_price, max_price=max_price, mode=mode, headers=headers, brand_ids=brand_ids)

    if items is None:
        return

    matching_items: list[MatchingItem] = []

    for i, item in enumerate(items):
        print(f'\nLooking for item {i+1}/{len(items)}...')
        maybe_matching_item = _process_item(item=item, min_favorites=min_favorites, min_discount=min_discount, headers=headers, publication_time=publication_time)

        if maybe_matching_item is not None:
            matching_items.append(maybe_matching_item)

    print('Job done. Matching items:\n')
    if len(matching_items) == 0:
        print('No matching items found.')
        return
    else:
        for matching_item in matching_items:
            matching_item.print_item()

if __name__ == '__main__':
    main()


