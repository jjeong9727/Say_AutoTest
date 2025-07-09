import pytest
import os
from playwright.sync_api import Page, expect
from config import Account, URLS
from helpers.record_utils import login, count_all_history, select_yesterday
from datetime import datetime

# 상담 내역 검색 기능 확인
def test_check_dashboard(page: Page):
    page.goto(URLS["say_history"])
    page.wait_for_timeout(2000)

    total = count_all_history(page)
    print(f"📊 총 개수: {total}")

    score_values = ["0.0", "1.0", "2.0", "3.0", "4.0"]

    for score_text in score_values:
        print(f"\n🎯 드롭다운 선택: {score_text}")

        # 드롭다운 열기 및 점수 선택
        page.locator('[data-testid="drop_score_trigger"]').click()
        page.wait_for_timeout(1000)
        page.locator('[data-testid="drop_score_item"]', has_text=score_text).click()
        page.wait_for_timeout(1000)

        score = count_all_history(page)
        print(f"   → 검색 결과: {score}")

        if total != score:
            print(f"✅ 비교 대상 발견: 전체 개수({total}) ≠ 검색결과 개수({score})")

            # 초기화
            page.locator('[data-testid="btn_reset"]').click()
            page.wait_for_timeout(1000)

            reset = count_all_history(page)
            assert total == reset, f"❌ 초기화 후 total({total})과 reset({reset})이 다릅니다"

            print("✅ 초기화 후 total 일치 확인 완료")
            break  # 더 이상 점수 체크 안 함
        else:
            print(f"⏩ total({total}) == score({score}) → 다음 점수로 넘어감")
            # 초기화 버튼 눌러서 다음 점수 테스트 준비
            page.locator('[data-testid="btn_reset"]').click()
            page.wait_for_timeout(1000)

    else:
        # for 루프가 끝났는데도 모든 score가 total과 같다면 테스트 실패 처리
        assert False, "❌ 모든 점수에서 검색결과가 total과 같아 비교 대상이 없습니다"

def get_change_tag(today, yesterday):
    if yesterday == 0:
        return "변동 없음"
    elif today > yesterday:
        return "증가"
    elif today < yesterday:
        return "감소"
    else:
        return "변동 없음"
    
# 대시보드 어제 값과 비교
def test_compare_dashboard(page:Page):
    login(page, "say", "testid_1")

    page.goto(URLS["say_dashboard"])


    # 어제 데이터랑 오늘 데이터 비교
    page.locator('[data-testid="input_date"]').click()
    page.wait_for_timeout(1000)
    mmdd = select_yesterday(page)
    txt_nodata = "상담 대시보드가 없어요"
    txt_title = "상담 전체 요약"
    # 내역이 없으면 0 리턴 
    if page.locator('[data-testid="txt_nodata"]').is_visible():
        expect(page.locator(f'[data-testid="txt_nodata"]')).to_have_text(txt_nodata, timeout=3000)
        print(f"⏩ 어제({mmdd}) 내역 없음")
        yesterday_count = int(0)
        yesterday_rate = int(0)
    else:
        # 내역이 있는 경우 → 비교 진행
        assert page.locator('[data-testid="txt_title"]').is_visible(), "❌ 내역이 있어야 할 위치에 txt_title이 없음"
        expect(page.locator(f'[data-testid="txt_nodata"]')).to_have_text(txt_title, timeout=3000)
        yesterday_count = int(page.locator('[data-testid="total_count"]').inner_text().strip())
        yesterday_rate = int(page.locator('[data-testid="score_rate"]').inner_text().strip())

    page.locator('[data-testid="btn_reset"]').click()
    
    today_count = int(page.locator('[data-testid="total_count"]').inner_text().strip())
    today_rate = int(page.locator('[data-testid="score_rate"]').inner_text().strip())

    tag_count = get_change_tag(today_count, yesterday_count)
    tag_rate = get_change_tag(today_rate, yesterday_rate)

    print(f"📊 상담 수: {yesterday_count} → {today_count} ({tag_count})")
    print(f"📈 점수율: {yesterday_rate}% → {today_rate}% ({tag_rate})")

    expect(page.locator(f'[data-testid="tag_count"]')).to_have_text(tag_count, timeout=3000)
    expect(page.locator(f'[data-testid="tag_rate"]')).to_have_text(tag_rate, timeout=3000)