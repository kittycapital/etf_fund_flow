"""
ETF Fund Flow 데이터 벌크 다운로드 스크립트
- 전체 ETF의 히스토리컬 가격(OHLCV) 다운로드
- 현재 shares outstanding 스냅샷 저장
- 최초 1회 실행용
"""

import os
import json
import time
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone

# config에서 ETF 리스트 가져오기
from config import ALL_TICKERS, TICKER_INFO, ETF_LIST

# 데이터 저장 경로
DATA_DIR = "data"
PRICES_DIR = os.path.join(DATA_DIR, "prices")
SHARES_DIR = os.path.join(DATA_DIR, "shares_outstanding")
META_DIR = os.path.join(DATA_DIR, "meta")

def setup_directories():
    """데이터 디렉토리 생성"""
    for d in [PRICES_DIR, SHARES_DIR, META_DIR]:
        os.makedirs(d, exist_ok=True)
    print("✅ 디렉토리 생성 완료")

def download_price_data(ticker, max_retries=3):
    """개별 ETF 가격 데이터 다운로드"""
    for attempt in range(max_retries):
        try:
            etf = yf.Ticker(ticker)
            df = etf.history(period="max", auto_adjust=True)
            
            if df.empty:
                print(f"  ⚠️  {ticker}: 데이터 없음")
                return None
            
            # 필요한 컬럼만 유지
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            df.index = df.index.strftime("%Y-%m-%d")
            df.index.name = "Date"
            
            # CSV 저장
            filepath = os.path.join(PRICES_DIR, f"{ticker}.csv")
            df.to_csv(filepath)
            
            print(f"  ✅ {ticker}: {len(df)}일 ({df.index[0]} ~ {df.index[-1]})")
            return df
            
        except Exception as e:
            print(f"  ❌ {ticker}: 시도 {attempt+1}/{max_retries} 실패 - {e}")
            time.sleep(2)
    
    return None

def download_shares_outstanding(tickers):
    """현재 shares outstanding 스냅샷 저장"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot = {"date": today, "data": {}}
    
    for ticker in tickers:
        try:
            etf = yf.Ticker(ticker)
            info = etf.info
            shares = info.get("sharesOutstanding", None)
            
            if shares:
                snapshot["data"][ticker] = shares
                print(f"  ✅ {ticker}: {shares:,.0f} shares")
            else:
                print(f"  ⚠️  {ticker}: shares outstanding 없음")
                
        except Exception as e:
            print(f"  ❌ {ticker}: {e}")
        
        time.sleep(0.5)  # rate limit 방지
    
    # 일별 스냅샷 CSV에 추가
    snapshot_file = os.path.join(SHARES_DIR, "daily_shares.csv")
    
    if os.path.exists(snapshot_file):
        existing = pd.read_csv(snapshot_file, index_col=0)
    else:
        existing = pd.DataFrame()
    
    new_row = pd.DataFrame(snapshot["data"], index=[today])
    combined = pd.concat([existing, new_row])
    combined = combined[~combined.index.duplicated(keep="last")]
    combined.sort_index(inplace=True)
    combined.index.name = "Date"
    combined.to_csv(snapshot_file)
    
    print(f"\n✅ Shares outstanding 저장: {len(snapshot['data'])}개 ETF")
    return snapshot

def save_metadata():
    """ETF 메타데이터 저장 (카테고리, 한글명 등)"""
    meta = {
        "etf_list": {cat: {t: n for t, n in tickers.items()} 
                     for cat, tickers in ETF_LIST.items()},
        "ticker_info": TICKER_INFO,
        "all_tickers": ALL_TICKERS,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    
    filepath = os.path.join(META_DIR, "etf_meta.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 메타데이터 저장: {filepath}")

def main():
    print("=" * 60)
    print("ETF Fund Flow 벌크 다운로드")
    print(f"대상: {len(ALL_TICKERS)}개 ETF")
    print(f"시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 디렉토리 생성
    setup_directories()
    
    # 2. 가격 데이터 다운로드
    print(f"\n📊 가격 데이터 다운로드 ({len(ALL_TICKERS)}개 ETF)")
    print("-" * 40)
    
    success = 0
    failed = []
    
    for i, ticker in enumerate(ALL_TICKERS, 1):
        info = TICKER_INFO[ticker]
        print(f"[{i}/{len(ALL_TICKERS)}] {ticker} ({info['name_kr']} - {info['category']})")
        
        result = download_price_data(ticker)
        if result is not None:
            success += 1
        else:
            failed.append(ticker)
        
        time.sleep(1)  # rate limit 방지
    
    print(f"\n가격 다운로드 완료: {success}/{len(ALL_TICKERS)} 성공")
    if failed:
        print(f"실패: {failed}")
    
    # 3. Shares Outstanding 스냅샷
    print(f"\n📈 Shares Outstanding 수집")
    print("-" * 40)
    download_shares_outstanding(ALL_TICKERS)
    
    # 4. 메타데이터 저장
    print(f"\n📋 메타데이터 저장")
    print("-" * 40)
    save_metadata()
    
    # 5. 요약
    print("\n" + "=" * 60)
    print("✅ 벌크 다운로드 완료!")
    print(f"종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 용량 확인
    total_size = 0
    for root, dirs, files in os.walk(DATA_DIR):
        for f in files:
            total_size += os.path.getsize(os.path.join(root, f))
    print(f"총 데이터 용량: {total_size / 1024 / 1024:.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    main()
