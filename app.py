import streamlit as st
import requests
import pandas as pd

# 1. 페이지 설정 (Minimal & Modern Layout)
st.set_page_config(
    page_title="Market Pulse",
    page_icon="⚫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 커스텀 CSS 적용 (Black & White, Minimal Style)
st.markdown("""
    <style>
        /* 전체 배경 및 폰트 설정 */
        .stApp {
            background-color: #000000;
            color: #FFFFFF;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        
        /* 테이블 스타일링 */
        div[data-testid="stDataFrame"] {
            border: 1px solid #333333;
        }
        
        /* 헤더 숨기기 및 여백 조정 (Minimalism) */
        header {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 95%;
        }
        
        /* 제목 스타일 */
        h1 {
            color: #FFFFFF;
            font-weight: 200;
            letter-spacing: -1px;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }
        
        /* 하이라이트 색상 무채색화 */
        ::selection {
            background: #333333;
            color: #FFFFFF;
        }
    </style>
""", unsafe_allow_html=True)

# 3. 키 매핑 딕셔너리 (영문 -> 한글)
KEY_MAP = {
    "itemname": "종목명",
    "itemcode": "종목코드",
    "sosok": "소속구분",
    "risefall": "등락구분",
    "type": "종목타입",
    "upperLimit": "상한가",
    "lowerLimit": "하한가",
    "statusTag": "상태태그",
    "tradeStopYn": "거래정지여부",
    "managementDate": "관리종목지정일",
    "managementReasonCode": "관리종목지정사유",
    "tradingHaltDate": "거래정지일",
    "tradingHaltReasonCode": "거래정지사유",
    "marketAlertType": "시장경보구분",
    "accQuant": "거래량",
    "marketStatus": "장운영상태",
    "nowVal": "현재가",
    "openVal": "시가",
    "highVal": "고가",
    "lowVal": "저가",
    "askBuy": "매수호가",
    "askSell": "매도호가",
    "buyTotal": "매수잔량",
    "sellTotal": "매도잔량",
    "changeVal": "전일비",
    "changeRate": "등락률",
    "accAmount": "거래대금",
    "frgnRate": "외국인비율",
    "frgnHoldCnt": "외국인보유수량",
    "listedStockCnt": "상장주식수",
    "marketSum": "시가총액",
    "eps": "주당순이익(EPS)",
    "per": "주가수익비율(PER)",
    "dividendRate": "배당수익률",
    "high52week": "52주최고가",
    "low52week": "52주최저가",
    "