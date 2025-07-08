import pytest
from playwright.sync_api import Page, expect
from config import Account, URLS
from helpers.record_utils import say_login


def test_check_popup (page:Page , device_profile):
    if device_profile["is_mobile"]:
        pytest.skip("❌ PC 환경에서만 실행됩니다.")

    say_login(page)
    