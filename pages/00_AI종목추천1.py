def generate_ai_signal(df):
    """주가 데이터를 바탕으로 간단한 AI 투자 시그널을 생성합니다."""
    if len(df) < 20:
        return "데이터 부족", "⚪"
    
    # 1. 이동평균선 계산 (단기 5일, 장기 20일)
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    
    current_price = df['Close'].iloc[-1]
    ma5 = df['MA5'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    
    # 2. RSI (상대강도지수) 계산 (과매수/과매도 판단)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    
    # 3. AI 시그널 조합 조건문
    if ma5 > ma20 and current_rsi < 40:
        return "적극 매수 (단기 반등 및 과매도)", "🔥"
    elif ma5 > ma20:
        return "매수 (상승 트렌드 유지)", "🟢"
    elif current_rsi > 70:
        return "매도 (단기 과열 상태)", "🚨"
    elif ma5 < ma20:
        return "관망 (하락 트렌드 진입)", "🟡"
    else:
        return "중립", "⚪"
