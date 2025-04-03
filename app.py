import streamlit as st
import openai
import os
import re

# ✅ Streamlit 페이지 설정
st.set_page_config(page_title="RSAS-RCN 읽기 평가 도구")

# ✅ OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ 샘플 지문과 질문
sample = {
    "title": "지문 1: 미나의 발표",
    "text": """오늘 미나는 반 친구들 앞에서 자기가 기른 고양이에 대해 발표했습니다.
고양이는 길에서 구조한 후 돌봐주었고, 지금은 가족처럼 지내고 있습니다.
발표가 끝나자 친구들은 박수를 보냈습니다.""",
    "questions": [
        "1. 사실적 이해: 미나는 무엇에 대해 발표했나요?",
        "2. 추론적 이해: 미나가 고양이를 구조하게 된 이유는 무엇일까요?",
        "3. 비판적 이해: 미나의 발표 태도에 대해 어떻게 생각하나요?",
        "4. 글의 유형 파악: 이 글은 어떤 종류의 글인가요?",
        "5. 설명 방식 인식: 이 글은 어떤 순서로 설명하고 있나요?",
        "6. 사실과 의견 구별: '가족처럼 지낸다'는 말은 사실일까요, 의견일까요?",
        "7. 이해 점검: 이해가 잘 안된 부분이 있다면 무엇인가요?",
        "8. 전략 사용: 어떤 단어나 문장이 글을 이해하는 데 도움이 되었나요?",
        "9. 자기 말로 재표현: 글 내용을 자신의 말로 다시 표현해보세요.",
        "10. 구조 요약: 글의 처음, 중간, 끝 내용을 요약해보세요.",
        "11. 중심 생각 파악: 이 글의 중심 생각은 무엇인가요?",
        "12. 다음 내용 예측: 발표 후 어떤 일이 일어날 것 같나요?",
        "13. 의미 추론: 미나는 어떤 성격의 사람이라고 생각하나요?"
    ]
}

# ✅ RSAS-RCN 항목 정의
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

# ✅ 프롬프트 생성
def build_rsas_prompt(passage, combined_answer):
    intro = (
        "당신은 읽기장애 아동을 평가하는 전문 특수교사입니다. "
        "아래 지문과 학생의 응답을 읽고, 각 읽기 이해 항목(1~13번)에 대해 다음 기준에 따라 1~5점으로 채점해주세요:\n\n"
        "※ 점수 기준:\n"
        "- 5점: 완벽하게 이해하고 정확하게 응답함. 핵심 요소를 모두 포함하고 근거도 적절함\n"
        "- 4점: 대체로 정확하지만 세부 요소 일부가 부족함\n"
        "- 3점: 부분적으로 이해하였으나 핵심에서 일부 벗어남\n"
        "- 2점: 이해 부족으로 부정확하거나 불완전한 응답을 함\n"
        "- 1점: 질문의 요지를 이해하지 못했거나 무관한 응답을 함\n\n"
        "각 항목은 반드시 아래 양식으로 작성하세요:\n"
        "① 사실적 이해: [5] / 미나가 고양이에 대해 발표했다는 사실을 정확히 이해함\n"
    )

    categories = "\n".join(rsas_items)
    prompt = (
        f"{intro}\n\n"
        f"[지문]\n{passage}\n\n"
        f"[학생의 응답]\n{combined_answer}\n\n"
        f"[평가 항목]\n{categories}"
    )
    return prompt

# ✅ 평가 실행 함수
def evaluate_with_rsas_rcn(passage, combined_answer):
    prompt = build_rsas_prompt(passage, combined_answer)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# ✅ 점수 파싱 함수
def parse_scores(text):
    matches = re.findall(r"\[(\d)\]", text)
    return [int(m) for m in matches] if len(matches) == 13 else None

# ✅ Streamlit 앱 UI 시작
st.title("📘 RSAS-RCN 읽기 평가 도구")
st.markdown("초등학생이 입력한 답변을 GPT가 평가해요.")
st.header(f"📖 {sample['title']}")
st.info("📝 아래 지문을 읽고 질문에 답해주세요:")
st.markdown(sample["text"])

responses = []
for i, q in enumerate(sample["questions"]):
    answer = st.text_input(q, key=f"q{i+1}")
    responses.append(answer)

# ✅ 제출 버튼 클릭 시
if st.button("제출"):
    combined = "\n".join([f"{q}\n{a}" for q, a in zip(sample["questions"], responses)])
    with st.spinner("GPT가 평가 중입니다..."):
        feedback = evaluate_with_rsas_rcn(sample["text"], combined)
        scores = parse_scores(feedback)

    # ✅ 줄바꿈 및 결과 출력
    st.success("📊 평가 결과")
    for line in feedback.splitlines():
        if line.strip():
            st.markdown(line.strip())

    # ✅ 점수 및 진단 출력
    if scores:
        total = sum(scores)
        avg = total / 13
        st.markdown(f"\n**총점: {total} / 65**\n\n**평균 점수: {avg:.2f} / 5.00**")

        if avg >= 4.5:
            st.success("🟢 읽기 수준 진단: 매우 우수함\n학생은 다양한 읽기 기술을 잘 활용하고 있으며 고차원적 이해 능력도 우수합니다.")
        elif avg >= 3.0:
            st.warning("🟡 읽기 수준 진단: 보통\n기본적인 이해는 가능하지만 전략적 읽기나 추론적 사고에 추가 훈련이 필요합니다.")
        else:
            st.error("🔴 읽기 수준 진단: 낮음\n중심 생각 파악, 요약, 추론 등에서 어려움을 보이며 교사의 보조적 개입이 필요합니다.")
    else:
        st.error("⚠️ GPT 평가에서 점수를 제대로 추출하지 못했습니다.")
