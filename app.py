import streamlit as st
import requests
import json

# =========================================================
# [설정] API 키 입력
# =========================================================
my_key = "여기에_선생님의_API키를_붙여넣으세요"

# 페이지 설정
st.set_page_config(page_title="함월고 입시 컨설팅", page_icon="🎓", layout="wide")

# 키 확인
if not my_key or "여기에" in my_key:
    st.error("🚨 코드 8번째 줄에 선생님의 API 키를 넣어주세요!")
    st.stop()

# --- 시스템 프롬프트 (PDF 내용) ---
SYSTEM_PROMPT = """
당신은 대한민국 최고의 입시 컨설턴트입니다. 
학생 정보를 받으면 [입시 컨설팅 전문 프롬프트]의 10단계 구조에 따라 
상세한 입시 전략 보고서를 작성하세요.
특히 '6단계 세특 예시'와 '8단계 면접 질문'을 구체적으로 작성하세요.
"""

# --- 화면 구성 ---
st.title("🎓 함월고등학교 AI 입시 컨설팅 (직통모드)")
st.caption("구글 서버와 직접 통신하여 오류 없이 작동합니다.")

with st.sidebar:
    st.header("학생 정보 입력")
    grade = st.selectbox("학년", ["고1", "고2", "고3"])
    gpa = st.text_input("내신 등급", placeholder="예: 2.5")
    target = st.text_area("희망 대학/학과", placeholder="예: 연세대 경영학과")
    record = st.text_area("생기부 내용", height=300)
    btn = st.button("분석 시작 ✨", type="primary")

# --- 구글 직통 전화 함수 (REST API) ---
def call_gemini(prompt):
    # 가장 최신이면서 안정적인 Flash 모델 주소
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={my_key}"
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
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
        return f"Error: {response.text}"

if btn:
    if not record:
        st.warning("생기부 내용을 입력해주세요.")
    else:
        with st.spinner("AI가 분석 중입니다... (직통 연결)"):
            try:
                # 프롬프트 조합
                full_prompt = f"{SYSTEM_PROMPT}\n\n[학생정보]\n1.학년: {grade}\n2.내신: {gpa}\n3.희망대학: {target}\n4.생기부:\n{record}"
                
                # 직통 함수 호출
                result = call_gemini(full_prompt)
                
                # 결과 출력
                if "Error:" in result:
                    st.error(f"오류가 발생했습니다: {result}")
                else:
                    st.markdown(result)
                    
            except Exception as e:
                st.error(f"예상치 못한 오류: {e}")
