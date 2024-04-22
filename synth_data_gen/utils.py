import re
import random


# TODO: some of them are actually lists of elements and lead to overlapping HTML components
FAKER_METATYPES = [
    "aba",
    "address",
    "administrative_unit",
    "am_pm",
    "android_platform_token",
    "ascii_company_email",
    "ascii_email",
    "ascii_free_email",
    "ascii_safe_email",
    "bank_country",
    "basic_phone_number",
    "bban",
    "boolean",
    "bothify",
    "bs",
    "building_number",
    "catch_phrase",
    "century",
    # "chrome",
    "city",
    "city_prefix",
    "city_suffix",
    "color",
    "color_hsl",
    "color_hsv",
    "color_name",
    "color_rgb",
    "color_rgb_float",
    "company",
    "company_email",
    "company_suffix",
    "coordinate",
    "country",
    "country_calling_code",
    "country_code",
    "credit_card_expire",
    "credit_card_full",
    "credit_card_number",
    "credit_card_provider",
    "credit_card_security_code",
    "cryptocurrency",
    "cryptocurrency_code",
    "cryptocurrency_name",
    "currency",
    "currency_code",
    "currency_name",
    "currency_symbol",
    "current_country",
    "current_country_code",
    "date",
    "date_between",
    "date_between_dates",
    "date_object",
    "date_of_birth",
    "date_this_century",
    "date_this_decade",
    "date_this_month",
    "date_this_year",
    "date_time",
    "date_time_ad",
    "date_time_between",
    "date_time_between_dates",
    "date_time_this_century",
    "date_time_this_decade",
    "date_time_this_month",
    "date_time_this_year",
    "day_of_month",
    "day_of_week",
    "dga",
    "domain_name",
    "domain_word",
    "ean",
    "ean13",
    "ean8",
    "ein",
    "email",
    "emoji",
    "file_extension",
    "file_name",
    "file_path",
    # "firefox",
    "first_name",
    "first_name_female",
    "first_name_male",
    "first_name_nonbinary",
    "fixed_width",
    "free_email",
    "free_email_domain",
    "future_date",
    "future_datetime",
    "hex_color",
    "hexify",
    "hostname",
    "http_method",
    "http_status_code",
    "iana_id",
    "iban",
    "image_url",
    # "internet_explorer",
    "invalid_ssn",
    "ios_platform_token",
    "ipv4",
    "ipv4_network_class",
    "ipv4_private",
    "ipv4_public",
    "ipv6",
    "isbn10",
    "isbn13",
    "iso8601",
    "itin",
    "job",
    "language_code",
    "language_name",
    "last_name",
    "last_name_female",
    "last_name_male",
    "last_name_nonbinary",
    "latitude",
    "latlng",
    "lexify",
    "license_plate",
    "linux_platform_token",
    "linux_processor",
    # "local_latlng",
    "locale",
    "localized_ean",
    "localized_ean13",
    "localized_ean8",
    "location_on_land",
    "longitude",
    "mac_address",
    "mac_platform_token",
    "mac_processor",
    "md5",
    "military_apo",
    "military_dpo",
    "military_ship",
    "military_state",
    "mime_type",
    "month",
    "month_name",
    "msisdn",
    "name",
    "name_female",
    "name_male",
    "name_nonbinary",
    "nic_handle",
    "nic_handles",
    "null_boolean",
    "numerify",
    "opera",
    "paragraph",
    # "paragraphs",
    "passport_dates",
    "passport_dob",
    "passport_full",
    "passport_gender",
    "passport_number",
    "passport_owner",
    "password",
    "past_date",
    "past_datetime",
    "phone_number",
    "port_number",
    "postalcode",
    "postalcode_in_state",
    "postalcode_plus4",
    "postcode",
    "postcode_in_state",
    "prefix",
    "prefix_female",
    "prefix_male",
    "prefix_nonbinary",
    "pricetag",
    "pybool",
    "pydecimal",
    "pyfloat",
    "pyint",
    "pystr",
    "pystr_format",
    "pytimezone",
    "random_choices",
    "random_digit",
    "random_digit_above_two",
    "random_digit_not_null",
    "random_digit_not_null_or_empty",
    "random_digit_or_empty",
    "random_element",
    "random_elements",
    "random_int",
    "random_letter",
    # "random_letters",
    "random_lowercase_letter",
    "random_number",
    "random_sample",
    "random_uppercase_letter",
    "randomize_nb_elements",
    "rgb_color",
    "rgb_css_color",
    "ripe_id",
    # "safari",
    "safe_color_name",
    "safe_domain_name",
    "safe_email",
    "safe_hex_color",
    "sbn9",
    "secondary_address",
    "sentence",
    "sentences",
    "sha1",
    "sha256",
    "slug",
    "ssn",
    "state",
    "state_abbr",
    "street_address",
    "street_name",
    "street_suffix",
    "suffix",
    "suffix_female",
    "suffix_male",
    "suffix_nonbinary",
    "swift",
    "swift11",
    "swift8",
    "text",
    # "texts",
    "time",
    "time_delta",
    "time_object",
    "timezone",
    "tld",
    "unix_device",
    "unix_partition",
    "unix_time",
    "upc_a",
    "upc_e",
    "uri",
    "uri_extension",
    "uri_page",
    "uri_path",
    "url",
    # "user_agent",
    "user_name",
    "uuid4",
    "vin",
    "windows_platform_token",
    "word",
    "words",
    "year",
    "zipcode",
    "zipcode_in_state",
    "zipcode_plus4",
]


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def parse_jinja_variables(html_path: str):
    """
    Warning: this is pretty brittle. Make sure all variables are formatted as "{{ variable }}"
    """
    with open(html_path, "r") as file:  # r to open file in READ mode
        html_as_string = file.read()
        return re.findall("\{\{\s(.*?)\s\}\}", html_as_string)


def get_random_metatype():
    return random.choice(FAKER_METATYPES)
