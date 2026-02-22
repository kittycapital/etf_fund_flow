"""
ETF Fund Flow 일일 업데이트 스크립트
- GitHub Actions에서 매일 실행
- 최신 가격 데이터 append
- Shares outstanding 스냅샷 추가
"""

import os
import json
import time
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta

from config import ALL_TICKERS, TICKER_INFO

DATA_DIR = "data"
PRICES_DIR = os.path.join(DATA_DIR, "prices")
SHARES_DIR = os.path.join(DATA_DIR, "shares_outstanding")

def update_price_data(ticker, lookback_days=5):
    """
    개별 ETF 최신 가격 데이터 업데이트
    lookback_days: 혹시 빠진 날짜가 있을 수 있으니 며칠치 더 가져옴
    """
    filepath = os.path.join(PRICES_DIR, f"{ticker}.csv")
    
    try:
        # 기존 데이터 로드
        if os.path.exists(filepath):
            existing = pd.read_csv(filepath, index_col="Date")
            last_date = existing.index[-1]
        else:
            # 기존 파일 없으면 전체 다운로드
            print(f"  ⚠️  {ticker}: 기존 파일 없음 - 전체 다운로드")
            etf = yf.Ticker(ticker)
            df = etf.history(period="max", auto_adjust=True)
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            df.index = df.index.strftime("%Y-%m-%d")
            df.index.name = "Date"
            df.to_csv(filepath)
            print(f"  ✅ {ticker}: {len(df)}일 전체 다운로드")
            return True
        
        # 최근 데이터 가져오기
        start_date = (datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        etf = yf.Ticker(ticker)
        new_data = etf.history(start=start_date, auto_adjust=True)
        
        if new_data.empty:
            print(f"  ⚠️  {ticker}: 새 데이터 없음")
            return False
        
        new_data = new_data[["Open", "High", "Low", "Close", "Volume"]]
        new_data.index = new_data.index.strftime("%Y-%m-%d")
        new_data.index.name = "Date"
        
        # 기존 데이터에 머지 (중복 제거, 최신값 우선)
        combined = pd.concat([existing, new_data])
        combined = combined[~combined.index.duplicated(keep="last")]
        combined.sort_index(inplace=True)
        combined.to_csv(filepath)
        
        new_count = len(combined) - len(existing)
        if new_count > 0:
            print(f"  ✅ {ticker}: {new_count}일 추가 (마지막: {combined.index[-1]})")
        else:
            print(f"  ⏭️  {ticker}: 변경 없음 (마지막: {combined.index[-1]})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ {ticker}: {e}")
        return False

def update_shares_outstanding():
    """일별 shares outstanding 스냅샷 추가"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot_file = os.path.join(SHARES_DIR, "daily_shares.csv")
    
    # 기존 데이터 로드
    if os.path.exists(snapshot_file):
        existing = pd.read_csv(snapshot_file, index_col=0)
    else:
        existing = pd.DataFrame()
    
    # 오늘 데이터 수집
    today_data = {}
    for ticker in ALL_TICKERS:
        try:
            etf = yf.Ticker(ticker)
            info = etf.info
            shares = info.get("sharesOutstanding", None)
            if shares:
                today_data[ticker] = shares
        except Exception as e:
            print(f"  ❌ {ticker} shares: {e}")
        time.sleep(0.3)
    
    if not today_data:
        print("⚠️  Shares outstanding 데이터 수집 실패")
        return
    
    # 추가 및 저장
    new_row = pd.DataFrame(today_data, index=[today])
    combined = pd.concat([existing, new_row])
    combined = combined[~combined.index.duplicated(keep="last")]
    combined.sort_index(inplace=True)
    combined.index.name = "Date"
    combined.to_csv(snapshot_file)
    
    print(f"✅ Shares outstanding 업데이트: {len(today_data)}개 ETF ({today})")

def update_last_updated():
    """마지막 업데이트 시간 기록"""
    meta_file = os.path.join(DATA_DIR, "meta", "etf_meta.json")
    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            meta = json.load(f)
        meta["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

def main():
    print("=" * 60)
    print("ETF Fund Flow 일일 업데이트")
    print(f"시작: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"대상: {len(ALL_TICKERS)}개 ETF")
    print("=" * 60)
    
    # 1. 가격 데이터 업데이트
    print(f"\n📊 가격 데이터 업데이트")
    print("-" * 40)
    
    success = 0
    failed = []
    
    for i, ticker in enumerate(ALL_TICKERS, 1):
        info = TICKER_INFO[ticker]
        print(f"[{i}/{len(ALL_TICKERS)}] {ticker} ({info['name_kr']})")
        
        if update_price_data(ticker):
            success += 1
        else:
            failed.append(ticker)
        
        time.sleep(0.5)
    
    print(f"\n가격 업데이트: {success}/{len(ALL_TICKERS)} 성공")
    if failed:
        print(f"실패: {failed}")
    
    # 2. Shares Outstanding 업데이트
    print(f"\n📈 Shares Outstanding 업데이트")
    print("-" * 40)
    update_shares_outstanding()
    
    # 3. 메타데이터 업데이트
    update_last_updated()
    
    print("\n" + "=" * 60)
    print("✅ 일일 업데이트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()
