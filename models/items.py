from datetime import datetime

from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class Price(BaseModel):
    amount: str
    currency_code: str


class PhotoThumbnail(BaseModel):
    type: str
    url: HttpUrl
    width: int
    height: int
    original_size: Optional[int] = None


class HighResolution(BaseModel):
    id: str
    timestamp: int
    orientation: Optional[int] = None


class Photo(BaseModel):
    id: int
    width: int
    height: int
    temp_uuid: Optional[str] = None
    url: HttpUrl
    dominant_color: str
    dominant_color_opaque: str
    thumbnails: List[PhotoThumbnail]
    is_suspicious: bool
    orientation: Optional[int] = None
    high_resolution: HighResolution
    full_size_url: HttpUrl
    is_hidden: bool
    extra: dict


class User(BaseModel):
    id: int
    login: str
    profile_url: HttpUrl
    photo: Optional[Photo] = None
    business: bool


class ItemPhoto(BaseModel):
    id: int
    image_no: int
    width: int
    height: int
    dominant_color: str
    dominant_color_opaque: str
    url: HttpUrl
    is_main: bool
    thumbnails: List[PhotoThumbnail]
    high_resolution: HighResolution
    is_suspicious: bool
    full_size_url: HttpUrl
    is_hidden: bool
    extra: dict


class Badge(BaseModel):
    title: str


class ItemBox(BaseModel):
    first_line: str
    second_line: str
    exposures: List[str]
    accessibility_label: str
    badge: Optional[Badge] = None
    item_id: int


class SearchTrackingParams(BaseModel):
    score: Optional[float] = None
    matched_queries: List[str]


class VintedItem(BaseModel):
    id: int
    title: str
    price: Price
    is_visible: bool
    brand_title: str
    path: str
    user: User
    conversion: Optional[str] = None
    url: HttpUrl
    promoted: bool
    photo: ItemPhoto
    favourite_count: int
    is_favourite: bool
    service_fee: Price
    total_item_price: Price
    view_count: int
    size_title: str
    content_source: str
    status: str
    item_box: ItemBox
    search_tracking_params: SearchTrackingParams


class GlobalSearchTrackingParams(BaseModel):
    search_correlation_id: str
    global_search_session_id: str | None = None
    search_session_id: str


class Pagination(BaseModel):
    current_page: int
    total_pages: int
    total_entries: int
    per_page: int
    time: int


class VintedItemsSearchResponse(BaseModel):
    items: List[VintedItem]
    search_tracking_params: GlobalSearchTrackingParams
    pagination: Pagination
    code: int



class MatchingItem(BaseModel):
    title: str
    amount: str
    currency_code: str
    publication_time: datetime
    profile_url: str
    item_url: str
    highest_discount: float

    def print_item(self):
        print('Matching item: ')
        print(f"- Title: {self.title}")
        print(f"- Amount: {self.amount}")
        print(f"- Currency Code: {self.currency_code}")
        print(f"- Publication Time: {self.publication_time}")
        print(f"- Profile URL: {self.profile_url}")
        print(f"- Item URL: {self.item_url}")
        print(f"- Highest Discount: {self.highest_discount}\n")