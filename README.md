# 📈 Market Pulse: KRX 시가총액 대시보드

**Market Pulse**는 한국 주식 시장(KOSPI, KOSDAQ)의 시가총액 상위 종목들을 실시간으로 조회하고 분석할 수 있는 Streamlit 기반 웹 애플리케이션입니다.

네이버 금융 API를 활용하여 최신 주식 데이터를 제공하며, 시장 전반의 등락 현황을 직관적인 게이지 차트와 상세 테이블로 시각화하여 투자자에게 유용한 인사이트를 제공합니다.

## ✨ 주요 기능

*   **📊 실시간 시가총액 순위 조회**
    *   **전체 / KOSPI / KOSDAQ** 시장별로 필터링하여 조회할 수 있습니다.
    *   **Top 50, 100, 200** 등 원하는 개수만큼 데이터를 불러올 수 있습니다.

*   **🌡️ 시장 분위기 시각화 (Market Gauge)**
    *   상위 종목(Top 50, 100, 200) 내에서 **상승(▲), 하락(▼), 보합(▬)** 종목의 비율을 게이지 차트로 한눈에 파악할 수 있습니다.
    *   시장 전체가 불장인지 물장인지 직관적으로 판단하는 데 도움을 줍니다.

*   **📝 상세 투자 지표 제공**
    *   종목별 **현재가, 등락률, 시가총액**뿐만 아니라 **PER, PBR, ROE, ROA, 배당수익률** 등 핵심 투자 지표를 제공합니다.
    *   상승 종목은 붉은색, 하락 종목은 푸른색으로 강조되어 가독성이 뛰어납니다.

*   **🔍 검색 및 사용자 편의성**
    *   **종목명 검색** 기능을 통해 원하는 종목을 빠르게 찾을 수 있습니다.
    *   사용자가 선택한 시장 및 조회 개수 설정이 **쿠키(Cookie)**에 자동 저장되어, 재방문 시에도 설정이 유지됩니다.

## 🛠️ 기술 스택

*   **Language**: Python 3.9+
*   **Framework**: [Streamlit](https://streamlit.io/)
*   **Data Processing**: Pandas
*   **Network**: Requests (Naver Finance API)
*   **Components**: `extra-streamlit-components` (Cookie Manager)

## 🚀 설치 및 실행 방법

### 1. 저장소 복제 (Clone)

```bash
git clone https://github.com/hyuns/krx-marketcap.git
cd krx-marketcap
```

### 2. 패키지 설치

필요한 Python 라이브러리를 설치합니다.

```bash
pip install streamlit pandas requests extra-streamlit-components
```

### 3. 애플리케이션 실행

Streamlit 명령어로 앱을 실행합니다.

```bash
streamlit run app.py
```

실행 후 브라우저에서 `http://localhost:8501` 주소로 접속하여 대시보드를 확인할 수 있습니다.

## 📂 프로젝트 구조

```
krx-marketcap/
├── app.py           # 메인 애플리케이션 코드
└── README.md        # 프로젝트 설명서
```