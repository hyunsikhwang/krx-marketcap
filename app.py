import streamlit as st
import requests
import pandas as pd

# 1. 페이지 설정
st.set_page_config(
    page_title="Market Pulse",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 스타일 설정 (화이트 모드 & 모던 스타일)
st.markdown("""
    <style>
        /* 전체 배경 및 폰트 설정 */
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        
        /* 데이터프레임 스타일 */
        div[data-testid="stDataFrame"] {
            border: 1px solid #E0E0E0;
        }
        
        /* 불필요한 헤더 숨기기 */
        header {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 95%;
        }
        
        /* 제목 스타일 */
        h1 {
            color: #111111;
            font-weight: 700;
            letter-spacing: -0.5px;
            border-bottom: 2px solid #000;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. 키 매핑 데이터
KEY_MAP = {
    "itemname": "종목명", "itemcode": "종목코드", "sosok": "소속구분", 
    "risefall": "등락구분", "type": "종목타입", "upperLimit": "상한가", 
    "lowerLimit": "하한가", "statusTag": "상태태그", "tradeStopYn": "거래정지여부", 
    "managementDate": "관리종목지정일", "managementReasonCode": "관리종목지정사유", 
    "tradingHaltDate": "거래정지일", "tradingHaltReasonCode": "거래정지사유", 
    "marketAlertType": "시장경보구분", "accQuant": "거래량", "marketStatus": "장운영상태", 
    "nowVal": "현재가", "openVal": "시가", "highVal": "고가", "lowVal": "저가", 
    "askBuy": "매수호가", "askSell": "매도호가", "buyTotal": "매수잔량", 
    "sellTotal": "매도잔량", "changeVal": "전일비", "changeRate": "등락률", 
    "accAmount": "거래대금", "frgnRate": "외국인비율", "frgnHoldCnt": "외국인보유수량", 
    "listedStockCnt": "상장주식수", "marketSum": "시가총액", "eps": "주당순이익(EPS)", 
    "per": "주가수익비율(PER)", "dividendRate": "배당수익률", "high52week": "52주최고가", 
    "low52week": "52주최저가", "quantDiff": "거래량변동", "quantDiffRate": "거래량변동률", 
    "prevQuant": "전일거래량", "propertyTotal": "자산총계", "debtTotal": "부채총계", 
    "sales": "매출액", "salesIncreasingRate": "매출액증가율", 
    "operatingProfit": "영업이익", "operatingProfitIncreasingRate": "영업이익증가율", 
    "netIncome": "당기순이익", "listedDate": "상장일", "dividend": "주당배당금", 
    "continualUpperLimit": "연속상한가일수", "continualUpperLower": "연속상하한가일수", 
    "accumUpper": "누적상한가일수", "accumLower": "누적하한가일수", 
    "roe": "자기자본이익률(ROE)", "roa": "총자산이익률(ROA)", 
    "pbr": "주가순자산비율(PBR)", "reserveRatio": "유보율", "itemInfo": "종목정보", 
    "etfChseErnrtDblSmbl": "ETF추적수익률배수코드", "etfChseErnrtDbl": "ETF추적수익률배수", 
    "refNidxLvgTpCd": "참조지수레버리지타입", "etfType": "ETF구분", 
    "oneMonthEarnRate": "1개월수익률", "threeMonthEarnRate": "3개월수익률", 
    "sixMonthEarnRate": "6개월수익률", "oneYearEarnRate": "1년수익률", 
    "nav": "순자산가치(NAV)", "deviationSign": "괴리율부호", "deviationRate": "괴리율", 
    "totalNetAssets": "순자산총액", "totalFee": "총보수", 
    "issuerNameKo": "발행사명", "inav": "실시간추정순자산가치(iNAV)"
}

# 4. 데이터 로드 및 전처리 함수
@st.cache_data(ttl=60)
def load_stock_data():
    url = (
        "https://stock.naver.com/api/domestic/market/stock/default"
        "?tradeType=KRX&marketType=ALL&orderType=marketSum"
        "&startIdx=0&pageSize=100"
    )
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        raw_data = response.json()
        json_data = []
        
        if isinstance(raw_data, list):
            json_data = raw_data
        elif isinstance(raw_data, dict):
            json_data = raw_data.get('data', [])
        
        df = pd.DataFrame(json_data)
        
        if df.empty:
            return df

        # 1. 컬럼명 한글 변환
        df = df.rename(columns=KEY_MAP)

        # 2. 소속/등락 변환
        df['소속구분'] = df['소속구분'].astype(str).replace({'0': 'KOSPI', '1': 'KOSDAQ'})
        df['등락구분'] = df['등락구분'].astype(str).replace({'2': '상승', '5': '하락', '3': '보합'})

        # 3. 불필요 컬럼 제거
        cols_to_drop = [col for col in df.columns if '관리' in col or '정지' in col or '상태태그' in col]
        df = df.drop(columns=cols_to_drop, errors='ignore')

        # 4. 숫자형 변환 (에러 방지)
        numeric_cols = ['시가총액', '현재가', '주가수익비율(PER)', '배당수익률', '자기자본이익률(ROE)', '주가순자산비율(PBR)', '총자산이익률(ROA)']
        for col in numeric_cols:
            if col in df.columns:
                 df[col] = pd.to_numeric(df[col], errors='coerce')

        # 5. 시가총액 단위 변환 (원 -> 억원)
        if '시가총액' in df.columns:
            df['시가총액'] = df['시가총액'] / 100000000

        # 6. 컬럼명 변경 (단위 추가)
        df = df.rename(columns={
            '시가총액': '시가총액(억원)',
            '현재가': '현재가(원)',
            '주가수익비율(PER)': 'PER',
            '주가순자산비율(PBR)': 'PBR',
            '자기자본이익률(ROE)': 'ROE',
            '총자산이익률(ROA)': 'ROA'
        })

        # 7. 현재가 화살표 표시 (문자열로 변환됨)
        #    참고: 숫자 정렬을 위해 원본을 남겨야 하지만, 화면 표시 우선으로 문자열 처리함.
        def format_price_with_arrow(row):
            price = row.get('현재가(원)', 0)
            status = row.get('등락구분', '')
            
            # NaN 처리
            if pd.isna(price): return "-"
            
            # 기호 결정
            symbol = "-"
            if status == '상승': symbol = "▲"
            elif status == '하락': symbol = "▼"
            
            # 포맷팅 (기호 + 천단위 콤마)
            return f"{symbol} {int(price):,}"

        if '현재가(원)' in df.columns:
            df['현재가(원)'] = df.apply(format_price_with_arrow, axis=1)

        # 8. 컬럼 순서 재배치
        priority_cols = [
            '종목명', '종목코드', '시가총액(억원)', '현재가(원)', 
            'PER', '배당수익률', 'ROE', 'PBR', 'ROA'
        ]
        existing_priority = [c for c in priority_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in existing_priority]
        df = df[existing_priority + other_cols]
        
        return df
        
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return pd.DataFrame()

# 5. 행 배경색 스타일링 함수
def highlight_rows(row):
    status = row.get('등락구분', '')
    
    # 가독성을 위해 아주 연한 파스텔톤 사용
    if status == '상승':
        color = 'background-color: #FFF0F0; color: black;' # 연한 빨강
    elif status == '하락':
        color = 'background-color: #F0F8FF; color: black;' # 연한 파랑 (AliceBlue)
    else:
        color = 'background-color: #FFFFFF; color: black;' # 흰색
        
    return [color] * len(row)

# 6. 메인 함수
def main():
    st.title("KOREA STOCK MARKET SUM")
    
    df_kr = load_stock_data()
    
    if not df_kr.empty:
        # Pandas Styler 적용
        # 1. 포맷팅 설정 (콤마, 소수점 등)
        format_dict = {
            "시가총액(억원)": "{:,.0f}",
            "PER": "{:,.1f}",
            "PBR": "{:,.1f}",
            "배당수익률": "{:,.1f}",
            "ROE": "{:,.1f}",
            "ROA": "{:,.1f}"
        }
        
        # 2. 스타일 적용 (배경색 + 포맷팅)
        # subset에 포맷팅할 컬럼이 실제로 있는지 확인
        available_format_cols = [c for c in format_dict.keys() if c in df_kr.columns]
        
        styled_df = (
            df_kr.style
            .apply(highlight_rows, axis=1)  # 행 배경색
            .format(format_dict, subset=available_format_cols) # 숫자 포맷
        )

        # 3. Streamlit에 표시
        st.dataframe(
            styled_df, 
            use_container_width=True, 
            hide_index=True,
            height=800
        )
        
        cnt = len(df_kr)
        st.markdown(f"""
        <div style="text-align: right; color: #888; font-size: 0.8em; margin-top: 10px;">
            Total Items: {cnt} | Source: Naver Finance
        </div>
        """, unsafe_allow_html=True)
    else:
        st.write("데이터를 불러올 수 없습니다.")

if __name__ == "__main__":
    main()