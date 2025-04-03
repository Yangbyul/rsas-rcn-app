import streamlit as st
import json
import re
from openai import OpenAI

# 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = 0
if "responses" not in st.session_state:
    st.session_state.responses = []
if "results" not in st.session_state:  # 🔧 여기 추가!
    st.session_state.results = []

# Streamlit UI 설정
st.set_page_config(page_title="RSAS-RCN 읽기 평가 도구", layout="centered")
st.title("📘 RSAS-RCN 읽기 평가 도구")
st.markdown("""
이 프로그램은 **초등학생의 읽기 수준**을 진단하기 위한 도구입니다.
학생은 각 지문을 읽고 13개의 문항에 답하게 됩니다. 
모든 응답을 마치면 GPT가 자동으로 각 항목을 평가하고 최종 결과를 제공합니다.
""")

# OpenAI API 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 지문 데이터 로드
with open("passages.json", "r", encoding="utf-8") as f:
    passages = json.load(f)

# 평가 항목 정의
rsas_items = [
    "1. 사실적 이해: 글에 나타난 사실을 정확히 이해함",
    "2. 추론적 이해: 단서를 바탕으로 내용을 유추함",
    "3. 비판적 이해: 글의 내용이나 태도를 평가함",
    "4. 글의 유형 파악: 이야기, 설명문 등 글의 형식을 구별함",
    "5. 설명 방식 인식: 예시, 비교 등 글의 설명 방법을 이해함",
    "6. 사실과 의견 구별: 글에서 사실과 의견을 구별함",
    "7. 이해하지 못한 부분 점검: 글을 읽으며 이해하지 못한 부분을 인식함",
    "8. 읽기 전략 활용: 내용을 이해하기 위한 전략 사용",
    "9. 자기 말로 재표현: 내용을 자신의 말로 바꿔 표현함",
    "10. 구조에 따른 요약: 글의 구조에 따라 핵심 내용 요약함",
    "11. 중심 생각 파악: 글 전체의 중심 생각을 파악함",
    "12. 다음 내용 예측: 이후 일어날 일을 예측함",
    "13. 의미 추론: 글의 숨겨진 의미를 유추함"
]

# 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = 0
if "results" not in st.session_state:
    st.session_state.results = []

# 프롬프트 생성

def build_rsas_prompt(passage, combined_answer):
    intro = (
        "당신은 읽기장애 아동을 진단하는 전문 특수교사입니다. 아래 지문과 학생의 응답을 읽고, "
        "**RSAS-RCN의 13개 읽기 이해 평가 항목**에 대해 각각 **1~5점**으로 채점해주세요.\n\n"
        "📌 반드시 지켜야 할 채점 지침\n"
        "1. 항목당 한 줄씩 총 13줄 평가해주세요.\n"
        "2. 형식: `① 항목명: [숫자] / 평가 근거`\n"
        "3. 줄마다 줄바꿈 포함, 점수 명확히 표시해주세요.\n\n"
        "📏 점수 기준 (1~5점):\n"
        "- 5점: 완벽한 이해, 핵심 정보 모두 포함, 표현도 명확\n"
        "- 4점: 대체로 정확하나 세부 정보 일부 누락\n"
        "- 3점: 일부 이해했으나 전체적으로 부족\n"
        "- 2점: 이해 부족, 핵심 누락\n"
        "- 1점: 무관한 응답 또는 전혀 이해하지 못함\n"
    )

    criteria = "\n".join(rsas_items)
    prompt = f"{intro}\n\n[지문]\n{passage}\n\n[학생 응답]\n{combined_answer}\n\n[평가 항목]\n{criteria}"
    return prompt

# GPT 평가 실행

def evaluate_with_gpt(passage, combined_answer):
    prompt = build_rsas_prompt(passage, combined_answer)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# 점수 파싱
def parse_scores(text):
    matches = re.findall(r"\[(\d)\]", text)
    return [int(m) for m in matches] if len(matches) == 13 else None

