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
    "quantDiff": "거래량변동",
    "quantDiffRate": "거래량변동률",
    "prevQuant": "전일거래량",
    "propertyTotal": "자산총계",
    "debtTotal": "부채총계",
    "sales": "매출액",
    "salesIncreasingRate": "매출액증가율",
    "operatingProfit": "영업이익",
    "operatingProfitIncreasingRate": "영업이익증가율",
    "netIncome": "당기순이익",
    "listedDate": "상장일",
    "dividend": "주당배당금",
    "continualUpperLimit": "연속상한가일수",
    "continualUpperLower": "연속상하한가일수",
    "accumUpper": "누적상한가일수",
    "accumLower": "누적하한가일수",
    "roe": "자기자본이익률(ROE)",
    "roa": "총자산이익률(ROA)",
    "pbr": "주가순자산비율(PBR)",
    "reserveRatio": "유보율",
    "itemInfo": "종목정보",
    "etfChseErnrtDblSmbl": "ETF추적수익률배수코드",
    "etfChseErnrtDbl": "ETF추적수익률배수",
    "refNidxLvgTpCd": "참조지수레버리지타입",
    "etfType": "ETF구분",
    "oneMonthEarnRate": "1개월수익률",
    "threeMonthEarnRate": "3개월수익률",
    "sixMonthEarnRate": "6개월수익률",
    "oneYearEarnRate": "1년수익률",
    "nav": "순자산가치(NAV)",
    "deviationSign": "괴리율부호",
    "deviationRate": "괴리율",
    "totalNetAssets": "순자산총액",
    "totalFee": "총보수",
    "issuerNameKo": "발행사명",
    "inav": "실시간추정순자산가치(iNAV)"
}

# 4. 데이터 수집 및 처리 함수
@st.cache_data(ttl=60)  # 60초 캐싱으로 성능 최적화
def load_stock_data():
    url = "https://stock.naver.com/api/domestic/market/stock/default?tradeType=KRX&marketType=ALL&orderType=marketSum&startIdx=0&pageSize=100"
    
    # 봇 차단 방지를 위한 User-Agent 설정
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # JSON 파싱 (API 구조상 'data' 키 안에 리스트가 있음)
        json_data = response.json().get('data', [])
        
        # DataFrame 생성
        df = pd.DataFrame(json_data)
        
        # 한글 컬럼명으로 변환
        # 존재하지 않는 키는 무시하고 존재하는 키만 변경
        df = df.rename(columns=KEY_MAP)
        
        return df
        
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# 5. 메인 UI 구성
def main():
    st.title("KOREA STOCK MARKET SUM")
    
    # 데이터 로드
    df_kr = load_stock_data()
    
    if not df_kr.empty:
        # 주요 컬럼만 먼저 보이도록 순서 조정 (원하는 경우)
        # 모든 컬럼을 보여주되, 사용자가 보기 편하게 데이터프레임 표시
        st.dataframe(
            df_kr, 
            use_container_width=True, 
            hide_index=True,
            height=800
        )
        
        # 간단한 데이터 요약 (Footer)
        st.markdown(f"""
        <div style="text-align: right; color: #666; font-size: 0.8em; margin-top: 10px;">
            Total Items: {len(df_kr)} | Source: Naver Finance
        </div>
        """, unsafe_allow_html=True)
    else:
        st.write("데이터가 없습니다.")

if __name__ == "__main__":
    main()