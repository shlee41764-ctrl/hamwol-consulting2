import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# =========================================================
# [설정 1] API 키 입력
# 따옴표("") 안에 선생님의 API 키를 붙여넣으세요.
# =========================================================
my_key = "AIzaSyCIRagsQj4ULjhdHt4UTujM-gLcy9XeGjk"

# 페이지 설정
st.set_page_config(page_title="함월고 AI 입시 컨설팅", page_icon="🎓", layout="wide")

# 키 확인
if not my_key or "여기에" in my_key:
    st.error("🚨 코드 8번째 줄에 선생님의 API 키를 넣어주세요!")
    st.stop()

# =========================================================
# [설정 2] 안전 필터 해제 (생기부 분석 필수 설정)
# =========================================================
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# 모델 설정 (이름을 표준 버전인 'gemini-1.5-pro'로 변경)
genai.configure(api_key=my_key)
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',  # 여기가 수정되었습니다!
    safety_settings=safety_settings
)

# --- 시스템 프롬프트 (PDF 내용) ---
SYSTEM_PROMPT = """
당신은 입시 전문 컨설턴트입니다. 
학생 정보를 받으면 [입시 컨설팅 전문 프롬프트]의 10단계 구조에 맞춰 
상세하고 체계적인 입시 전략 보고서를 작성하세요.
특히 '6단계 세특 예시'와 '8단계 면접 질문'을 구체적으로 작성하세요.
"""

# --- 화면 구성 ---
st.title("🎓 함월고등학교 AI 입시 컨설팅")
st.info("💡 팁: 분석 내용이 많아서 결과가 나올 때까지 약 30초~1분 정도 걸릴 수 있습니다.")

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
        # 스트리밍 출력 (타임아웃 방지)
        output_placeholder = st.empty()
        full_text = ""
        
        with st.spinner("함월고 AI가 생기부를 분석하고 있습니다..."):
            try:
                user_msg = f"""
                1. 학년: {grade}
                2. 내신: {gpa}
                3. 희망 대학/학과: {target}
                4. 생기부 내용:
                {record}
                """
                # stream=True로 설정하여 한 줄씩 받아옵니다.
                response = model.generate_content([SYSTEM_PROMPT, user_msg], stream=True)
                
                for chunk in response:
                    full_text += chunk.text
                    output_placeholder.markdown(full_text)
                    
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                st.write("혹시 '400' 에러라면 생기부 내용이 너무 길어서일 수 있습니다. 내용을 조금 줄여서 시도해보세요.")
