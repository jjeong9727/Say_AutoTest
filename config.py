record_base_url = "https://stg.centurion.ai.kr"
say_base_url = "https://stg.centurion.ai.kr"
URLS = {
    # 모바일 전용 녹음 화면
    "record_login" : f"{record_base_url}/login", # 로그인 화면
    "record_home" : f"{record_base_url}/", # 기존 / 신규 고객 선택화면
    "record_record" : f"{record_base_url}/", # 녹음 진행 화면 
    # Say 
    "say_login" : f"{say_base_url}/", # 로그인 화면 
    "say_dashboard" : f"{say_base_url}/", # 대시보드 화면
    "say_history" : f"{say_base_url}/" # 상담 내역 리스트 
}

Account={
    "testid_1" : "stg@medisolveai.com", #상담사 1 대시보드 진입 가능  
    "testid_2" : "test@medisolveai.com", #상담사2
    "testpw" : "12341234",
    "wrongpw" : "00000000"
}