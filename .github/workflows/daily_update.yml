"""
ETF 자금 레이더 — 일일 업데이트 스크립트
- GitHub Actions에서 매일 실행
- 가격 데이터 (전체 ETF): yfinance
- Shares Outstanding (iShares ETF): iShares 공식 CSV → 정확한 Fund Flow
- Shares Outstanding (非iShares ETF): yfinance info 스냅샷 → 추정용
"""

import os
import io
import json
import time
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta

from config import ALL_TICKERS, TICKER_INFO, ISHARES_PRODUCT_IDS, ISHARES_SLUGS, OFFICIAL_TICKERS

DATA_DIR = "data"
PRICES_DIR = os.path.join(DATA_DIR, "prices")
SHARES_DIR = os.path.join(DATA_DIR, "shares_outstanding")
ISHARES_DIR = os.path.join(DATA_DIR, "ishares")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def update_price_data(ticker, lookback_days=5):
    filepath = os.path.join(PRICES_DIR, f"{ticker}.csv")
    try:
        if os.path.exists(filepath):
            existing = pd.read_csv(filepath, index_col="Date")
            last_date = existing.index[-1]
        else:
            print(f"  ⚠️  {ticker}: 기존 파일 없음 - 전체 다운로드")
            etf = yf.Ticker(ticker)
            df = etf.history(period="max", auto_adjust=True)
            df = df[["Open", "High", "Low", "Close", "Volume"]]
            df.index = df.index.strftime("%Y-%m-%d")
            df.index.name = "Date"
            df.to_csv(filepath)
            print(f"  ✅ {ticker}: {len(df)}일 전체 다운로드")
            return True

        start_date = (datetime.strptime(last_date, "%Y-%m-%d") - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        etf = yf.Ticker(ticker)
        new_data = etf.history(start=start_date, auto_adjust=True)
        if new_data.empty:
            print(f"  ⚠️  {ticker}: 새 데이터 없음")
            return False

        new_data = new_data[["Open", "High", "Low", "Close", "Volume"]]
        new_data.index = new_data.index.strftime("%Y-%m-%d")
        new_data.index.name = "Date"
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


def fetch_ishares_shares(ticker):
    """
    iShares 공식 CSV에서 Shares Outstanding + NAV 히스토리 가져오기

    iShares CSV 구조:
      - 상단 N줄: 펀드명, ISIN, 설정일 등 메타데이터 (컬럼 수 불규칙)
      - 실제 데이터 헤더 행: "As Of Date", "Fund Name", "Shares Outstanding", "NAV", ...
      - 이후: 날짜별 데이터 행
    → pandas가 메타데이터 행에서 컬럼 수 불일치로 파싱 실패하므로
      헤더 행 위치를 먼저 찾고 그 행부터 파싱
    """
    product_id = ISHARES_PRODUCT_IDS.get(ticker)
    slug = ISHARES_SLUGS.get(ticker)
    if not product_id or not slug:
        return None

    url = (
        f"https://www.ishares.com/us/products/{product_id}/{slug}"
        f"/1467271812596.ajax?fileType=csv&fileName={ticker}_fund&dataType=fund"
    )

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()

        lines = resp.text.splitlines()

        # ── Step 1: 실제 데이터 헤더 행 찾기
        # "Shares Outstanding" 또는 "As Of" 가 포함된 첫 번째 행
        header_row = None
        for i, line in enumerate(lines):
            if "shares outstanding" in line.lower() or (
                "as of" in line.lower() and "nav" in line.lower()
            ):
                header_row = i
                break

        if header_row is None:
            # fallback: 컬럼이 5개 이상인 첫 번째 행
            for i, line in enumerate(lines):
                if line.count(",") >= 4:
                    header_row = i
                    break

        if header_row is None:
            print(f"  ⚠️  {ticker}: 헤더 행을 찾을 수 없음")
            return None

        # ── Step 2: 헤더 행부터만 파싱 (메타데이터 행 완전 스킵)
        csv_text = "\n".join(lines[header_row:])
        df = pd.read_csv(
            io.StringIO(csv_text),
            on_bad_lines="skip",   # 컬럼 수 불일치 행 무시
            thousands=",",         # 숫자에 콤마 포함된 경우 처리
        )
        df.columns = [str(c).strip() for c in df.columns]

        # ── Step 3: 필요한 컬럼 찾기
        date_col   = next((c for c in df.columns if "as of" in c.lower() or c.lower() == "date"), None)
        shares_col = next((c for c in df.columns if "shares outstanding" in c.lower()), None)
        nav_col    = next((c for c in df.columns if c.strip().upper() == "NAV"), None)

        if not date_col or not shares_col:
            print(f"  ⚠️  {ticker}: 필수 컬럼 없음. 컬럼 목록: {df.columns.tolist()[:10]}")
            return None

        # ── Step 4: 정리 및 반환
        keep = [date_col, shares_col] + ([nav_col] if nav_col else [])
        result = df[keep].copy()
        result.columns = ["Date", "shares_outstanding"] + (["nav"] if nav_col else [])

        # 숫자 정리 (콤마, 공백 제거)
        result["shares_outstanding"] = (
            result["shares_outstanding"]
            .astype(str).str.replace(",", "").str.strip()
        )
        result = result[result["shares_outstanding"].str.match(r"^\d+\.?\d*$")]
        result["shares_outstanding"] = result["shares_outstanding"].astype(float)

        result["Date"] = pd.to_datetime(result["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
        result = result.dropna(subset=["Date", "shares_outstanding"])
        result = result.set_index("Date").sort_index()

        return result

    except Exception as e:
        print(f"  ❌ {ticker} iShares fetch 실패: {e}")
        return None


def update_ishares_data(ticker):
    filepath = os.path.join(ISHARES_DIR, f"{ticker}_shares.csv")
    new_df = fetch_ishares_shares(ticker)
    if new_df is None or new_df.empty:
        return False

    if os.path.exists(filepath):
        existing = pd.read_csv(filepath, index_col="Date")
        combined = pd.concat([existing, new_df])
        combined = combined[~combined.index.duplicated(keep="last")]
        combined.sort_index(inplace=True)
    else:
        combined = new_df

    combined.to_csv(filepath)
    print(f"  ✅ {ticker}: {len(combined)}일 iShares 공식 데이터 저장")
    return True


def update_shares_snapshot():
    """非iShares ETF 일별 shares outstanding 스냅샷 (추정용)"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot_file = os.path.join(SHARES_DIR, "daily_shares.csv")

    if os.path.exists(snapshot_file):
        existing = pd.read_csv(snapshot_file, index_col=0)
    else:
        existing = pd.DataFrame()

    estimated_tickers = [t for t in ALL_TICKERS if t not in OFFICIAL_TICKERS]
    today_data = {}

    for ticker in estimated_tickers:
        try:
            etf = yf.Ticker(ticker)
            shares = etf.info.get("sharesOutstanding", None)
            if shares:
                today_data[ticker] = shares
        except Exception as e:
            print(f"  ❌ {ticker} shares: {e}")
        time.sleep(0.3)

    if not today_data:
        print("⚠️  Shares outstanding 스냅샷 수집 실패")
        return

    new_row = pd.DataFrame(today_data, index=[today])
    combined = pd.concat([existing, new_row])
    combined = combined[~combined.index.duplicated(keep="last")]
    combined.sort_index(inplace=True)
    combined.index.name = "Date"
    combined.to_csv(snapshot_file)
    print(f"✅ 추정 ETF Shares 스냅샷: {len(today_data)}개 ({today})")


def update_last_updated():
    meta_file = os.path.join(DATA_DIR, "meta", "etf_meta.json")
    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            meta = json.load(f)
        meta["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)


def main():
    for d in [PRICES_DIR, SHARES_DIR, ISHARES_DIR, os.path.join(DATA_DIR, "meta")]:
        os.makedirs(d, exist_ok=True)

    official  = [t for t in ALL_TICKERS if t in OFFICIAL_TICKERS]
    estimated = [t for t in ALL_TICKERS if t not in OFFICIAL_TICKERS]

    print("=" * 60)
    print("ETF 자금 레이더 — 일일 업데이트")
    print(f"시작: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"전체: {len(ALL_TICKERS)}개  |  공식: {len(official)}개  |  추정: {len(estimated)}개")
    print("=" * 60)

    # 1. 가격 데이터 (전체)
    print(f"\n📊 가격 데이터 업데이트")
    print("-" * 40)
    price_success, price_failed = 0, []
    for i, ticker in enumerate(ALL_TICKERS, 1):
        info = TICKER_INFO[ticker]
        badge = "[공식]" if info["official"] else "[추정]"
        print(f"[{i}/{len(ALL_TICKERS)}] {ticker} {badge} ({info['name_kr']})")
        if update_price_data(ticker):
            price_success += 1
        else:
            price_failed.append(ticker)
        time.sleep(0.5)

    print(f"\n가격 업데이트: {price_success}/{len(ALL_TICKERS)} 성공")
    if price_failed:
        print(f"실패: {price_failed}")

    # 2. iShares 공식 Shares Outstanding
    print(f"\n🏦 iShares 공식 Shares Outstanding 업데이트")
    print("-" * 40)
    ishares_success, ishares_failed = 0, []
    for i, ticker in enumerate(official, 1):
        print(f"[{i}/{len(official)}] {ticker}")
        if update_ishares_data(ticker):
            ishares_success += 1
        else:
            ishares_failed.append(ticker)
        time.sleep(1.5)  # iShares 서버 부하 방지

    print(f"\niShares 업데이트: {ishares_success}/{len(official)} 성공")
    if ishares_failed:
        print(f"실패: {ishares_failed}")

    # 3. 非iShares Shares 스냅샷
    print(f"\n📈 추정 ETF Shares Outstanding 스냅샷")
    print("-" * 40)
    update_shares_snapshot()

    # 4. 메타데이터
    update_last_updated()

    print("\n" + "=" * 60)
    print("✅ 일일 업데이트 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
