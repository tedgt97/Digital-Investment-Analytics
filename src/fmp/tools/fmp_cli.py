import argparse
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd
from fmp.client import FMPClient  # --Fixed--

def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding='utf-8')

def save_df(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

def main():
    p = argparse.ArgumentParser(description='FMP data fetch CLI')
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--out", default="data/raw", help="output root dir")

    p_quote = sub.add_parser("quote", parents=[common])
    p_quote.add_argument("--symbol", required=True)

    p_chart = sub.add_parser("chart", parents=[common])
    p_chart.add_argument("--symbol", required=True)
    p_chart.add_argument("--from", dest="start", required=True)
    p_chart.add_argument("--to", dest="end", required=True)

    p_income = sub.add_parser("income", parents=[common])
    p_income.add_argument("--symbol", required=True)
    p_income.add_argument("--period", choices=["annual", "quarter"], default="annual")
    p_income.add_argument("--limit", type=int, default=5)

    p_profile = sub.add_parser("profile", parents=[common])
    p_profile.add_argument("--symbol", required=True)

    args = p.parse_args()
    client = FMPClient(verbose=False)
    out_root = Path(args.out)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    if args.cmd == "quote":
        data = client.get_quote(args.symbol)
        save_json(data, out_root / "quote" / args.symbol / f"{ts}.json")
        print("saved quote")

    elif args.cmd == "chart":
        df = client.get_chart(args.symbol, args.start, args.end)
        save_df(df, out_root / "chart" / args.symbol / f"{args.start}_{args.end}.parquet")
        print(f"saved chart rows={len(df)}")
    
    elif args.cmd == "income":
        df = client.get_income_statement(args.symbol, args.period, args.limit)
        save_df(df, out_root / "income-statement" / args.symbol / f"{args.period}_{ts}.parquet")
        print(f"saved income rows={len(df)}")
    
    elif args.cmd == "profile":
        data = client.get_company_profile(args.symbol)
        save_json(data, out_root / "profile" / args.symbol / f"{ts}.json")
        print("saved profile")

if __name__ == "__main__":
    main()

