import pytest
from playwright.sync_api import Page, expect
from config import Account, URLS
from helpers.record_utils import say_login, select_customer, check_logout_popup, run_record, save_record_to_file

@pytest.mark.skip_browser("webkit")
# 기존 고객 상담 녹음
def test_record_exist_customer(page:Page, device_profile):
    if not device_profile["is_mobile"]:
        pytest.skip("❌ 모바일 환경에서만 실행됩니다.")

    counselor = "홍길동"
    cust_name = "자동화 고객"
    cust_contact = "01012345678"
    say_login(page)
    page.locator('[data-testid="btn_customer_exist"]').click()
    expect(page.locator(f'[data-testid="txt_counselor_name"]')).to_have_text(counselor, timeout=3000)
    page.wait_for_timeout(500)

    select_customer(page, "existing", cust_name, cust_contact)
    expect(page.locator(f'[data-testid="txt_contact"]')).to_have_text(cust_contact, timeout=3000)
    page.wait_for_timeout(500)

    check_logout_popup(page)

    page.locator('[data-testid="btn_start"]').click()
    page.wait_for_timeout(1000)

    info = run_record(page)

    save_record_to_file(
        counselor=counselor,
        cust_name=cust_name,
        cust_contact=cust_contact,
        start_time=info["start_time"],
        recorded_time=info["recorded_time"]
    )   


# 신규 고객 상담 녹음  
def test_record_exist_customer(page:Page, device_profile):
    if not device_profile["is_mobile"]:
        pytest.skip("❌ 모바일 환경에서만 실행됩니다.")

    counselor = "홍길동"
    cust_name = "자동화 신규고객"
    cust_contact = "newcust@test.com"
    say_login(page)
    
    page.locator('[data-testid="btn_customer_new"]').click()
    expect(page.locator(f'[data-testid="txt_counselor_name"]')).to_have_text(counselor, timeout=3000)
    page.wait_for_timeout(500)

    page.fill('[data-testid="input_customer_name"]', cust_name)
    page.wait_for_timeout(500)
    page.fill('[data-testid="input_contact"]', cust_contact)
    page.wait_for_timeout(500)

    check_logout_popup(page)

    page.locator('[data-testid="btn_start"]').click()
    page.wait_for_timeout(1000)

    info = run_record(page)

    save_record_to_file(
        counselor=counselor,
        cust_name=cust_name,
        cust_contact=cust_contact,
        start_time=info["start_time"],
        recorded_time=info["recorded_time"]
    )   

# 녹음 진행 후 취소 
def test_record_cancel(page:Page, device_profile):
    if not device_profile["is_mobile"]:
        pytest.skip("❌ 모바일 환경에서만 실행됩니다.")
    
    counselor = "홍길동"
    cust_name = "자동화 고객"
    cust_contact = "01012345678"
    notice_cancel = "상담을 취소할까요?"

    say_login(page)
    
    page.locator('[data-testid="btn_customer_new"]').click()
    expect(page.locator(f'[data-testid="txt_counselor_name"]')).to_have_text(counselor, timeout=3000)
    page.wait_for_timeout(500)

    page.fill('[data-testid="input_customer_name"]', cust_name)
    page.wait_for_timeout(500)
    page.fill('[data-testid="input_contact"]', cust_contact)
    page.wait_for_timeout(500)

    page.locator('[data-testid="btn_start"]').click()
    page.wait_for_timeout(1000)

    page.click('[data-testid="start"]')
    page.wait_for_timeout(5000)
    page.click('[data-testid="cancel"]')
    page.wait_for_timeout(1000)
    expect('[data-testid="txt_cancel"]').to_have_text(notice_cancel, timeout=3000)
    page.wait_for_timeout(500)
    page.click('[data-testid="btn_yes"]')
    expect(page.locator('[data-testid="btn_customer_exist"]')).to_be_visible(timeout=3000)
