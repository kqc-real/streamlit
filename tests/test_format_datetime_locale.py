from datetime import datetime, timezone

import pandas as pd

from helpers.text import (
    format_decimal_locale,
    FMT_DATE_SHORT,
    FMT_DATETIME,
    format_datetime_locale,
)


def test_scalar_formats_follow_locale_mapping():
    dt = datetime(2024, 1, 2, 15, 4)

    # Naive datetimes are interpreted as UTC then converted to Europe/Berlin (+1h in winter)
    assert format_datetime_locale(dt, fmt=FMT_DATETIME, locale="de") == "02.01.2024 16:04"
    assert format_datetime_locale(dt, fmt=FMT_DATETIME, locale="en") == "2024-01-02 16:04"
    assert format_datetime_locale(dt, fmt=FMT_DATETIME, locale="zh") == "2024-01-02 16:04"


def test_series_formats_and_converts_timezone():
    series = pd.Series([pd.Timestamp("2024-01-02T12:00:00Z")])
    formatted = format_datetime_locale(series, fmt=FMT_DATETIME, locale="de")
    # UTC noon should become 13:00 in Europe/Berlin (winter time)
    assert formatted.iloc[0] == "02.01.2024 13:00"


def test_unknown_locale_falls_back_to_en_format():
    dt = datetime(2024, 1, 2, 15, 4, tzinfo=timezone.utc)
    assert format_datetime_locale(dt, fmt=FMT_DATE_SHORT, locale="xx") == "24-01-02"


def test_format_decimal_locale_separators():
    assert format_decimal_locale(12.34, decimals=1, locale="de") == "12,3"
    assert format_decimal_locale(12.34, decimals=1, locale="en") == "12.3"
