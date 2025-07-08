import pytest
from playwright.sync_api import Page, expect
from config import Account, URLS
import random
import json
from pathlib import Path
from datetime import datetime
RECORD_FILE = Path("data/record.json")

# ✅ 로그인 공통 함수
def say_login(page:Page):
    page.goto(URLS["say_login"])
    page.wait_for_timeout(5000)
    page.fill('[data-testid="input_id"]', Account["testid_1"])
    page.wait_for_timeout(1000)
    page.fill('[data-testid="input_pw"]', Account["testpw"])
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_login"]')
    page.wait_for_timeout(2000)
    page.wait_for_url(URLS["say_home"])
    page.wait_for_timeout(1000)

# ✅ 로그아웃 팝업 확인 공통 함수
def check_logout_popup (page: Page):
    txt_logout = "로그아웃할까요?"
    page.locator('[data-testid="btn_logout"]').click()
    expect(page.locator(f'[data-testid="txt_logout"]')).to_have_text(txt_logout, timeout=3000)
    page.wait_for_timeout(500)
    page.locator('[data-testid="btn_logout"]').click()
    page.wait_for_timeout(500)
    page.click('[data-testid="btn_no"]')
    page.wait_for_timeout(1000)

# ✅ 고객 선택 공통 함수 
def select_customer(
    page: Page,
    customer_type: str,  # "existing" or "new"
    name: str,
    contact: str = ""
):
    if customer_type == "existing":
        #드롭다운 열기
        page.click('[data-testid="drop_customer_trigger"]')
        page.wait_for_timeout(1000)
        page.fill('[data-testid="drop_customer_search"]', name)
        page.wait_for_timeout(1000)

        #드롭다운 리스트 중에서 고객 선택
        page.locator('[data-testid="drop_customer_item"]', has_text=name).first.click()
        page.wait_for_timeout(1000)

    elif customer_type == "new":
        #이름 입력
        page.fill('[data-testid="input_customer_name"]', name)
        page.wait_for_timeout(1000)

        # 전화번호 또는 이메일 입력
        page.fill('[data-testid="input_contact"]', contact)
        page.wait_for_timeout(1000)
        

    else:
        raise ValueError(f"잘못된 고객 유형: {customer_type}")

# ✅ 상담 시간 (1분 미만 | 1분 | 1분 이상) 선택 함수
def get_random_recording_duration() -> int:
    mode = random.choice(["short", "exact", "long"])
    if mode == "short":
        duration = random.randint(10, 59)
    elif mode == "exact":
        duration = 60
    else:
        duration = random.randint(61, 100)
    print(f"🎙️ 녹음 시간 선택됨: {duration}초")
    return duration * 1000

# ✅ 상담 녹음 진행 함수 
def run_record(page: Page) -> dict:
    duration_sec = get_random_recording_duration() // 1000  # 초 단위

    #녹음 시작
    page.click('[data-testid="start"]')
    print("▶️ 녹음 시작")

    #시작 시각 저장
    start_time = page.locator('[data-testid="txt_time_start"]').inner_text()
    print(f"🕒 시작 시각: {start_time}")

    #전체 녹음 시간 대기
    page.wait_for_timeout(duration_sec * 1000)
    print("⏳ 전체 녹음 시간 경과")

    #일시정지
    page.click('[data-testid="pause"]')
    pause_duration = random.randint(8, 12)
    print(f"⏸️ 일시정지: {pause_duration}초")
    page.wait_for_timeout(pause_duration * 1000)

    #재개
    page.click('[data-testid="start"]')
    print("▶️ 재개")

    #종료
    page.click('[data-testid="stop"]')
    print("⏹️ 녹음 종료")

    #팝업 처리
    expect(page.locator('[data-testid="txt_stop"]')).to_have_text("상담을 종료할까요?", timeout=3000)
    page.wait_for_timeout(500)
    page.click('[data-testid="btn_yes"]')
    expect(page.locator('[data-testid="txt_stop"]')).to_have_text("상담이 완료되었어요", timeout=3000)
    page.wait_for_timeout(500)

    #녹음된 시간 추출
    recorded_time = page.locator('[data-testid="txt_time_record"]').inner_text()
    print(f"⏱️ 녹음 시간: {recorded_time}")

    #MM:SS → 초로 변환
    def to_seconds(mmss: str) -> int:
        minutes, seconds = map(int, mmss.strip().split(":"))
        return minutes * 60 + seconds

    recorded_sec = to_seconds(recorded_time)

    #비교
    if abs(recorded_sec - duration_sec) > 1:
        raise AssertionError(f"❌ 녹음 시간이 다릅니다. 기대값: {duration_sec}s / 실제값: {recorded_sec}s")

    print("✅ 녹음 시간 일치")

    return {
        "start_time": start_time,
        "recorded_time": recorded_time
    }

# ✅ 녹음 정보 json 저장 
def save_record_to_file(
    counselor: str,
    cust_name: str,
    cust_contact: str,
    start_time: str,         # HH:MM 형식
    recorded_time: str       # MM:SS 형식
):
    today = datetime.now().strftime("%Y.%m.%d")
    start_datetime = f"{today} / {start_time}"

    # MM:SS → MM분 SS초 형식 변환
    mm, ss = map(int, recorded_time.strip().split(":"))
    record_time_formatted = f"{mm:02d}분 {ss:02d}초"

    record_data = {
        "counselor": counselor,
        "cust_name": cust_name,
        "cust_contact": cust_contact,
        "start_datetime": start_datetime,
        "record_time": record_time_formatted
    }

    # 기존 파일 불러오기 또는 새 리스트 생성
    if RECORD_FILE.exists():
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    else:
        records = []

    records.append(record_data)

    # 저장
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print("✅ 녹음 정보 저장 완료:", record_data)