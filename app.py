import streamlit as st
import requests
import pandas as pd
import datetime
import extra_streamlit_components as stx
import base64
import os

# 1. 페이지 설정
st.set_page_config(
    page_title="Market Pulse",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 스타일 및 디자인 시스템 (Value Horizon 기준)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* 깔끔한 배경 및 폰트 */
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
        font-family: 'Inter', sans-serif;
    }

    /* 컨테이너 패딩 조정 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* 기존 헤더 및 푸터 숨기기 */
    [data-testid="stHeader"], footer {
        display: none !important;
    }

    /* Hero Section - Value Horizon Style */
    .hero-container {
        padding: 2rem 0;
        text-align: center;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #111111;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 1rem;
        font-weight: 400;
        color: #888888;
        letter-spacing: 0.2px;
    }

    /* Search & Filter Container */
    .filter-container {
        background: #f9f9f9;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid #eaeaea;
    }

    /* Gauge Section Design */
    .gauge-wrapper {
        margin-bottom: 25px;
        padding: 20px;
        border: 1px solid #eaeaea;
        border-radius: 16px;
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    .gauge-item {
        margin-bottom: 18px;
    }
    
    .gauge-item:last-child {
        margin-bottom: 0;
    }

    .gauge-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #333;
    }

    .gauge-bar-container {
        display: flex;
        width: 100%;
        height: 10px;
        background-color: #f0f0f0;
        border-radius: 5px;
        overflow: hidden;
    }

    .gauge-bar-up { background-color: #ff4b4b; transition: width 0.5s ease; }
    .gauge-bar-steady { background-color: #d1d1d1; transition: width 0.5s ease; }
    .gauge-bar-down { background-color: #007aff; transition: width 0.5s ease; }

    /* 데이터프레임 테두리 제거 및 그림자 */
    div[data-testid="stDataFrame"] {
        border: none !important;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* 셀렉트박스 등 입력 요소 커스텀 */
    div[data-baseweb="select"], div[data-baseweb="input"] {
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 키 매핑 및 데이터 로직 (원래 기능 유지)
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

@st.cache_data(ttl=60)
def load_stock_data(market_type="ALL", page_size=10):
    url = (
        "https://stock.naver.com/api/domestic/market/stock/default"
        f"?tradeType=KRX&marketType={market_type}&orderType=marketSum"
        f"&startIdx=0&pageSize={page_size}"
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
        json_data = raw_data if isinstance(raw_data, list) else raw_data.get('data', [])
        
        df = pd.DataFrame(json_data)
        if df.empty: return df

        df['순위'] = df.index + 1
        df = df.rename(columns=KEY_MAP)
        df['소속구분'] = df['소속구분'].astype(str).replace({'0': 'KOSPI', '1': 'KOSDAQ'})
        df['등락구분'] = df['등락구분'].astype(str).replace({'2': '상승', '5': '하락', '3': '보합'})

        exclude_columns = [
            "매출액증가율", "영업이익", "영업이익증가율", "당기순이익", "상장일",
            "연속상한가일수", "연속하한가일수", "연속상하한가일수", "누적상한가일수", "누적하한가일수",
            "유보율", "종목정보", "참조지수레버리지타입", "1개월수익률", "3개월수익률", "6개월수익률", 
            "1년수익률", "순자산가치(NAV)", "괴리율부호", "괴리율", "순자산총액", "총보수",
            "발행사명", "실시간추정순자산가치(iNAV)", "종목타입", "시장경보구분", "장운영상태", 
            "상장주식수", "거래량변동", "거래량변동률", "전일거래량", "외국인보유수량"
        ]

        cols_to_drop = [col for col in df.columns if any(k in col for k in ['관리', '정지', '상태태그', 'ETF']) or col in exclude_columns]
        df = df.drop(columns=cols_to_drop, errors='ignore')

        numeric_cols = ['시가총액', '현재가', '등락률', '주가수익비율(PER)', '배당수익률', '자기자본이익률(ROE)', 
                        '주가순자산비율(PBR)', '총자산이익률(ROA)', "상한가", "하한가", "거래량", "시가", "고가", 
                        "저가", "매수호가", "매수잔량", "매도호가", "매도잔량", "전일비", "거래대금", "외국인비율", 
                        "상장주식수", "주당순이익(EPS)", "52주최고가", "52주최저가", "자산총계", "부채총계", "매출액", "주당배당금"]

        for col in numeric_cols:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')

        if '시가총액' in df.columns: df['시가총액'] = df['시가총액'] / 100000000
        if '거래대금' in df.columns: df['거래대금'] = df['거래대금'] / 100000000
        if '상장주식수' in df.columns: df['상장주식수'] = df['상장주식수'] / 10000

        rename_map = {'시가총액': '시가총액(억원)', '현재가': '현재가(원)', '주가수익비율(PER)': 'PER', 
                      '주가순자산비율(PBR)': 'PBR', '자기자본이익률(ROE)': 'ROE', '총자산이익률(ROA)': 'ROA', 
                      '거래대금': '거래대금(억원)', '상장주식수': '상장주식수(만주)'}
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        def format_price_with_arrow(row):
            price, status = row.get('현재가(원)', 0), row.get('등락구분', '')
            if pd.isna(price): return "-"
            symbol = "▲" if status == '상승' else "▼" if status == '하락' else "-"
            return f"{symbol} {int(price):,}"

        if '현재가(원)' in df.columns: df['현재가(원)'] = df.apply(format_price_with_arrow, axis=1)

        priority_cols = ['순위', '종목명', '종목코드', '소속구분','시가총액(억원)', '현재가(원)', '등락률', 'PER', '배당수익률', 'ROE', 'PBR', 'ROA']
        existing_priority = [c for c in priority_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in existing_priority]
        return df[existing_priority + other_cols]
        
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return pd.DataFrame()

def style_dataframe(row):
    status = row.get('등락구분', '')
    bg_color = '#fff5f5' if status == '상승' else '#f0f7ff' if status == '하락' else '#ffffff'
    font_color = '#e03131' if status == '상승' else '#1971c2' if status == '하락' else '#1a1a1a'
    
    return [f"background-color: {bg_color}; color: {'#1a1a1a' if col not in ['현재가(원)', '등락률'] else font_color}; font-weight: {'600' if col in ['현재가(원)', '등락률'] else 'normal'};" for col in row.index]

# 4. 메인 함수
def main():
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Market Pulse</div>
        <div class="hero-subtitle">Comprehensive tracking of KOSPI and KOSDAQ exchange data</div>
    </div>
    """, unsafe_allow_html=True)

    cookie_manager = stx.CookieManager()
    saved_market = cookie_manager.get("market_pref")
    saved_size = cookie_manager.get("size_pref")

    if saved_market is not None and "initialized" not in st.session_state:
        st.session_state["market_sb"] = saved_market
        if saved_size is not None: st.session_state["size_sb"] = int(saved_size)
        st.session_state["initialized"] = True
        st.rerun()

    def save_settings():
        cookie_manager.set("market_pref", st.session_state["market_sb"], expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key="set_market")
        cookie_manager.set("size_pref", st.session_state["size_sb"], expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key="set_size")

    market_options = {"전체": "ALL", "코스피": "KOSPI", "코스닥": "KOSDAQ"}
    size_options = [50, 100, 200]
    
    # Filter Controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1: selected_label = st.selectbox("시장 선택", options=list(market_options.keys()), key="market_sb", on_change=save_settings)
    with col2: selected_size = st.selectbox("조회 개수", options=size_options, key="size_sb", on_change=save_settings)
    with col3: search_term = st.text_input("종목명 검색", placeholder="Search by company name...")

    # 데이터 로드
    selected_code = market_options[selected_label]
    df_total_200 = load_stock_data(selected_code, 200)
    
    if not df_total_200.empty:
        # Gauge HTML 생성 함수
        def get_market_gauge_html(df_subset, title):
            counts = df_subset['등락구분'].value_counts()
            up_cnt, down_cnt, steady_cnt = int(counts.get('상승', 0)), int(counts.get('하락', 0)), int(counts.get('보합', 0))
            total = up_cnt + down_cnt + steady_cnt
            
            if total > 0:
                up_per, down_per, steady_per = (up_cnt/total)*100, (down_cnt/total)*100, (steady_cnt/total)*100
                return (
                    f'<div class="gauge-item">'
                    f'    <div class="gauge-header">'
                    f'        <span>{title}</span>'
                    f'        <span>'
                    f'            <span style="color: #ff4b4b;">▲ {up_cnt}</span> | '
                    f'            <span style="color: #888;">▬ {steady_cnt}</span> | '
                    f'            <span style="color: #007aff;">▼ {down_cnt}</span>'
                    f'        </span>'
                    f'    </div>'
                    f'    <div class="gauge-bar-container">'
                    f'        <div class="gauge-bar-up" style="width: {up_per}%;"></div>'
                    f'        <div class="gauge-bar-steady" style="width: {steady_per}%;"></div>'
                    f'        <div class="gauge-bar-down" style="width: {down_per}%;"></div>'
                    f'    </div>'
                    f'</div>'
                )
            return ""

        # Gauges Container
        gauge_html = get_market_gauge_html(df_total_200.head(50), "Market Sentiment (Top 50)")
        gauge_html += get_market_gauge_html(df_total_200.head(100), "Market Sentiment (Top 100)")
        gauge_html += get_market_gauge_html(df_total_200.head(200), "Market Sentiment (Top 200)")

        st.markdown(f'<div class="gauge-wrapper">{gauge_html}</div>', unsafe_allow_html=True)

        # 테이블 필터링
        df_kr = df_total_200.head(selected_size).copy()
        if search_term: df_kr = df_kr[df_kr['종목명'].str.contains(search_term, case=False)]

        format_dict = {"시가총액(억원)": "{:,.0f}", "등락률": "{:+.2f}%", "PER": "{:,.1f}", "PBR": "{:,.1f}", 
                       "배당수익률": "{:,.1f}", "ROE": "{:,.1f}", "ROA": "{:,.1f}", "상한가": "{:,.0f}", 
                       "하한가": "{:,.0f}", "거래량": "{:,.0f}", "시가": "{:,.0f}", "고가": "{:,.0f}", 
                       "저가": "{:,.0f}", "매수호가": "{:,.0f}", "매수잔량": "{:,.0f}", "매도호가": "{:,.0f}", 
                       "매도잔량": "{:,.0f}", "전일비": "{:,.0f}", "거래대금(억원)": "{:,.0f}", 
                       "외국인비율": "{:,.1f}%", "상장주식수": "{:,.0f}", "주당순이익(EPS)": "{:,.0f}", 
                       "52주최고가": "{:,.0f}", "52주최저가": "{:,.0f}", "자산총계": "{:,.0f}", 
                       "부채총계": "{:,.0f}", "매출액": "{:,.0f}", "주당배당금": "{:,.0f}"}
        
        available_format_cols = [c for c in format_dict.keys() if c in df_kr.columns]
        styled_df = df_kr.style.apply(style_dataframe, axis=1).format(format_dict, subset=available_format_cols)
        
        final_height = max(100, min((len(df_kr) * 35) + 43, 750))
        st.dataframe(styled_df, width='stretch', hide_index=True, height=final_height, column_config={"등락구분": None})
        
        st.markdown(f'<div style="text-align: right; color: #888; font-size: 0.8rem; margin-top: 15px;">Last updated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Source: Naver Finance</div>', unsafe_allow_html=True)
    else:
        st.write("Unable to load data. Please check your connection.")

if __name__ == "__main__":
    main()