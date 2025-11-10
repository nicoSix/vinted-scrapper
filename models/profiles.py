from pydantic import BaseModel, HttpUrl, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


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


class PaymentMethod(BaseModel):
    id: int
    code: str
    requires_credit_card: bool
    event_tracking_code: str
    icon: str
    enabled: bool
    translated_name: str
    note: str
    method_change_possible: bool


class BundleDiscountTier(BaseModel):
    minimal_item_count: int
    fraction: str


class BundleDiscount(BaseModel):
    id: int
    user_id: int
    enabled: bool
    minimal_item_count: int
    fraction: str
    discounts: List[BundleDiscountTier]


class Fundraiser(BaseModel):
    id: Optional[int] = None
    active: bool
    percentage: int
    currency: str
    feature_disabled: bool


class EmailVerification(BaseModel):
    valid: bool
    available: bool


class FacebookVerification(BaseModel):
    valid: bool
    verified_at: Optional[str] = None
    available: bool


class GoogleVerification(BaseModel):
    valid: bool
    verified_at: Optional[str] = None
    available: bool


class Verification(BaseModel):
    email: EmailVerification
    facebook: FacebookVerification
    google: GoogleVerification


class VintedProfile(BaseModel):
    id: int
    anon_id: str
    login: str
    birthday: Optional[str] = None
    country_id: int
    city_id: Optional[int] = None
    updated_on: int
    real_name: Optional[str] = None
    email: Optional[EmailStr] = None
    country_code: str
    feedback_count: int
    feedback_reputation: float
    moderator: bool
    business_account_id: Optional[int] = None
    can_bundle: bool
    business_account: Optional[dict] = None
    business: bool
    photo: Optional[Photo] = None
    accepted_pay_in_methods: List[PaymentMethod]
    can_view_profile: bool
    bundle_discount: Optional[BundleDiscount] = None
    last_loged_on_ts: str
    last_loged_on: str
    item_count: int
    total_items_count: int
    followers_count: int
    following_count: int
    following_brands_count: int
    account_status: int
    positive_feedback_count: int
    neutral_feedback_count: int
    negative_feedback_count: int
    is_on_holiday: bool
    expose_location: bool
    city: str
    is_publish_photos_agreed: bool
    third_party_tracking: bool
    locale: str
    iso_locale_code: str
    profile_url: HttpUrl
    share_profile_url: HttpUrl
    is_online: bool
    fundraiser: Fundraiser
    location_description: Optional[str] = None
    localization: str
    is_bpf_price_prominence_applied: bool
    msg_template_count: int
    is_account_banned: bool
    account_ban_date: Optional[str] = None
    is_account_ban_permanent: bool
    action_restriction: Optional[str] = None
    is_favourite: bool
    is_hated: bool
    hates_you: bool
    contacts_permission: Optional[str] = None
    contacts: Optional[dict] = None
    path: str
    is_catalog_moderator: bool
    is_catalog_role_marketing_photos: bool
    hide_feedback: bool
    allow_direct_messaging: bool
    verification: Verification
    avg_response_time: Optional[int] = None
    about: str
    facebook_user_id: Optional[str] = None
    given_item_count: int
    taken_item_count: int
    country_title_local: str
    country_iso_code: str
    country_title: str
    currency: str
    default_address: Optional[dict] = None


class VintedProfileResponse(BaseModel):
    user: VintedProfile
    code: int