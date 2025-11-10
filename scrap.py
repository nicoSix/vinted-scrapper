import random
import time
from enum import StrEnum
from typing import Optional, Any

import inquirer
import requests
from dotenv import dotenv_values

from models.items import VintedItemsSearchResponse, VintedItem
from models.profiles import VintedProfileResponse, VintedProfile

config = dotenv_values(".env")

ALL_ITEMS_BASE_URL = 'https://www.vinted.fr/api/v2/catalog/items?search_text='
PROFILE_BASE_URL = 'https://www.vinted.fr/api/v2/users/'

class SearchMode(StrEnum):
    RELEVANCY = 'relevancy'
    MOST_RECENT = 'most_recent'


def _random_sleep() -> None:
    """Sleep for a random duration between 1 and 3 seconds to mimic human browsing behavior."""
    sleep_duration = random.uniform(1, 3)
    time.sleep(sleep_duration)


def _build_items_search_query(mode: SearchMode, search_value: str) -> str:
    """Build the search query URL based on mode and search value."""
    sort_param = 'newest' if mode == SearchMode.MOST_RECENT else 'relevance'
    return f'{ALL_ITEMS_BASE_URL}{search_value}&sort={sort_param}'


def _get_user_input() -> Optional[dict]:
    """Prompt user for search parameters. Returns None if cancelled."""
    questions = [
        inquirer.Text('search_value', message='Search value'),
        inquirer.List('mode',
                     message='Search mode',
                     choices=[
                         ('Most Recent', SearchMode.MOST_RECENT),
                         ('Relevancy', SearchMode.RELEVANCY)
                     ]),
        inquirer.Text('min_favorites',
                     message='Minimum number of favourites',
                     validate=lambda _, x: x.isdigit() and int(x) >= 0,
                     default='0'),
        inquirer.Text('min_discount',
                     message='Minimum discount (in %)',
                     validate=lambda _, x: x.isdigit() and 0 <= int(x) <= 100,
                     default='0'),
    ]
    return inquirer.prompt(questions)


def _fetch_items(search_value: str, mode: SearchMode, headers: dict) -> list[VintedItem]:
    """Fetch items from Vinted API. Returns None on error."""
    url = _build_items_search_query(search_value=search_value, mode=mode)
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


def _process_item(item: VintedItem, min_favorites: int, min_discount: int, headers: dict[str, Any]) -> None:
    """Process a single item: check favorites, fetch profile, and check discounts."""
    if item.favourite_count < min_favorites:
        print('Skipping item, not enough favourites...')
        return

    _random_sleep()
    owner_id = str(item.user.id)
    profile = _fetch_profile(owner_id, headers)

    if profile is None:
        return

    highest_discount = _get_highest_discount(profile)
    if highest_discount < min_discount:
        print(f"Skipping profile, no discount enabled or not enough discounts (discount: {highest_discount:.0f}%)...")
        return

    print(f"Profile with interesting item and discounts identified:\n - discount percentage: {highest_discount}%\n - profile URL: {profile.path}\n - item URL: {item.path})")


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

    items = _fetch_items(search_value, mode, headers)
    if items is None:
        return

    for i, item in enumerate(items):
        print(f'\nLooking for item {i+1}/{len(items)}...')
        _process_item(item, min_favorites, min_discount, headers)


if __name__ == '__main__':
    main()


