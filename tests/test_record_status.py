import pytest
from playwright.sync_api import Page, expect
from config import Account, URLS
from helpers.record_utils import login, check_logout_popup


def test_check_popup (page:Page , device_profile):
    if device_profile["is_mobile"]:
        pytest.skip("❌ PC 환경에서만 실행됩니다.")
    
    counselor = "홍길동"
    cust_name = "자동화 고객"
    wrong_contact = "01112345678"
    short_contact = "0101234567"
    cust_contact = "01012345678"
    email = "testnaver.com"
    ready = "녹음 준비 완료"
    recoding = "녹음 중"
    pause = "일시정지 중"

    login(page, "record")
    
    check_logout_popup(page)
    
    page.locator('[data-testid="btn_customer_new"]').click()
    page.wait_for_timeout(1000)

    check_logout_popup(page)
    
    page.locator('[data-testid="btn_back"]').click()
    expect(page.locator('[data-testid="btn_customer_exist"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_customer_exist"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_customer_name"]', cust_name)
    page.wait_for_timeout(500)
    # 010 아닌 전화번호
    page.fill('[data-testid="input_contact"]', wrong_contact)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator('[data-testid="toast_contact"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    # 10자리 전화번호 
    page.fill('[data-testid="input_contact"]', short_contact)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator('[data-testid="toast_contact"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    # 이메일 형식 오류
    page.fill('[data-testid="input_contact"]', email)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator('[data-testid="toast_contact"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(500)
    # "녹음 준비 완료" 상태 확인 
    page.fill('[data-testid="input_contact"]', cust_contact)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator(f'[data-testid="txt_status"]')).to_have_text(ready, timeout=3000)
    page.wait_for_timeout(500)    
    # "녹음 중" 상태 확인 
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator(f'[data-testid="txt_status"]')).to_have_text(recoding, timeout=3000)
    page.wait_for_timeout(3000)
    # "녹음 일시정지" 상태 확인 
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator(f'[data-testid="txt_status"]')).to_have_text(pause, timeout=3000)