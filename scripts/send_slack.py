import os
import json
import requests
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
RESULT_FILE = "scripts/summary_.json"

# 시간 포맷 (KST)
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
seoul_time = now.strftime("%Y-%m-%d %H:%M:%S")

# 이슈 맵 받아오기 (run_test.py에서 sys.argv[1]로 전달됨)
if len(sys.argv) > 1:
    try:
        issue_map = json.loads(sys.argv[1])
    except Exception:
        issue_map = {}
else:
    issue_map = {}

print(f"💡 issue_map: {issue_map}")

def load_test_results(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_duration(total_seconds):
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes}분 {seconds}초"

def get_total_duration_from_results(results):
    total = 0.0
    for r in results:
        try:
            duration = float(r.get("duration", "0").replace("초", ""))
            total += duration
        except:
            continue
    return format_duration(total)

def get_device_label(device_str):
    if not device_str:
        return "Unknown"
    if "Mobile" in device_str:
        return "Mobile"
    return "PC"

def build_slack_message(test_results, issue_map):
    success_count = 0
    fail_count = 0
    skip_count = 0
    detail_lines = []

    for idx, result in enumerate(test_results, 1):
        status = result.get("status")
        message = result.get("message", "")
        test_file = result.get("file", "")
        test_name = result.get("name", result.get("test_name"))
        device_info = result.get("device", "")
        device_label = get_device_label(device_info)

        jira_id = issue_map.get(test_file) or issue_map.get(test_name)

        if status == "PASS":
            success_count += 1
            detail_lines.append(f"{idx}. ✅[PASS] [{device_label}] {test_name}")
        elif status == "FAIL":
            fail_count += 1
            if jira_id:
                detail_lines.append(f"{idx}. ❌[FAIL] [{device_label}] {test_name}  → JIRA: `{jira_id}`\n   {message}")
            else:
                detail_lines.append(f"{idx}. ❌[FAIL] [{device_label}] {test_name} \n   {message}")
        elif status == "SKIP":
            skip_count += 1
            detail_lines.append(f"{idx}. [SKIP] [{device_label}] {test_name} ")

    total_time = get_total_duration_from_results(test_results)

    slack_message = f":mega: *Say* 자동화 테스트 결과 ({seoul_time})\n"
    slack_message += f"Total: {len(test_results)} | ✅ PASS: {success_count} | ❌ FAIL: {fail_count}\n\n"
    slack_message += "\n".join(detail_lines)

    return slack_message

def send_slack_message(message):
    payload = {
        "text": message
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error sending message to Slack: {response.status_code}, {response.text}")

if __name__ == "__main__":
    test_results = load_test_results(RESULT_FILE)
    slack_message = build_slack_message(test_results, issue_map)
    send_slack_message(slack_message)
    print("✅ 슬랙 알림이 전송되었습니다.")