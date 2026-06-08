import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 설정 (멀티페이지용)
st.set_page_config(page_title="AI 종목 추천", page_icon="🤖", layout="wide")

st.title("🤖 AI 기술적 지표 종목 분석")
st.markdown("이동평균선(MA)과 상대강도지수(RSI)를 분석하여 현재 주가의 상태와 간단한 투자 시그널을 제공합니다.")

# 2. AI 시그널 계산 함수
def generate_ai_signal(df):
    """주가 데이터를 바탕으로 간단한 AI 투자 시그널을 생성합니다."""
    if len(df) < 20:
        return "데이터 부족", "⚪", 0, 0, 0
    
    # 이동평균선 계산 (단기 5일, 장기 20일)
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    # RSI (상대강도지수) 계산 (14일 기준)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    
    # 최신 지표 값 추출
    current_price = df['Close'].iloc[-1]
    ma5 = df['MA5'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    current_rsi = rsi.iloc[-1]
    
    # AI 시그널 조합 조건문
    if ma5 > ma20 and current_rsi < 40:
        signal, emoji = "적극 매수 (단기 반등 및 과매도)", "🔥"
    elif ma5 > ma20:
        signal, emoji = "매수 (상승 트렌드 유지)", "🟢"
    elif current_rsi > 70:
        signal, emoji = "매도 (단기 과열 상태)", "🚨"
    elif ma5 < ma20:
        signal, emoji = "관망 (하락 트렌드 진입)", "🟡"
    else:
        signal, emoji = "중립", "⚪"
        
    return signal, emoji, ma5, ma20, current_rsi

# 3. 분석할 종목 선택 영역
st.divider()
st.subheader("🔍 분석 종목 선택")

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

# 단일 종목 선택 (Selectbox)
selected_stock = st.selectbox("어떤 종목을 분석할까요?", list(stock_dict.keys()))

# 4. 분석 실행 및 결과 출력
if st.button("🚀 AI 분석 시작", type="primary"):
    ticker = stock_dict[selected_stock]
    
    with st.spinner(f"'{selected_stock}' 데이터를 분석 중입니다..."):
        # 이동평균선(20일)과 RSI(14일) 계산을 위해 최근 90일치 데이터 가져오기
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        data = yf.Ticker(ticker).history(start=start_date, end=end_date)
        
        if len(data) >= 20:
            # AI 분석 함수 호출
            signal, emoji, ma5, ma20, current_rsi = generate_ai_signal(data)
            current_price = data['Close'].iloc[-1]
            
            st.divider()
            st.subheader(f"📊 [{selected_stock}] AI 분석 리포트")
            
            # 종합 의견 강조 표시
            st.success(f"**💡 AI 종합 의견:** {emoji} **{signal}**")
            
            # 주요 지표 메트릭(Metric) 표시
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("현재 종가", f"{current_price:,.2f}")
            with col2:
                # RSI 수치에 따라 색상/문구 변경
                rsi_desc = "과매수 구간 (70 이상)" if current_rsi >= 70 else "과매도 구간 (30 이하)" if current_rsi <= 30 else "보통"
                st.metric("RSI (14일)", f"{current_rsi:.1f}", rsi_desc, delta_color="off")
            with col3:
                # 단기 이평선이 장기 이평선 위에 있는지 여부
                trend = "단기 상승세 (정배열)" if ma5 > ma20 else "단기 하락세 (역배열)"
                st.metric("이동평균선 (5일/20일)", trend)
                
            # 주의사항 안내
            st.info("※ 본 리포트는 과거 주가 데이터를 기반으로 한 단순 기술적 지표(이동평균선, RSI) 분석 결과입니다. 실제 투자 결정에는 참고용으로만 활용하시기 바랍니다.")
            
        else:
            st.error("❌ 분석에 필요한 데이터가 부족합니다. 상장한 지 얼마 안 된 종목이거나 일시적인 통신 오류일 수 있습니다.")
