"""
ETF Fund Flow 설정 파일
- ETF 리스트 및 카테고리 정의
- iShares product ID 매핑 (공식 Shares Outstanding 데이터용)
"""

# iShares ETF product ID 매핑
# URL: https://www.ishares.com/us/products/{ID}/...
ISHARES_PRODUCT_IDS = {
    "IWM":  "239710",  # iShares Russell 2000 ETF
    "IGV":  "239705",  # iShares Expanded Tech-Software Sector ETF
    "SOXX": "239705",  # iShares Semiconductor ETF (별도 확인 필요)
    "TLT":  "239454",  # iShares 20+ Year Treasury Bond ETF
    "HYG":  "239565",  # iShares iBoxx $ High Yield Corporate Bond ETF
    "LQD":  "239566",  # iShares iBoxx $ Investment Grade Corporate Bond ETF
    "EMB":  "239572",  # iShares J.P. Morgan USD Emerging Markets Bond ETF
    "EEM":  "239637",  # iShares MSCI Emerging Markets ETF
    "FXI":  "239536",  # iShares China Large-Cap ETF
    "EWJ":  "239665",  # iShares MSCI Japan ETF
    "EWY":  "239667",  # iShares MSCI South Korea ETF
    "EWZ":  "239612",  # iShares MSCI Brazil ETF
    "INDA": "239659",  # iShares MSCI India ETF
    "SLV":  "239855",  # iShares Silver Trust
}

# iShares ETF 슬러그 (URL용)
ISHARES_SLUGS = {
    "IWM":  "ishares-russell-2000-etf",
    "IGV":  "ishares-expanded-tech-software-sector-etf",
    "SOXX": "ishares-semiconductor-etf",
    "TLT":  "ishares-20-year-treasury-bond-etf",
    "HYG":  "ishares-iboxx-high-yield-corporate-bond-etf",
    "LQD":  "ishares-iboxx-investment-grade-corporate-bond-etf",
    "EMB":  "ishares-jp-morgan-usd-emerging-markets-bond-etf",
    "EEM":  "ishares-msci-emerging-markets-etf",
    "FXI":  "ishares-china-large-cap-etf",
    "EWJ":  "ishares-msci-japan-etf",
    "EWY":  "ishares-msci-south-korea-etf",
    "EWZ":  "ishares-msci-brazil-etf",
    "INDA": "ishares-msci-india-etf",
    "SLV":  "ishares-silver-trust",
}

# 공식 데이터 제공 ETF 세트
OFFICIAL_TICKERS = set(ISHARES_PRODUCT_IDS.keys())

ETF_LIST = {
    "미국 대표 지수": {
        "SPY":  {"name_kr": "S&P 500",      "official": False},
        "QQQ":  {"name_kr": "나스닥 100",   "official": False},
        "DIA":  {"name_kr": "다우",          "official": False},
        "IWM":  {"name_kr": "러셀 2000",    "official": True},
    },
    "섹터": {
        "XLF":  {"name_kr": "금융",          "official": False},
        "XLE":  {"name_kr": "에너지",        "official": False},
        "XLK":  {"name_kr": "기술",          "official": False},
        "XLV":  {"name_kr": "헬스케어",      "official": False},
        "IGV":  {"name_kr": "소프트웨어",    "official": True},
        "SMH":  {"name_kr": "반도체",        "official": False},
        "SOXX": {"name_kr": "반도체",        "official": True},
        "XBI":  {"name_kr": "바이오",        "official": False},
        "ITB":  {"name_kr": "주택건설",      "official": False},
    },
    "테마/성장": {
        "ARKK": {"name_kr": "혁신",          "official": False},
        "HACK": {"name_kr": "사이버보안",    "official": False},
        "TAN":  {"name_kr": "태양광",        "official": False},
        "LIT":  {"name_kr": "리튬/배터리",   "official": False},
        "BOTZ": {"name_kr": "로봇/AI",       "official": False},
    },
    "커머디티": {
        "GLD":  {"name_kr": "금",            "official": False},
        "SLV":  {"name_kr": "은",            "official": True},
        "USO":  {"name_kr": "원유",          "official": False},
        "UNG":  {"name_kr": "천연가스",      "official": False},
        "COPX": {"name_kr": "구리",          "official": False},
        "WEAT": {"name_kr": "밀",            "official": False},
    },
    "채권": {
        "TLT":  {"name_kr": "미국 장기채",   "official": True},
        "HYG":  {"name_kr": "하이일드",      "official": True},
        "LQD":  {"name_kr": "투자등급 회사채","official": True},
        "EMB":  {"name_kr": "신흥국 채권",   "official": True},
    },
    "국가/지역": {
        "EEM":  {"name_kr": "신흥국",        "official": True},
        "FXI":  {"name_kr": "중국",          "official": True},
        "EWJ":  {"name_kr": "일본",          "official": True},
        "EWY":  {"name_kr": "한국",          "official": True},
        "EWZ":  {"name_kr": "브라질",        "official": True},
        "INDA": {"name_kr": "인도",          "official": True},
    },
    "변동성/헷지": {
        "VXX":  {"name_kr": "VIX",           "official": False},
        "UVXY": {"name_kr": "VIX 2배",       "official": False},
    },
}

# 전체 티커 리스트
ALL_TICKERS = [t for cat in ETF_LIST.values() for t in cat.keys()]

# 티커별 플랫 정보
TICKER_INFO = {
    ticker: {
        "name_kr": info["name_kr"],
        "official": info["official"],
        "category": cat,
    }
    for cat, tickers in ETF_LIST.items()
    for ticker, info in tickers.items()
}

if __name__ == "__main__":
    official = [t for t, v in TICKER_INFO.items() if v["official"]]
    estimated = [t for t, v in TICKER_INFO.items() if not v["official"]]
    print(f"전체: {len(ALL_TICKERS)}개")
    print(f"공식 (iShares): {len(official)}개 → {official}")
    print(f"추정 (Volume):  {len(estimated)}개 → {estimated}")
