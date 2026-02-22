ETF_LIST = {
    "미국 대표 지수": {
        "SPY": "S&P 500",
        "QQQ": "나스닥 100",
        "DIA": "다우",
        "IWM": "러셀 2000",
    },
    "섹터": {
        "XLF": "금융",
        "XLE": "에너지",
        "XLK": "기술",
        "XLV": "헬스케어",
        "IGV": "소프트웨어",
        "SMH": "반도체",
        "SOXX": "반도체",
        "XBI": "바이오",
        "ITB": "주택건설",
    },
    "테마/성장": {
        "ARKK": "혁신",
        "HACK": "사이버보안",
        "TAN": "태양광",
        "LIT": "리튬/배터리",
        "BOTZ": "로봇/AI",
    },
    "커머디티": {
        "GLD": "금",
        "SLV": "은",
        "USO": "원유",
        "UNG": "천연가스",
        "COPX": "구리",
        "WEAT": "밀",
    },
    "채권": {
        "TLT": "미국 장기채",
        "HYG": "하이일드",
        "LQD": "투자등급 회사채",
        "EMB": "신흥국 채권",
    },
    "국가/지역": {
        "EEM": "신흥국",
        "FXI": "중국",
        "EWJ": "일본",
        "EWY": "한국",
        "EWZ": "브라질",
        "INDA": "인도",
    },
    "변동성/헷지": {
        "VXX": "VIX",
        "UVXY": "VIX 2배",
    },
}

# 전체 티커 리스트 (flat)
ALL_TICKERS = []
TICKER_INFO = {}  # ticker -> {"category": ..., "name_kr": ...}

for category, tickers in ETF_LIST.items():
    for ticker, name_kr in tickers.items():
        if ticker not in ALL_TICKERS:
            ALL_TICKERS.append(ticker)
            TICKER_INFO[ticker] = {"category": category, "name_kr": name_kr}

print(f"Total ETFs: {len(ALL_TICKERS)}")
print(f"Tickers: {ALL_TICKERS}")
