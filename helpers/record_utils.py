import pytest
import os   
from playwright.sync_api import Page, expect
from config import Account, URLS
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
RECORD_FILE = Path("data/record.json")

# ✅ 로그인 공통 함수
def login(page: Page, service_type: str, account_info: str):
    if service_type == "say":
        login_url = URLS["say_login"]
        home_url = URLS["say_dashboard"]
        user_id = Account[account_info]
        password = Account["testpw"]
    elif service_type == "record":
        login_url = URLS["record_login"]
        home_url = URLS["record_home"]
        user_id = Account[account_info]
        password = Account["testpw"]
    else:
        raise ValueError(f"지원하지 않는 로그인 타입입니다: {service_type}")

    # 로그인 진행
    page.goto(login_url)
    page.wait_for_timeout(3000)
    page.fill('[data-testid="input_id"]', user_id)
    page.wait_for_timeout(500)
    page.fill('[data-testid="input_pw"]', password)
    page.wait_for_timeout(500)
    page.click('[data-testid="btn_login"]')
    page.wait_for_timeout(2000)
    page.wait_for_url(home_url)
    page.wait_for_timeout(1000)


# ✅ 로그아웃 팝업 확인 공통 함수
def check_logout_popup (page: Page):
    txt_logout = "로그아웃할까요?"
    page.locator('[data-testid="btn_logout"]').click()
    expect(page.locator(f'[data-testid="txt_logout"]')).to_have_text(txt_logout, timeout=3000)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_no"]')
    page.wait_for_timeout(1000)
    page.locator('[data-testid="btn_logout"]').click()
    expect(page.locator(f'[data-testid="txt_logout"]')).to_have_text(txt_logout, timeout=3000)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_close"]')
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

def to_mmss(seconds: int) -> str:
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02}:{secs:02}"

def extract_24h_time(text: str) -> str:
    """
    '상담 시작 시간 | 오후 4:25' → '16:25' 형식으로 변환
    """
    try:
        time_part = text.split("|")[-1].strip()  # '오후 4:25'
        # 한글 오전/오후 → 영어 AM/PM 치환
        time_part = time_part.replace("오전", "AM").replace("오후", "PM")
        dt = datetime.strptime(time_part, "%p %I:%M")
        return dt.strftime("%H:%M")
    except Exception as e:
        print(f"⛔ 시간 추출 실패: {e}")
        return ""

# ✅ 상담 녹음 진행 함수 
def run_record(page: Page) -> dict:
    duration_ms = get_random_recording_duration()

    #녹음 시작
    page.click('[data-testid="btn_start"]')
    start_time = datetime.now()
    print(f"🎙️ 녹음 시작: {start_time.strftime('%H:%M')}")

    #전체 녹음 시간 대기
    page.wait_for_timeout(duration_ms)

    #일시정지
    page.click('[data-testid="btn_pause"]')
    print(f"⏸️ 일시정지")
    page.wait_for_timeout(3000)

    #재개
    page.click('[data-testid="btn_start"]')
    pause_duration = random.randint(8, 12)
    print("▶️ 재개")
    page.wait_for_timeout(pause_duration * 1000)

    start_time_text = page.locator('[data-testid="txt_time_start"]').inner_text().strip()
    actual_start_time = extract_24h_time(start_time_text)
    recorded_time_text = page.locator('[data-testid="txt_time_record"]').inner_text().strip()

    print(f"🕒 화면 표기 시작 시간: {start_time_text}")
    print(f"⏱️ 화면 표기 녹음 시간: {recorded_time_text}")
    
    #종료
    page.click('[data-testid="btn_stop"]')
    print("⏹️ 녹음 종료")

    #팝업 처리
    expect(page.locator('[data-testid="txt_stop"]')).to_have_text("상담을 종료할까요?", timeout=3000)
    page.wait_for_timeout(1000)
    page.click('[data-testid="btn_yes"]')
    text = page.locator('[data-testid="txt_complete"]').inner_text(timeout=3000)
    assert text.startswith("상담이 완료되었어요"), f"텍스트가 다릅니다: {text}" 
    page.wait_for_timeout(1000)

    # MM:SS → 초로 변환
    def to_seconds(mmss: str) -> int:
        minutes, seconds = map(int, mmss.strip().split(":"))
        return minutes * 60 + seconds

    duration_sec = duration_ms // 1000
    expected_mmss = to_mmss(duration_sec + pause_duration)

    # 🔁 녹음 시작 시간 비교 (실제 시간 / 표기 시간)
    start_actual_str = start_time.strftime("%H:%M")
    assert start_actual_str == actual_start_time, \
        f"❌ 시작 시간 불일치: 기대값={start_actual_str} / 표기={actual_start_time}"
    print("✅ 시작 시간 일치")

    # 🔁 녹음 시간 비교 (실제 시간 / 표기 시간)
    expected_sec = duration_sec + pause_duration
    actual_sec = to_seconds(recorded_time_text)

    assert abs(actual_sec - expected_sec) <= 1, \
        f"❌ 녹음 시간 불일치: 기대값={expected_sec}s / 실제={actual_sec}s"
    print("✅ 녹음 시간 일치")

    return {
        "start_time": start_time_text,
        "recorded_time": recorded_time_text
    }

