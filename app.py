import streamlit as st
import requests
import json

# =========================================================
# [설정] API 키 입력
# =========================================================
my_key = "AIzaSyAVpAN04JrFejHsVNpPiX0BA2zIIkT33Pg"

st.set_page_config(page_title="함월고 입시 컨설팅", page_icon="🎓", layout="wide")

# 키 확인
if not my_key or "여기에" in my_key:
    st.error("🚨 코드 8번째 줄에 선생님의 API 키를 넣어주세요!")
    st.stop()

# --- 1. 사용 가능한 모델 자동 찾기 함수 ---
def get_auto_model_name():
    # 구글에게 "네가 가진 모델 목록 좀 보여줘"라고 요청
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={my_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            # 사용 가능한 모델 중에서 'gemini'가 들어간 최신 모델을 찾음
            for m in models:
                if 'gemini-1.5-flash' in m['name']:
                    return m['name'] # 1순위: Flash
            for m in models:
                if 'gemini-1.5-pro' in m['name']:
                    return m['name'] # 2순위: Pro 1.5
            for m in models:
                if 'gemini-pro' in m['name']:
                    return m['name'] # 3순위: 구형 Pro
            
            # 목록은 있는데 위 이름들이 없으면 첫 번째 거라도 가져옴
            if models:
                return models[0]['name']
        
        # 목록을 못 가져왔을 때 (키 문제 등)
        return "ERROR_KEY"
        
    except:
        return "ERROR_NET"

# --- 2. 모델 확정 ---
valid_model = get_auto_model_name()

# 화면 표시
st.title("🎓 함월고등학교 AI 입시 컨설팅 (자동연결 모드)")

# 상태 체크 및 알림
if valid_model == "ERROR_KEY":
    st.error("🚨 구글 서버 접속 실패! API 키가 잘못되었거나, 'Generative Language API'가 활성화되지 않았습니다.")
    st.info("해결책: https://aistudio.google.com/app/apikey 에서 키를 새로 하나 발급받아 보세요.")
    st.stop()
elif valid_model == "ERROR_NET":
    st.error("🚨 인터넷 연결 오류가 발생했습니다.")
    st.stop()
else:
    # 성공적으로 모델을 찾았으면 작게 표시
    st.caption(f"✅ 구글 서버와 성공적으로 연결되었습니다. (사용 모델: {valid_model})")

# --- 3. 시스템 프롬프트 ---
SYSTEM_PROMPT = """
당신은 대한민국 최고의 입시 컨설턴트입니다. 
학생 정보를 받으면 [입시 컨설팅 전문 프롬프트]의 10단계 구조에 따라 
상세한 입시 전략 보고서를 작성하세요.
답변이 끊기지 않도록 핵심 내용을 명확하게 전달하세요.
"""

with st.sidebar:
    st.header("학생 정보 입력")
    grade = st.selectbox("학년", ["고1", "고2", "고3"])
    gpa = st.text_input("내신 등급", placeholder="예: 2.5")
    target = st.text_area("희망 대학/학과", placeholder="예: 연세대 경영학과")
    record = st.text_area("생기부 내용", height=300)
    btn = st.button("분석 시작 ✨", type="primary")

# --- 4. 분석 요청 함수 ---
def call_ai(prompt, model_name):
    # 자동으로 찾은 모델 이름(model_name)을 주소에 넣음
    # model_name은 보통 'models/gemini-1.5-flash' 형태이므로 앞의 'models/'를 처리
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={my_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error ({response.status_code}): {response.text}"

if btn:
    if not record:
        st.warning("생기부 내용을 입력해주세요.")
    else:
        with st.spinner(f"AI가 맞춤형 전략을 분석 중입니다..."):
            try:
                full_prompt = f"{SYSTEM_PROMPT}\n\n[학생정보]\n1.학년: {grade}\n2.내신: {gpa}\n3.희망대학: {target}\n4.생기부:\n{record}"
                result = call_ai(full_prompt, valid_model)
                
                if "Error" in result:
                    st.error(result)
                    st.write("혹시 API 키를 'Google Cloud'가 아니라 'AI Studio'에서 발급받으셨나요?")
                else:
                    st.markdown(result)
                    
            except Exception as e:
                st.error(f"예상치 못한 오류: {e}")


