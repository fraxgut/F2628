import argparse
import ast
import csv
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


ANALYSIS_PATTERN = re.compile(r"Analysis Result: (\{.*\})")
NP_FLOAT_PATTERN = re.compile(r"np\.float64\(([^)]+)\)")


def run_command(args):
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"Command failed: {' '.join(args)}")
    return proc.stdout


def load_runs(repo):
    raw = run_command(
        [
            "gh",
            "api",
            f"/repos/{repo}/actions/runs?per_page=100",
            "--paginate",
        ]
    )
    pages = []
    decoder = json.JSONDecoder()
    idx = 0
    text = raw.strip()
    while idx < len(text):
        obj, offset = decoder.raw_decode(text, idx)
        pages.append(obj)
        idx = offset
        while idx < len(text) and text[idx].isspace():
            idx += 1
    runs = []
    for page in pages:
        runs.extend(page.get("workflow_runs", []))
    return runs


def latest_run_per_day(runs, since_date, until_date):
    selected = {}
    for run in runs:
        started = run.get("run_started_at")
        if not started:
            continue
        run_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
        run_date = run_dt.date()
        if run_date < since_date or run_date > until_date:
            continue
        key = run_date.isoformat()
        current = selected.get(key)
        if current is None or started > current.get("run_started_at", ""):
            selected[key] = run
    return [selected[k] for k in sorted(selected)]


def parse_analysis_from_log(log_text):
    match = ANALYSIS_PATTERN.search(log_text)
    if not match:
        return None
    payload = NP_FLOAT_PATTERN.sub(r"\1", match.group(1))
    try:
        return ast.literal_eval(payload)
    except Exception:
        return None


def collect_truth_rows(repo, runs):
    rows = []
    for run in runs:
        run_id = run.get("id")
        if run_id is None:
            continue
        run_date = run.get("run_started_at", "")[:10]
        try:
            log_text = run_command(
                [
                    "gh",
                    "run",
                    "view",
                    str(run_id),
                    "--repo",
                    repo,
                    "--log",
                ]
            )
        except RuntimeError:
            continue

        analysis = parse_analysis_from_log(log_text)
        if not analysis:
            continue

        rows.append(
            {
                "date": run_date,
                "run_id": run_id,
                "run_started_at": run.get("run_started_at"),
                "event": analysis.get("event"),
                "stress_score": analysis.get("stress_score"),
                "stress_level": analysis.get("stress_level"),
                "cycle_phase": analysis.get("cycle_phase"),
                "cycle_trend": analysis.get("cycle_trend"),
                "cycle_confidence": analysis.get("cycle_confidence"),
                "cycle_pressure": analysis.get("cycle_pressure"),
                "cycle_spec": analysis.get("cycle_spec"),
                "cycle_index": analysis.get("cycle_index"),
                "cycle_break_risk": analysis.get("cycle_break_risk"),
                "cycle_near_break": analysis.get("cycle_near_break"),
                "regime_phase": analysis.get("regime_phase"),
                "regime_score": analysis.get("regime_score"),
                "regime_trend": analysis.get("regime_trend"),
                "regime_confidence": analysis.get("regime_confidence"),
                "risk_daily_label": analysis.get("risk_daily_label"),
                "reason": analysis.get("reason"),
            }
        )
    return rows


def write_csv(rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "date",
        "run_id",
        "run_started_at",
        "event",
        "stress_score",
        "stress_level",
        "cycle_phase",
        "cycle_trend",
        "cycle_confidence",
        "cycle_pressure",
        "cycle_spec",
        "cycle_index",
        "cycle_break_risk",
        "cycle_near_break",
        "regime_phase",
        "regime_score",
        "regime_trend",
        "regime_confidence",
        "risk_daily_label",
        "reason",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(description="Export canonical run truth from GitHub Actions logs.")
    parser.add_argument("--repo", default="fraxgut/F2628", help="GitHub repo in owner/name format.")
    parser.add_argument("--since", required=True, help="Start date (YYYY-MM-DD).")
    parser.add_argument("--until", help="End date (YYYY-MM-DD). Defaults to today (UTC).")
    parser.add_argument(
        "--output",
        help="Output CSV path. Defaults to output/runs_truth_<since>_<until>.csv",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    since = datetime.strptime(args.since, "%Y-%m-%d").date()
    until = (
        datetime.strptime(args.until, "%Y-%m-%d").date()
        if args.until
        else datetime.utcnow().date()
    )
    if until < since:
        raise ValueError("--until must be >= --since")

    runs = load_runs(args.repo)
    latest_runs = latest_run_per_day(runs, since, until)
    rows = collect_truth_rows(args.repo, latest_runs)

    output = (
        Path(args.output)
        if args.output
        else Path("output") / f"runs_truth_{since.isoformat()}_{until.isoformat()}.csv"
    )
    write_csv(rows, output)
    print(f"Wrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()
