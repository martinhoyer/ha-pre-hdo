"""Shared test fixtures for PRE Distribuce tests."""

import pytest

SAMPLE_HDO_HTML = (
    '<div class="hdo-bar">'
    '<div class="blue-text pull-left">pátek 13.02.</div>'
    '<div class="overflow-bar"></div>'
    '<span style="left: 0.00%;" class="hdovt"></span>'
    '<span style="left: 0.00%;" class="span-overflow" title="00:00 - 01:00"></span>'
    '<span style="left: 4.17%;" class="hdont"></span>'
    '<span style="left: 4.17%;" class="span-overflow" title="01:00 - 06:00"></span>'
    '<span style="left: 25.00%;" class="hdovt"></span>'
    '<span style="left: 25.00%;" class="span-overflow" title="06:00 - 13:00"></span>'
    '<span style="left: 54.17%;" class="hdont"></span>'
    '<span style="left: 54.17%;" class="span-overflow" title="13:00 - 16:00"></span>'
    '<span style="left: 66.67%;" class="hdovt"></span>'
    '<span style="left: 66.67%;" class="span-overflow" title="16:00 - 00:00"></span>'
    "</div>"
)

SAMPLE_HDO_JSON = {"html": SAMPLE_HDO_HTML}


@pytest.fixture
def sample_hdo_html():
    return SAMPLE_HDO_HTML


@pytest.fixture
def sample_hdo_json():
    return SAMPLE_HDO_JSON


SAMPLE_MULTI_DAY_HTML = (
    '<div class="hdo-bar">'
    '<div class="blue-text pull-left">pondělí 09.03. - pátek 13.03.</div>'
    '<div class="overflow-bar"></div>'
    '<span style="left: 0.00%;" class="hdovt"></span>'
    '<span style="left: 0.00%;" class="span-overflow" title="00:00 - 01:00"></span>'
    '<span style="left: 4.17%;" class="hdont"></span>'
    '<span style="left: 4.17%;" class="span-overflow" title="01:00 - 06:00"></span>'
    '<span style="left: 25.00%;" class="hdovt"></span>'
    '<span style="left: 25.00%;" class="span-overflow" title="06:00 - 13:00"></span>'
    '<span style="left: 54.17%;" class="hdont"></span>'
    '<span style="left: 54.17%;" class="span-overflow" title="13:00 - 16:00"></span>'
    '<span style="left: 66.67%;" class="hdovt"></span>'
    '<span style="left: 66.67%;" class="span-overflow" title="16:00 - 00:00"></span>'
    "</div>"
    '<div class="hdo-bar">'
    '<div class="blue-text pull-left">sobota 14.03.</div>'
    '<div class="overflow-bar"></div>'
    '<span style="left: 0.00%;" class="hdovt"></span>'
    '<span style="left: 0.00%;" class="span-overflow" title="00:00 - 03:00"></span>'
    '<span style="left: 12.50%;" class="hdont"></span>'
    '<span style="left: 12.50%;" class="span-overflow" title="03:00 - 06:00"></span>'
    '<span style="left: 25.00%;" class="hdovt"></span>'
    '<span style="left: 25.00%;" class="span-overflow" title="06:00 - 13:00"></span>'
    '<span style="left: 54.17%;" class="hdont"></span>'
    '<span style="left: 54.17%;" class="span-overflow" title="13:00 - 18:00"></span>'
    '<span style="left: 75.00%;" class="hdovt"></span>'
    '<span style="left: 75.00%;" class="span-overflow" title="18:00 - 00:00"></span>'
    "</div>"
)

SAMPLE_MULTI_DAY_JSON = {"html": SAMPLE_MULTI_DAY_HTML}


@pytest.fixture
def sample_multi_day_json():
    return SAMPLE_MULTI_DAY_JSON
