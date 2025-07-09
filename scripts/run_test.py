import os
import json
import subprocess
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from scripts.send_slack import send_slack_message

TEST_RESULTS_FILE = "test_results.json"
JSON_REPORT_FILE = "scripts/result.json"
SUMMARY_FILE = "scripts/summary.json"

# 실행할 테스트 
tests = [
    "test/login.py",
    "test/record_status.py",
    "test/record.py",
    "test/history.py"
]

# ✅ 기존 결과 파일 제거
for path in [TEST_RESULTS_FILE, JSON_REPORT_FILE, SUMMARY_FILE]:
    if os.path.exists(path):
        os.remove(path)
        print(f"🎩 기존 파일 제거: {path}")

# ✅ 테스트 결과 저장 함수
def save_test_result(test_name, message, status="FAIL", file_name=None, stack_trace="", duration=None, device=None):
    result_data = {
        "test_name": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file": file_name,
        "stack": stack_trace,
        "duration": duration,
        "device": device
    }

    if os.path.exists(TEST_RESULTS_FILE):
        with open(TEST_RESULTS_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = []

    results.append(result_data)

    with open(TEST_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# ✅ 테스트 실행
for test_file in tests:
    print(f"\n테스트 파일: {test_file}")

    test_name = os.path.splitext(os.path.basename(test_file))[0]
    start_time = datetime.now()

    try:
        result = subprocess.run(
            ["pytest", test_file, "--json-report"],
            capture_output=True,
            text=True,
            check=True
        )

        duration = (datetime.now() - start_time).total_seconds()
        print(f"✅ {test_file} 테스트 성공")
        save_test_result(
            test_name=test_name,
            message="테스트 성공",
            status="PASS",
            file_name=test_file,
            duration=f"{duration:.2f}초"
        )

    except subprocess.CalledProcessError as e:
        duration = (datetime.now() - start_time).total_seconds()
        full_output = e.stderr or e.stdout or "출력 없음"
        error_lines = full_output.strip().splitlines()
        parsed_message = next(
            (line for line in reversed(error_lines)
             if any(x in line for x in ["Error", "Exception", "Traceback", "Assertion"])),
            error_lines[-1] if error_lines else "에러 메시지 없음"
        )

        print(f"❌ {test_file} 테스트 실패")
        save_test_result(
            test_name=test_name,
            message=parsed_message.strip(),
            status="FAIL",
            file_name=test_file,
            stack_trace=full_output,
            duration=f"{duration:.2f}초"
        )

print("\n📦 모든 테스트 완료")

# ✅ 결과 요약 및 알림 처리
subprocess.run(["python", "scripts/parse.py"])

# jira_issues_path = "scripts/jira_issues.json"
# if os.path.exists(jira_issues_path) and os.path.getsize(jira_issues_path) > 0:
#     issue_map = process_issues(jira_issues_path)
# else:
issue_map = []

subprocess.run(["python", "scripts/send_slack.py", json.dumps(issue_map, ensure_ascii=False)])
send_slack_message(issue_map)