def interpret_score(avg):
    if avg >= 4.5:
        return "🟢 매우 우수함: 대부분의 항목에서 완벽한 이해를 보였습니다."
    elif avg >= 3.0:
        return "🟡 보통 수준: 전반적으로 내용을 이해하고 있으나 일부 항목에서 세부 내용이 부족하거나 오해가 있습니다. 추가적인 읽기 전략 훈련이 도움이 될 수 있습니다."
    else:
        return "🔴 낮은 수준: 지문 내용에 대한 이해가 부족하며 주요 정보를 파악하는 데 어려움이 있습니다. 구조화된 읽기 지도가 필요합니다."

# 현재 지문
current = passages[st.session_state.step]
st.subheader(current["title"])
st.info(current["text"])

# 사용자 응답 수집
answers = []
for i, q in enumerate(current["questions"]):
    a = st.text_input(q, key=f"q{st.session_state.step}_{i}")
    answers.append(a)

# ✅ 제출 버튼 클릭 시
# 제출 및 평가 처리
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "results" not in st.session_state:
    st.session_state.results = []

if not st.session_state.submitted:
    if st.button("제출"):
        combined = "\n".join([f"{q}\n{a}" for q, a in zip(current["questions"], answers)])
        with st.spinner("GPT가 평가 중입니다..."):
            feedback = evaluate_with_gpt(current["text"], combined)
            scores = parse_scores(feedback)

        # 결과 저장
        st.session_state.results.append({
            "title": current["title"],
            "scores": scores,
            "feedback": feedback
        })
        st.session_state.submitted = True
        st.rerun()

else:
    # 평가 결과 보여주기
    result = st.session_state.results[st.session_state.step]
    st.success(f"📊 {result['title']} 평가 결과")
    for line in result["feedback"].splitlines():
        if line.strip():
            st.markdown(line.strip())

    # 평균 점수 및 수준 진단
    if result["scores"]:
        total = sum(result["scores"])
        avg = total / 13
        st.markdown(f"\n**총점: {total} / 65** &nbsp;&nbsp; 평균: **{avg:.2f} / 5.00**")

        if avg >= 4.5:
            st.success("🟢 읽기 수준: 매우 우수함 — 대부분의 질문에 대해 핵심을 정확히 파악하고 있어요.")
        elif avg >= 3.0:
            st.warning("🟡 읽기 수준: 보통 — 핵심은 이해했지만 세부 내용이나 표현에서 부족한 부분이 있어요.")
        else:
            st.error("🔴 읽기 수준: 낮음 — 전반적으로 이해가 부족하거나 질문 의도를 놓친 경우가 많아요.")

    # 다음 지문으로 넘어가기
    if st.session_state.step < len(passages) - 1:
        if st.button("➡️ 다음 지문으로"):
            st.session_state.step += 1
            st.session_state.submitted = False
            st.rerun()
    else:
        st.balloons()
        st.info("🎉 모든 지문 평가가 완료되었습니다!")

        # ✅ 최종 요약 결과 출력
        all_scores = [score for r in st.session_state.results for score in r["scores"]]
        total = sum(all_scores)
        avg = total / len(all_scores)
        st.markdown(f"### 🧾 최종 총점: {total} / {65 * len(passages)}")
        st.markdown(f"**전체 평균 점수: {avg:.2f} / 5.00**")

        if avg >= 4.5:
            st.success("🟢 전반적 읽기 이해 수준: 매우 우수함\n\n핵심 내용과 세부 정보를 빠짐없이 파악하고 표현도 뛰어납니다.")
        elif avg >= 3.0:
            st.warning("🟡 전반적 읽기 이해 수준: 보통\n\n핵심은 이해했으나 세부 요소 일부 누락 또는 표현이 모호한 경우가 있습니다.")
        else:
            st.error("🔴 전반적 읽기 이해 수준: 낮음\n\n전반적으로 질문 의도나 핵심 내용을 파악하지 못한 경우가 많습니다.")
