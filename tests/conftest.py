import json
import pytest
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright

DEVICE_PROFILE_FILE = "tests/device_profile.json"

def load_device_profiles():
    with open(DEVICE_PROFILE_FILE, encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def device_profiles():
    return load_device_profiles()  # 이건 dict을 반환

@pytest.fixture(params=["Mobile Chrome", "PC Chrome"], scope="function")
def device_profile(request, device_profiles):
    selected = device_profiles.get(request.param)
    if not selected:
        pytest.skip(f"No matching device found: {request.param}")
    return selected

@pytest.fixture(scope="function")
def page(device_profile):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=device_profile["user_agent"],
            viewport=device_profile["viewport"],
            device_scale_factor=device_profile["device_scale_factor"],
            is_mobile=device_profile["is_mobile"],
            has_touch=device_profile["has_touch"],
            permissions=["microphone"],  # 🎤 마이크 권한 허용
        )
        page = context.new_page()
        yield page
        context.close()
        browser.close()
#run_test.py 에 추가할것 
# @pytest.fixture(scope="session", autouse=True)
# def clear_record_file():
#     path = "data/record.json"
#     if os.path.exists(path):
#         os.remove(path)
#         print("🧹 기존 record.json 초기화 완료")