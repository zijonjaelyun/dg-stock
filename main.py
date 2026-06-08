import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="국내외 주요 주식 수익률 비교", layout="wide")

st.title("📈 국내외 주요 주식 수익률 비교 대시보드")
st.markdown("한국과 미국 주요 주식의 **누적 수익률**을 비교해 보세요. (yfinance 데이터 기준)")

# 2. 사이드바 - 설정 영역
st.sidebar.header("⚙️ 설정")

# 기본 제공 주식 리스트 (원하는 종목을 마음대로 추가/수정 가능)
stock_dict = {
    "삼성전자 (KR)": "005930.KS",
    "SK하이닉스 (KR)": "000660.KS",
    "현대차 (KR)": "005380.KS",
    "NAVER (KR)": "035420.KS",
    "Apple (US)": "AAPL",
    "Microsoft (US)": "MSFT",
    "NVIDIA (US)": "NVDA",
    "Tesla (US)": "TSLA",
    "S&P 500 (ETF)": "SPY",
    "나스닥 100 (ETF)": "QQQ"
}

# 종목 선택 (기본값으로 삼성전자, Apple, NVIDIA 선택)
selected_stocks = st.sidebar.multiselect(
    "비교할 종목을 선택하세요:",
    list(stock_dict.keys()),
    default=["삼성전자 (KR)", "Apple (US)", "NVIDIA (US)"]
)

# 기간 선택
start_date = st.sidebar.date_input("시작일", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("종료일", datetime.now())

# 3. 데이터 로드 및 가공
if not selected_stocks:
    st.warning("⚠️ 최소 한 개 이상의 종목을 선택해 주세요.")
else:
    returns_df = pd.DataFrame()
    summary_list = []

    with st.spinner('주가 데이터를 가져오는 중입니다...'):
        for name in selected_stocks:
            ticker = stock_dict[name]
            # yfinance 데이터 다운로드
            data = yf.Ticker(ticker).history(start=start_date, end=end_date)
            
            if not data.empty:
                # 한국/미국 시장 휴장일 차이로 인한 결측치는 선형 보간 처리
                close_prices = data['Close'].dropna()
                
                if len(close_prices) > 0:
                    # 누적 수익률 계산: (현재가격 / 시작가격 - 1) * 100
                    initial_price = close_prices.iloc[0]
                    current_price = close_prices.iloc[-1]
                    cum_return = ((close_prices / initial_price) - 1) * 100
                    
                    # 차트용 데이터프레임 병합
                    returns_df[name] = cum_return
                    
                    # 요약 데이터 저장
                    summary_list.append({
                        "종목명": name,
                        "티커": ticker,
                        "시작일 종가": f"{initial_price:,.2f}",
                        "최근 종가": f"{current_price:,.2f}",
                        "기간 수익률": f"{((current_price / initial_price) - 1) * 100:.2f}%"
                    })

    # 다른 국가 간 휴장일 차이로 발생하는 NaN 값 깔끔하게 메우기
    returns_df = returns_df.ffill().bfill()

    # 4. 시각화 및 결과 출력
    if not returns_df.empty:
        # 레이아웃 분할 (차트와 표를 깔끔하게 배치)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("📊 누적 수익률 (%) 추이")
            # Plotly 라인 차트 생성
            fig = px.line(
                returns_df, 
                labels={"value": "수익률 (%)", "Date": "날짜", "variable": "종목"},
                title=f"{start_date} ~ {end_date} 기준"
            )
            fig.update_layout(
                hovermode="x unified", 
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("📌 종목별 요약")
            summary_df = pd.DataFrame(summary_list)
            # 인덱스를 종목명으로 변경하여 깔끔하게 출력
            summary_df = summary_df.set_index("종목명")
            st.dataframe(summary_df[["기간 수익률", "최근 종가"]])
            
        # 하단 전체 데이터 테이블 출력
        st.subheader("📋 상세 데이터 (종가 기준 수익률 타임라인)")
        st.dataframe(returns_df.tail(10).style.format("{:.2f}%"))
    else:
        st.error("❌ 선택한 기간에 대한 데이터를 불러오지 못했습니다. 날짜 설정을 확인해 주세요.")
