import streamlit as st
import requests
import pandas as pd
import datetime
import extra_streamlit_components as stx

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
        
        /* 셀렉트박스 및 인풋 스타일 */
        div[data-baseweb="select"], div[data-baseweb="input"] {
            font-family: 'Helvetica Neue', sans-serif;
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
        json_data = []
        
        if isinstance(raw_data, list):
            json_data = raw_data
        elif isinstance(raw_data, dict):
            json_data = raw_data.get('data', [])
        
        df = pd.DataFrame(json_data)
        
        if df.empty:
            return df

        # 순위 컬럼 생성 (인덱스 + 1)
        df['순위'] = df.index + 1

        # 1. 컬럼명 한글 변환
        df = df.rename(columns=KEY_MAP)

        # 2. 소속/등락 변환
        df['소속구분'] = df['소속구분'].astype(str).replace({'0': 'KOSPI', '1': 'KOSDAQ'})
        df['등락구분'] = df['등락구분'].astype(str).replace({'2': '상승', '5': '하락', '3': '보합'})

        # 3. 불필요 컬럼 제거
        exclude_columns = [
            "매출액증가율", "영업이익", "영업이익증가율", "당기순이익", "상장일",
            "연속상한가일수", "연속하한가일수", "연속상하한가일수", "누적상한가일수", "누적하한가일수",
            "유보율", "종목정보", "참조지수레버리지타입",
            "1개월수익률", "3개월수익률", "6개월수익률", "1년수익률",
            "순자산가치(NAV)", "괴리율부호", "괴리율", "순자산총액", "총보수",
            "발행사명", "실시간추정순자산가치(iNAV)",
            "종목타입", "시장경보구분", "장운영상태", "상장주식수", 
            "거래량변동", "거래량변동률", "전일거래량", "외국인보유수량"
        ]

        cols_to_drop = []
        for col in df.columns:
            if any(k in col for k in ['관리', '정지', '상태태그']):
                cols_to_drop.append(col)
            elif 'ETF' in col:
                cols_to_drop.append(col)
            elif col in exclude_columns:
                cols_to_drop.append(col)

        df = df.drop(columns=cols_to_drop, errors='ignore')

        # 4. 숫자형 변환
        numeric_cols = ['시가총액', '현재가', '등락률', '주가수익비율(PER)', '배당수익률', 
                        '자기자본이익률(ROE)', '주가순자산비율(PBR)', '총자산이익률(ROA)', 
                        "상한가", "하한가", "거래량", "시가", "고가", "저가", 
                        "매수호가", "매수잔량", "매도호가", "매도잔량", 
                        "전일비", "거래대금", "외국인비율", "외국인보유수량", "상장주식수",
                        "주당순이익(EPS)", "52주최고가", "52주최저가",
                        "자산총계", "부채총계", "매출액", "주당배당금"]

        for col in numeric_cols:
            if col in df.columns:
                 df[col] = pd.to_numeric(df[col], errors='coerce')

        # 5. 단위 변환
        if '시가총액' in df.columns:
            df['시가총액'] = df['시가총액'] / 100000000
        if '거래대금' in df.columns:
            df['거래대금'] = df['거래대금'] / 100000000
        if '외국인보유수량' in df.columns:
            df['외국인보유수량'] = df['외국인보유수량'] / 10000
        if '상장주식수' in df.columns:
            df['상장주식수'] = df['상장주식수'] / 10000

        # 6. 컬럼명 변경
        rename_map = {
            '시가총액': '시가총액(억원)',
            '현재가': '현재가(원)',
            '주가수익비율(PER)': 'PER',
            '주가순자산비율(PBR)': 'PBR',
            '자기자본이익률(ROE)': 'ROE',
            '총자산이익률(ROA)': 'ROA',
            '거래대금': '거래대금(억원)',
            '외국인보유수량': '외국인보유수량(만주)',
            '상장주식수': '상장주식수(만주)'
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

        # 7. 현재가 화살표 표시
        def format_price_with_arrow(row):
            price = row.get('현재가(원)', 0)
            status = row.get('등락구분', '')
            if pd.isna(price): return "-"
            symbol = "-"
            if status == '상승': symbol = "▲"
            elif status == '하락': symbol = "▼"
            return f"{symbol} {int(price):,}"

        if '현재가(원)' in df.columns:
            df['현재가(원)'] = df.apply(format_price_with_arrow, axis=1)

        # 8. 컬럼 순서 재배치
        priority_cols = [
            '순위', '종목명', '종목코드', '소속구분','시가총액(억원)', '현재가(원)', '등락률',
            'PER', '배당수익률', 'ROE', 'PBR', 'ROA'
        ]
        existing_priority = [c for c in priority_cols if c in df.columns]
        other_cols = [c for c in df.columns if c not in existing_priority]
        df = df[existing_priority + other_cols]
        
        return df
        
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return pd.DataFrame()

# 5. 스타일링 함수
def style_dataframe(row):
    status = row.get('등락구분', '')
    
    if status == '상승':
        bg_color = '#FFF0F0'
        font_color = 'red'
    elif status == '하락':
        bg_color = '#F0F8FF'
        font_color = 'blue'
    else:
        bg_color = '#FFFFFF'
        font_color = 'black'
    
    styles = []
    for col in row.index:
        style = f'background-color: {bg_color};'
        if col in ['현재가(원)', '등락률']:
            style += f' color: {font_color}; font-weight: bold;'
        else:
            style += ' color: black;'
        styles.append(style)
        
    return styles

# 6. 메인 함수
def main():
    st.title("KOREA STOCK MARKET SUM")

    cookie_manager = stx.CookieManager()
    saved_market = cookie_manager.get("market_pref")
    saved_size = cookie_manager.get("size_pref")

    if saved_market is not None and "initialized" not in st.session_state:
        st.session_state["market_sb"] = saved_market
        if saved_size is not None:
            st.session_state["size_sb"] = int(saved_size)
        st.session_state["initialized"] = True
        st.rerun()

    def save_settings():
        cookie_manager.set(
            "market_pref", 
            st.session_state["market_sb"], 
            expires_at=datetime.datetime.now() + datetime.timedelta(days=30),
            key="set_market"
        )
        cookie_manager.set(
            "size_pref", 
            st.session_state["size_sb"], 
            expires_at=datetime.datetime.now() + datetime.timedelta(days=30),
            key="set_size"
        )

    market_options = {"전체": "ALL", "코스피": "KOSPI", "코스닥": "KOSDAQ"}
    size_options = [10, 50, 100]
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        selected_label = st.selectbox(
            "시장 선택", 
            options=list(market_options.keys()), 
            key="market_sb",
            on_change=save_settings 
        )
    
    with col2:
        selected_size = st.selectbox(
            "조회 개수 (Top N)", 
            options=size_options, 
            key="size_sb",
            on_change=save_settings
        )

    with col3:
        search_term = st.text_input("종목명 검색", placeholder="종목명을 입력하세요 (예: 삼성)")

    # 데이터 로드 및 출력
    selected_code = market_options[selected_label]
    df_kr = load_stock_data(selected_code, selected_size)
    
    if not df_kr.empty:
        if search_term:
            df_kr = df_kr[df_kr['종목명'].str.contains(search_term)]

        # --- 추가된 부분: 시장 등락 현황 Gauge ---
        counts = df_kr['등락구분'].value_counts()
        up_cnt = int(counts.get('상승', 0))
        down_cnt = int(counts.get('하락', 0))
        steady_cnt = int(counts.get('보합', 0))
        total_gauge = up_cnt + down_cnt + steady_cnt

        if total_gauge > 0:
            up_per = (up_cnt / total_gauge) * 100
            down_per = (down_cnt / total_gauge) * 100
            steady_per = (steady_cnt / total_gauge) * 100
            
            st.markdown(f"""
                <div style="margin-bottom: 25px; padding: 12px; border: 1px solid #F0F0F0; border-radius: 10px; background-color: #FAFAFA;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9rem; font-weight: 600;">
                        <span style="color: #FF4B4B;">상승 {up_cnt}</span>
                        <span style="color: #666666;">보합 {steady_cnt}</span>
                        <span style="color: #1C83E1;">하락 {down_cnt}</span>
                    </div>
                    <div style="display: flex; width: 100%; height: 12px; background-color: #E0E0E0; border-radius: 6px; overflow: hidden;">
                        <div style="width: {up_per}%; background-color: #FF4B4B;"></div>
                        <div style="width: {steady_per}%; background-color: #CCCCCC;"></div>
                        <div style="width: {down_per}%; background-color: #1C83E1;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        # ------------------------------------------

        format_dict = {
            "시가총액(억원)": "{:,.0f}",
            "등락률": "{:+.2f}%",
            "PER": "{:,.1f}",
            "PBR": "{:,.1f}",
            "배당수익률": "{:,.1f}",
            "ROE": "{:,.1f}",
            "ROA": "{:,.1f}",
            "상한가": "{:,.0f}",
            "하한가": "{:,.0f}",
            "거래량": "{:,.0f}",
            "시가": "{:,.0f}",
            "고가": "{:,.0f}",
            "저가": "{:,.0f}",
            "매수호가": "{:,.0f}",
            "매수잔량": "{:,.0f}",
            "매도호가": "{:,.0f}",
            "매도잔량": "{:,.0f}",
            "전일비": "{:,.0f}",
            "거래대금(억원)": "{:,.0f}",
            "외국인비율": "{:,.1f}%",
            "외국인보유수량": "{:,.0f}",
            "상장주식수": "{:,.0f}",
            "주당순이익(EPS)": "{:,.0f}",
            "52주최고가": "{:,.0f}",
            "52주최저가": "{:,.0f}",
            "자산총계": "{:,.0f}",
            "부채총계": "{:,.0f}",
            "매출액": "{:,.0f}",
            "주당배당금": "{:,.0f}"
        }
        
        available_format_cols = [c for c in format_dict.keys() if c in df_kr.columns]
        
        styled_df = (
            df_kr.style
            .apply(style_dataframe, axis=1) 
            .format(format_dict, subset=available_format_cols)
        )

        row_height = 35
        header_height = 40
        buffer = 3
        
        calculated_height = (len(df_kr) * row_height) + header_height + buffer
        MAX_TABLE_HEIGHT = 750 
        final_height = min(calculated_height, MAX_TABLE_HEIGHT)
        if final_height < 100:
            final_height = 100

        st.dataframe(
            styled_df, 
            width='stretch', 
            hide_index=True,
            height=final_height,
            column_config={
                "등락구분": None
            }
        )
        
        cnt = len(df_kr)
        st.markdown(f"""
        <div style="text-align: right; color: #888; font-size: 0.8em; margin-top: 10px;">
            Items displayed: {cnt} | Source: Naver Finance
        </div>
        """, unsafe_allow_html=True)
    else:
        st.write("데이터를 불러올 수 없습니다.")

if __name__ == "__main__":
    main()