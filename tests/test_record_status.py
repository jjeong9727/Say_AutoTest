import pytest
from playwright.sync_api import Page, expect
from config import Account, URLS
from helpers.record_utils import login, check_logout_popup


def test_check_popup (page:Page , device_profile):
    if not device_profile["is_mobile"]:
        pytest.skip("❌ 모바일 환경에서만 실행됩니다.")
    
    counselor = "QA 계정(권정의)"
    cust_name = "홍길동"
    wrong_contact = "01112345678"
    short_contact = "0101234567"
    cust_contact = "01012345678"
    email = "testnaver.com"
    ready = "녹음 준비 완료"
    recoding = "녹음 중"
    pause = "일시정지 중"
    txt_cancel = "상담을 취소할까요?"
    txt_stop = "상담을 종료할까요?"

    login(page, "record", "testid_1")
    
    check_logout_popup(page)
    
    
    page.locator('[data-testid="btn_customer_exist"]').click()
    expect(page.locator("data-testid=txt_counselor_name")).to_be_visible(timeout=3000)
    text = page.locator('[data-testid="txt_counselor_name"]').inner_text().strip()
    acutual_counselor = text.split('님')[0].strip()
    assert counselor == acutual_counselor, f"상담사명 불일치: {counselor} != {acutual_counselor}"
    page.wait_for_timeout(1000)

    check_logout_popup(page)
    
    page.locator('[data-testid="btn_back"]').click()
    expect(page.locator('[data-testid="btn_customer_new"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_customer_new"]').click()
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_customer_name"]', cust_name)
    page.wait_for_timeout(1000)
    # 010 아닌 전화번호
    page.fill('[data-testid="input_contact"]', wrong_contact)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator('[data-testid="toast_contact"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 10자리 전화번호 
    page.fill('[data-testid="input_contact"]', short_contact)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator('[data-testid="toast_contact"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    # 이메일 형식 오류
    page.fill('[data-testid="input_contact"]', email)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator('[data-testid="toast_contact"]')).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)   
    # "녹음 준비 완료" 상태 확인 
    page.fill('[data-testid="input_contact"]', cust_contact)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator(f'[data-testid="txt_status"]')).to_have_text(ready, timeout=3000)
    page.wait_for_timeout(1000)
    # 종료 버튼 비활성화 확인
    expect(page.locator("data-testid=btn_stop")).to_be_disabled(timeout=3000)
    page.wait_for_timeout(1000)
    # # 녹음 준비 상태 > 취소 확인 팝업 닫기 버튼 확인
    page.locator('[data-testid="btn_cancel"]').click()
    expect(page.locator("data-testid=btn_close")).to_be_visible(timeout=3000)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_close"]').click()
    expect(page.locator(f'[data-testid="txt_status"]')).to_have_text(ready, timeout=3000)
    page.wait_for_timeout(1000)
    # "녹음 중" 상태 확인 
    page.locator('[data-testid="btn_start"]').click()
    expect(page.locator(f'[data-testid="txt_status"]')).to_have_text(recoding, timeout=3000)
    page.wait_for_timeout(3000)
    # 녹음 중 상태 > 취소 확인 팝업 닫기 버튼 확인
    page.locator("data-testid=btn_cancel").click()
    # expect(page.locator("data-testid=txt_cancel")).to_have_text(txt_cancel, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator("data-testid=btn_close").click()
    expect(page.locator(f'[data-testid="txt_status"]')).to_have_text(recoding, timeout=3000)
    page.wait_for_timeout(2000)
    
    # "녹음 일시정지" 상태 확인 
    page.locator('[data-testid="btn_pause"]').click()
    expect(page.locator(f'[data-testid="txt_status"]')).to_have_text(pause, timeout=3000)
    page.wait_for_timeout(2000)
    # 종료 확인 팝업 닫기 버튼 확인
    page.locator("data-testid=btn_stop").click()
    expect(page.locator("data-testid=txt_stop")).to_have_text(txt_stop, timeout=3000)
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_close"]').click()
    expect(page.locator(f'[data-testid="txt_status"]')).to_have_text(pause, timeout=3000)
    page.wait_for_timeout(1000)

