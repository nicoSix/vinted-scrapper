import random
import time

import requests
from dotenv import dotenv_values

from models.items import VintedItemsSearchResponse
from models.profiles import VintedProfileResponse

config = dotenv_values(".env")

ALL_ITEMS_BASE_URL = 'https://www.vinted.fr/api/v2/catalog/items?search_text='
PROFILE_BASE_URL = 'https://www.vinted.fr/api/v2/users/'


def random_sleep() -> None:
    """Sleep for a random duration between 1 and 3 seconds to mimic human browsing behavior."""
    sleep_duration = random.uniform(1, 3)
    time.sleep(sleep_duration)

if __name__ == '__main__':
    headers = {
        'Accept': config["ACCEPT"],
        'Cookie': config["AUTH_COOKIE"],
        'User-Agent': config["USER_AGENT"],
        'Cache-Control': config["CACHE_CONTROL"]
    }

    search_query = input('Search query: ')

    items_response = requests.get(ALL_ITEMS_BASE_URL + search_query, headers=headers)

    if items_response.ok:
        items = VintedItemsSearchResponse.model_validate(items_response.json()).items

        for i, item in enumerate(items):
            print(f'\nLooking for item {i+1}/{len(items)}...')
            owner_id = str(item.user.id)
            if item.favourite_count > 10:
                random_sleep()
                profile_response = requests.get(PROFILE_BASE_URL + owner_id, headers=headers)

                if profile_response.ok:
                    profile = VintedProfileResponse.model_validate(profile_response.json()).user

                    if profile.bundle_discount is not None and profile.bundle_discount.enabled is True:
                        if any(float(item.fraction) >= 0.4 for item in profile.bundle_discount.discounts):
                            print(f"Profile with interesting item and discounts identified (profile={profile.path}, item={item.path})")
                        else:
                            print(f"Skipping profile, not enough discounts...")
                    else:
                        print("Skipping profile, no discount enabled...")
                else:
                    print("Error while retrieving profile: ", profile_response.json())
            else:
                print('Skipping item, not enough favourites...')

    else:
        print("Error while retrieving items: ", items_response.json())


