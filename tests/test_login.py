import pytest
import os
import json
from playwright.sync_api import Page, expect
from config import Account, URLS
from helpers.record_utils import check_logout_popup

file_path = os.path.join(os.path.dirname(__file__), "version_info.json")

def test_login_flow(page: Page, device_profile):
    if not device_profile["is_mobile"]:
        pytest.skip("❌ 모바일 환경에서만 실행됩니다.")
        
    page.goto(URLS["record_login"])
    page.wait_for_timeout(2000)

    page.fill('[data-testid="input_id"]', Account["testid_1"])
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="btn_login"]')).to_be_disabled()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_pw"]', Account["wrongpw"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_login"]')
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="alert_wrong"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)

    page.fill('[data-testid="input_pw"]', Account["testpw"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_login"]')
    page.wait_for_timeout(2000)
    page.wait_for_url(URLS["record_home"])
    page.wait_for_timeout(1000)

    # 테스트 버전 가져오기
    version_span = page.locator("text=메디솔브에이아이(주)").locator("xpath=following-sibling::span")
    version_text = version_span.text_content().strip().splitlines()[-1].strip().strip('"')

    print(f"버전: {version_text}")

    version_data = {
        "version": version_text
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"version": version_text}, f, ensure_ascii=False, indent=2)

    txt_logout = "로그아웃할까요?"
    check_logout_popup(page)
    page.click('[data-testid="btn_logout"]')
    page.wait_for_timeout(1000)
    expect(page.locator(f'[data-testid="txt_logout"]')).to_have_text(txt_logout, timeout=3000)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_yes"]')
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="toast_logout"]')).to_be_visible(timeout=3000)
    page.wait_for_url(URLS["record_login"])