# ✅ 녹음 정보 json 저장 
def save_record_to_json(counselor, cust_name, cust_contact, start_time, recorded_time):
    records = []

    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:  # 파일이 비어있지 않으면
                records = json.loads(content)

    new_record = {
        "counselor": counselor,
        "customer_name": cust_name,
        "contact": cust_contact,
        "start_time": start_time,
        "recorded_time": recorded_time
    }

    records.append(new_record)

    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
# ✅ 상담 정보 불러오기
def load_all_records_from_json():
    with open(RECORD_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
        return records 
    
def parse_consult_date(raw_date: str) -> str:
    # raw_date 예: "2025.07.09 / 13:30"
    clean_date = raw_date.split(" / ")[0].replace(".", "")  # '20250709'
    return clean_date[2:]  # '250709'
    
# ✅ 파일 다운로드 확인 
def download_files(page: Page, consult_date_str: str, counselor_name: str, customer_name: str):
    # 상담 내역에서 가져온 상담 일자 → YYMMDD 변환
    yymmdd = parse_consult_date(consult_date_str)

    # ✅ 상담 요약 PDF 다운로드
    with page.expect_download() as summary_info:
        page.click('[data-testid="btn_summary"]')
        page.wait_for_timeout(3000)
    summary_file = summary_info.value
    summary_name = summary_file.suggested_filename
    expected_summary_name = f"상담상세_{counselor_name}_{yymmdd}_{customer_name}.pdf"
    assert summary_name == expected_summary_name, f"❌ 요약 파일명 불일치: {summary_name}"

    # ✅ rawdata PDF/WAV 2개 다운로드
    raw_downloads = []
    with page.expect_download() as d1:
        with page.expect_download() as d2:
            page.click('[data-testid="btn_rawdata"]')
            page.wait_for_timeout(3000)
        raw_downloads.append(d2.value)
    raw_downloads.append(d1.value)

    expected_pdf = f"대화내역_{counselor_name}_{yymmdd}_{customer_name}.pdf"
    expected_wav = f"음성파일_{counselor_name}_{yymmdd}_{customer_name}.wav"
    actual_names = [d.suggested_filename for d in raw_downloads]

    assert expected_pdf in actual_names, f"❌ PDF 파일 없음: {actual_names}"
    assert expected_wav in actual_names, f"❌ WAV 파일 없음: {actual_names}"

    print("✅ 파일 다운로드 및 파일명 확인 완료")

# ✅ 상담 내역 개수 확인
def count_all_history(page) -> int:

    total_rows = 0
    while True:
        # 현재 페이지에서 행 수 카운트
        rows = page.locator("table tbody tr")
        count = rows.count()
        total_rows += count

        # 다음 페이지 버튼 확인
        next_button = page.locator('[data-testid="page_next"]')
        
        if next_button.is_disabled():
            break

        next_button.click()
        page.wait_for_timeout(2000)
    return total_rows

# ✅ 캘린더 어제 날짜 선택
def select_yesterday(page):
    # 어제 날짜 계산
    yesterday = datetime.today() - timedelta(days=1)
    mmdd = yesterday.strftime("%m%d")  # MMDD 형식 → 예: 0708

    # 해당 날짜 버튼 클릭
    page.locator(f'[data-testid="btn_day_{mmdd}"]').click()
    print(f"📅 어제 날짜 선택됨: {mmdd}")
    return mmdd