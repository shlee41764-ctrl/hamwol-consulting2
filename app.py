import streamlit as st
import google.generativeai as genai

# =========================================================
# [비상 모드] 키 직접 입력 방식
# 따옴표("") 안에 선생님의 API 키를 붙여넣으세요.
# 예시: my_key = "AIzaSyD-12345678..."
# =========================================================
my_key = "AIzaSyCIRagsQj4ULjhdHt4UTujM-gLcy9XeGjk" 

st.set_page_config(page_title="함월고 AI 입시 컨설팅", page_icon="🎓", layout="wide")

# 키가 제대로 들어갔는지 확인
if not my_key or "여기에" in my_key:
    st.error("🚨 선생님! 코드 8번째 줄에 API 키를 아직 안 넣으셨습니다!")
    st.stop()

# 모델 설정
try:
    genai.configure(api_key=my_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
except Exception as e:
    st.error(f"키 설정 중 오류가 났습니다: {e}")
    st.stop()

# --- 시스템 프롬프트 (PDF 내용 요약) ---
SYSTEM_PROMPT = """
당신은 대한민국 최고의 입시 컨설턴트입니다. 
학생 정보를 받으면 [입시 컨설팅 전문 프롬프트]의 10단계 구조에 맞춰 
상세하고 체계적인 입시 전략 보고서를 작성하세요.
"""

# --- 화면 구성 ---
st.title("🎓 함월고등학교 AI 입시 컨설팅")
st.success("✅ 시스템이 정상적으로 연결되었습니다! 이제 분석을 시작할 수 있습니다.")

with st.sidebar:
    st.header("입력란")
    grade = st.selectbox("학년", ["고1", "고2", "고3"])
    target = st.text_input("희망 대학/학과", placeholder="예: 연세대 경영학과")
    record = st.text_area("생기부 내용/활동 요약", height=200)
    btn = st.button("컨설팅 시작하기")

if btn:
    if not record:
        st.warning("생기부 내용을 넣어주세요.")
    else:
        with st.spinner("분석 보고서를 작성 중입니다... (약 30초 소요)"):
            try:
                user_msg = f"학년:{grade}, 희망:{target}, 생기부:{record}"
                response = model.generate_content([SYSTEM_PROMPT, user_msg])
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류 발생: {e}")
