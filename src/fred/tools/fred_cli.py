import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd

from fred.client import FREDClient

def save_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

def save_df(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

def main():
    parser = argparse.ArgumentParser(description="FRED data fetch CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--out", default="data/raw", help="output root dir")

    p_series = sub.add_parser(
        "series",
        parents=[common],
        help="fetch FRED series metadata",
    )
    p_series.add_argument("--id", dest="series_id", required=True, help="FRED series id")

    p_observations = sub.add_parser(
        "observations",
        parents=[common],
        help="fetch FRED series observations",
    )
    p_observations.add_argument("--id", dest="series_id", required=True, help="FRED series id")
    p_observations.add_argument("--from", dest="start", required=True, help="start date YYYY-MM-DD")
    p_observations.add_argument("--to", dest="end", required=False, help="end date YYYY-MM-DD (default: latest available)")
    p_observations.add_argument(
        "--frequency",
        choices=["d", "w", "bw", "m", "q", "sa", "a"],
        help="optional FRED frequency",
    )
    p_observations.add_argument(
        "--aggregation",
        dest="aggregation_method",
        choices=["avg", "sum", "eop"],
        help="optional aggregation method",
    )

    args = parser.parse_args()
    client = FREDClient(verbose=False)
    out_root = Path(args.out)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")

    if args.cmd == "series":
        data = client.get_series(args.series_id)
        save_json(data, out_root / "fred-series" / args.series_id / f"{ts}.json")
        print("saved series metadata")

    elif args.cmd == "observations":
        df = client.get_series_observations(
            args.series_id,
            args.start,
            args.end,
            args.frequency,
            args.aggregation_method,
        )
        end_label = args.end or df["date"].max().date().isoformat()
        save_df(
            df,
            out_root / "fred-observations" / args.series_id / f"{args.start}_{end_label}.parquet",
        )
        print(f"saved observations rows = {len(df)}")

if __name__ == "__main__":
    main()