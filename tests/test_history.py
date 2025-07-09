import pytest
import os
from playwright.sync_api import Page, expect
from config import Account, URLS
from helpers.record_utils import login, load_all_records_from_json, download_files, count_all_history
from datetime import datetime

def normalize_contact(contact: str) -> str:
    # 전화번호일 경우만 normalize 처리
    if contact.isdigit() or contact.replace("-", "").replace(".", "").replace(" ", "").isdigit():
        return contact.replace("-", "").replace(".", "").replace(" ", "")
    return contact.strip()

# 대시보드 확인
def test_check_dashboard(page:Page):
    login(page, "say","testid_1")
    # 상담 내역 개수 확인 
    total = count_all_history(page)

    page.goto(URLS["say_dashboard"])

    total_count = int(page.locator('[data-testid="total_count"]').inner_text().strip())
    morning_count = int(page.locator('[data-testid="morning_count"]').inner_text().strip())
    afternoon_count = int(page.locator('[data-testid="afternoon_count"]').inner_text().strip())
    good_score = int(page.locator('[data-testid="good_score"]').inner_text().strip())
    bad_score = int(page.locator('[data-testid="bad_score"]').inner_text().strip())
    score_rate_text = page.locator('[data-testid="score_rate"]').inner_text().strip().replace('%', '')
    score_rate = int(score_rate_text)

    # 값 비교 
    assert total == total_count, f"❌ 전체 행 수({total})와 total_count({total_count}) 불일치"
    assert morning_count + afternoon_count == total_count, f"❌ 오전/오후 합계({morning_count + afternoon_count}) ≠ total_count({total_count})"
    assert good_score + bad_score == total_count, f"❌ good/bad 합계({good_score + bad_score}) ≠ total_count({total_count})"
    expected_score_rate = round(good_score / total_count * 100)
    assert score_rate == expected_score_rate, f"❌ score_rate({score_rate}%) ≠ 계산값({expected_score_rate}%)"
    print("✅ 상담 건수 확인 완료")

    with page.expect_download() as download_info:
        page.click('[data-testid="btn_summary_download"]')  # 요약 다운로드 버튼 클릭
    download = download_info.value

    # 다운로드 파일 저장
    download_dir = "downloads"  # 경로는 상황에 맞게 조정
    os.makedirs(download_dir, exist_ok=True)
    download_path = os.path.join(download_dir, download.suggested_filename)
    download.save_as(download_path)

    # 파일명 검증: YYMMDD_상담 대시보드.pdf
    today_str = datetime.now().strftime("%y%m%d")
    expected_filename = f"{today_str}_상담 대시보드.pdf"

    assert os.path.basename(download_path) == expected_filename, \
        f"❌ 다운로드된 파일명 불일치: {os.path.basename(download_path)} ≠ {expected_filename}"

    print(f"✅ 다운로드 확인 완료: {expected_filename}")

# 상담 내역 및 상세 확인 
def test_check_history(page: Page):
    records = load_all_records_from_json()

    login(page, "say","testid_1")
    page.goto(URLS["say_history"])
    page.wait_for_timeout(2000)
    
    for record in records:
        customer = record["customer"]
        counselor = record["counselor"]
        raw_contact = record["contact"]
        normalized_contact = normalize_contact(raw_contact)
        raw_date = record["date"]         # 예: "2025.01.01 / 13:00"
        raw_time = record["record_time"]  # 예: "20분 30초"

        # 리스트 노출 값 확인 
        # 고객명 검색
        page.fill('[data-testid="input_search"]', customer)
        page.click('[data-testid="btn_search"]')
        page.wait_for_timeout(2000)

        first_row = page.locator("tbody tr").first
        expect(first_row).to_be_visible(timeout=5000)
        cells = first_row.locator("td")

        # 열 비교 및 점수 추출
        score_text = cells.nth(0).inner_text().strip()
        actual_counselor = cells.nth(1).inner_text().strip()
        actual_customer = cells.nth(2).inner_text().strip()
        actual_contact = normalize_contact(cells.nth(3).inner_text().strip())
        actual_date = cells.nth(4).inner_text().strip()
        actual_time = cells.nth(2).inner_text().strip()

        # 정보가 모두 일치하면 상세 확인 
        if (
            customer == actual_customer
            and counselor == actual_counselor
            and normalized_contact == actual_contact
            and raw_date == actual_date
            and raw_time == actual_time 
        ):
            try:
                # 상세 진입 후 확인 
                expected_score = round(float(score_text), 1)
                last_cell = cells.nth(-1)
                last_cell.click()
                page.wait_for_timeout(500)

                # 상세 진입 버튼 클릭
                page.click('[data-testid="btn_review"]')
                page.wait_for_timeout(2000) 

                # 상세 페이지에서 고객명 및 점수 추출
                detail_customer = page.locator('[data-testid="customer_name"]').inner_text().strip()
                detail_score = page.locator('[data-testid="txt_score"]').inner_text().strip()
                actual_score = round(float(detail_score), 1)

                # 비교
                if detail_customer == customer and actual_score == expected_score:
                    print(f"✅ 상세 페이지 정보 일치: 고객명({detail_customer}), 점수({detail_score})")
                else:
                    print(f"❌ 상세 정보 불일치: 고객명({actual_customer}) vs {customer}, 점수({actual_score}) vs {expected_score}")

                print(f"✅ [{customer}] 상담 내역 생성 확인 : {expected_score}")
            except ValueError:
                print(f"⚠️ [{customer}] 상담 내역 확인 불가")
        else:
            print(f"⚠️ [{customer}] 정보 불일치")

        page.wait_for_timeout(1000)
        download_files(page, raw_date, customer)
