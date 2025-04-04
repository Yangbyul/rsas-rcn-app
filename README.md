# 📘 RSAS-RCN 읽기 평가 도구

이 프로젝트는 **초등학생의 읽기 이해 능력을 진단**하는 데 사용되는  
**RSAS-RCN (Reading Skills Assessment Scale - Reading Comprehension Narrative)** 기반 GPT 평가 앱입니다.  
Streamlit을 활용하여 웹 기반 인터페이스를 제공하며,  
학생의 응답을 OpenAI GPT를 통해 평가하고 피드백을 자동으로 제공합니다.

---

## 📌 목적 및 배경

읽기 이해는 초등 교육에서 핵심적인 기초 학습 능력입니다.  
기존의 평가는 교사의 수작업 기반 채점이었으나,  
이 도구는 GPT-4 모델을 활용하여 자동화된 정성 평가를 시도합니다.

- 평가 모델: RSAS-RCN (13개 읽기 평가 항목)
- 응답 기반 GPT 정성 평가
- 자동 총점 및 읽기 수준 판별 기능 포함

---

## 🛠 기능 소개

- ✅ 초등학생용 지문 입력 (샘플 제공)
- ✅ 13개 문항 기반 학생 응답 수집
- ✅ OpenAI GPT API 기반 자동 평가
- ✅ 항목별 점수 및 피드백 제공
- ✅ 총점에 따른 읽기 수준 판별 (우수 / 보통 / 미흡)

---

## 🚀 설치 및 실행 방법

### 1. 환경 세팅

```bash
pip install -r requirements.txt
```

### 2. OpenAI API 키 설정
.streamlit/secrets.toml 파일에 다음과 같이 입력하세요:
```toml
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxx"
```
(이 파일은 .gitignore에 포함되어 있어 GitHub에 업로드되지 않습니다.)

### 3. 앱 실행

```bash
streamlit run app.py
```
앱 실행 후 브라우저에서 http://localhost:8501 로 접속하면 평가 도구를 사용할 수 있습니다.

---

## 👩‍🔬 연구자 소개
양은별 (Yang, Eunbyul)

- 제주대학교 초등교육학부 초등교육학전공 조교수
- 연구 분야: 멀티모달 학습분석, XR 기반 몰입형 학습설계
- 이메일: e.yang@jejunu.ac.kr

---

## 📄 라이선스
⚠️ 현재는 연구 중인 프로젝트입니다.
연구 종료 후 적절한 오픈 라이선스를 적용할 계획입니다.

---

## 💡 향후 계획
- 다양한 읽기 수준 지문 추가
- 시각화 대시보드 (점수 분포, 난이도 분석 등)
- 영어/다국어 확장 가능성 탐색


