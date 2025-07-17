import pytest
from playwright.sync_api import Page, expect
from config import Account, URLS
from helpers.record_utils import login, select_customer, check_logout_popup, run_record, save_record_to_json

@pytest.mark.skip_browser("webkit")
# 기존 고객 상담 녹음
def test_record_exist_customer(page:Page, device_profile):
    if not device_profile["is_mobile"]:
        pytest.skip("❌ 모바일 환경에서만 실행됩니다.")

    counselor = "QA 계정(권정의)"
    cust_name = "홍길동"
    cust_contact = "010-1234-5678"
    login(page, "record", "testid_1") # 계정 1 로그인 
    page.locator('[data-testid="btn_customer_exist"]').click()

    expect(page.locator("data-testid=txt_counselor_name")).to_be_visible(timeout=3000)
    text = page.locator('[data-testid="txt_counselor_name"]').inner_text().strip()
    acutual_counselor = text.split('님')[0].strip()
    assert counselor == acutual_counselor, f"상담사명 불일치: {counselor} != {acutual_counselor}"
    page.wait_for_timeout(1000)

    select_customer(page, "existing", cust_name, cust_contact)
    expect(page.locator(f'[data-testid="txt_contact"]')).to_have_value(cust_contact, timeout=3000)
    page.wait_for_timeout(1000)

    check_logout_popup(page)

    page.locator('[data-testid="btn_start"]').click()
    page.wait_for_timeout(1000)

    info = run_record(page)

    save_record_to_json(
        counselor=counselor,
        cust_name=cust_name,
        cust_contact=cust_contact,
        start_time=info["start_time"],
        recorded_time=info["recorded_time"]
    )   
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_new_record"]').click()
    expect(page.locator('[data-testid="btn_customer_exist"]')).to_be_visible(timeout=3000)


# 신규 고객 상담 녹음  
def test_record_new_customer(page:Page, device_profile):
    if not device_profile["is_mobile"]:
        pytest.skip("❌ 모바일 환경에서만 실행됩니다.")

    counselor = "QA 계정(법인폰)"
    cust_name = "홍길동"
    cust_contact = "newcust@test.com"
    login(page, "record", "testid_2") # 계정 2 로그인 

    
    page.locator('[data-testid="btn_customer_new"]').click()
    expect(page.locator("data-testid=txt_counselor_name")).to_be_visible(timeout=3000)
    text = page.locator('[data-testid="txt_counselor_name"]').inner_text().strip()
    acutual_counselor = text.split('님')[0].strip()
    assert counselor == acutual_counselor, f"상담사명 불일치: {counselor} != {acutual_counselor}"
    page.wait_for_timeout(1000)

    page.fill('[data-testid="input_customer_name"]', cust_name)
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_contact"]', cust_contact)
    page.wait_for_timeout(1000)

    check_logout_popup(page)

    page.locator('[data-testid="btn_start"]').click()
    page.wait_for_timeout(1000)

    info = run_record(page)

    save_record_to_json(
        counselor=counselor,
        cust_name=cust_name,
        cust_contact=cust_contact,
        start_time=info["start_time"],
        recorded_time=info["recorded_time"]
    )   
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_new_record"]').click()
    expect(page.locator('[data-testid="btn_customer_exist"]')).to_be_visible(timeout=3000)
    
# 녹음 진행 후 취소 
def test_record_cancel(page:Page, device_profile):
    if not device_profile["is_mobile"]:
        pytest.skip("❌ 모바일 환경에서만 실행됩니다.")
    
    counselor = "QA 계정(권정의)"
    cust_name = "홍길동"
    cust_contact = "01012345678"
    notice_cancel = "상담을 취소할까요?"

    login(page, "record", "testid_1")
    
    page.locator('[data-testid="btn_customer_new"]').click()
    expect(page.locator("data-testid=txt_counselor_name")).to_be_visible(timeout=3000)
    text = page.locator('[data-testid="txt_counselor_name"]').inner_text().strip()
    acutual_counselor = text.split('님')[0].strip()
    assert counselor == acutual_counselor, f"상담사명 불일치: {counselor} != {acutual_counselor}"
    page.wait_for_timeout(1000)

    page.fill('[data-testid="input_customer_name"]', cust_name)
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_contact"]', cust_contact)
    page.wait_for_timeout(1000)

    page.locator('[data-testid="btn_start"]').click()
    page.wait_for_timeout(1000)

    page.click('[data-testid="btn_start"]')
    page.wait_for_timeout(5000)
    page.click('[data-testid="btn_cancel"]')
    page.wait_for_timeout(1000)
    expect(page.locator('[data-testid="txt_cancel"]')).to_have_text(notice_cancel, timeout=3000)
    page.wait_for_timeout(1000)
    
    page.click('[data-testid="btn_yes"]')
    expect(page.locator('[data-testid="txt_time_record"]')).to_have_text("00:00", timeout=3000)
    page.wait_for_timeout(1000)

    page.locator('[data-testid="btn_start"]').click()
    page.wait_for_timeout(3000)
    page.click('[data-testid="btn_cancel"]')
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_no"]')
    expect(page.locator('[data-testid="btn_customer_exist"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    
