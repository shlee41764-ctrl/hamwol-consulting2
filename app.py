import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# =========================================================
# [설정 1] API 키 입력
# =========================================================
my_key = "AIzaSyCIRagsQj4ULjhdHt4UTujM-gLcy9XeGjk"

# 페이지 설정
st.set_page_config(page_title="함월고 입시 컨설팅", page_icon="🎓", layout="wide")

# 키 확인
if not my_key or "여기에" in my_key:
    st.error("🚨 코드 8번째 줄에 선생님의 API 키를 넣어주세요!")
    st.stop()

# =========================================================
# [설정 2] 모델 변경 (가장 표준적인 'gemini-pro' 사용)
# 최신 버전(1.5) 대신 호환성이 가장 좋은 버전을 씁니다.
# =========================================================
genai.configure(api_key=my_key)

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    model_name='gemini-pro',  # 여기가 핵심입니다! (1.5나 flash 뺌)
    safety_settings=safety_settings
)

# --- 시스템 프롬프트 ---
SYSTEM_PROMPT = """
당신은 대한민국 최고의 입시 컨설턴트입니다. 
학생 정보를 받으면 [입시 컨설팅 전문 프롬프트]의 10단계 구조에 따라 
상세한 입시 전략 보고서를 작성하세요.
답변이 중간에 끊기지 않도록 핵심 내용을 요약하여 명확하게 전달하세요.
"""

# --- 화면 구성 ---
st.title("🎓 함월고등학교 AI 입시 컨설팅 (표준모드)")
st.info("💡 팁: 생기부 내용이 너무 길면 오류가 날 수 있습니다. 주요 활동 위주로 넣어주세요.")

with st.sidebar:
    st.header("학생 정보 입력")
    grade = st.selectbox("학년", ["고1", "고2", "고3"])
    gpa = st.text_input("내신 등급", placeholder="예: 2.5")
    target = st.text_area("희망 대학/학과", placeholder="예: 연세대 경영학과")
    record = st.text_area("생기부 내용 (세특, 행특, 동아리 등)", height=300)
    btn = st.button("분석 시작 ✨", type="primary")

if btn:
    if not record:
        st.warning("생기부 내용을 입력해주세요.")
    else:
        output_placeholder = st.empty()
        full_text = ""
        
        with st.spinner("AI가 분석 중입니다..."):
            try:
                user_msg = f"""
                1. 학년: {grade}
                2. 내신: {gpa}
                3. 희망 대학: {target}
                4. 생기부:
                {record}
                """
                # stream=True 유지
                response = model.generate_content([SYSTEM_PROMPT, user_msg], stream=True)
                
                for chunk in response:
                    full_text += chunk.text
                    output_placeholder.markdown(full_text)
                    
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.write("혹시 'finish_reason' 관련 오류라면 내용이 너무 길어서 AI가 답변을 하다가 멈춘 것입니다.")
