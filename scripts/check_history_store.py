import os
import sys
import tempfile
from datetime import date, timedelta

os.environ.setdefault("REGIME_METHOD", "absolute")
os.environ.setdefault("PHASE_2_THRESHOLD", "2.0")
os.environ.setdefault("PHASE_2_EXIT_THRESHOLD", "1.5")
os.environ.setdefault("PHASE_3_THRESHOLD", "4.0")
os.environ.setdefault("PHASE_3_EXIT_THRESHOLD", "3.0")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import history_store


def write_scores(db_path, scores):
    history_store.ensure_db(db_path)
    start_date = date(2026, 1, 1)
    for offset, score in enumerate(scores):
        day = (start_date + timedelta(days=offset)).isoformat()
        snapshot = {
            "date": day,
            "run_ts": f"{day}T12:00:00",
            "event": "NORMAL",
            "stress_score": score,
            "stress_level": "Test",
            "phase_daily": history_store.phase_from_score(score),
            "phase_score": float(score),
            "regime_phase": None,
            "regime_score": None,
            "regime_trend": None,
            "regime_confidence": None,
            "spx": 0,
            "vix": 0,
            "spread": 0,
            "us10y": 0,
            "dxy": 0,
            "net_liq_b": 0,
            "gold": 0,
            "btc": 0,
            "triggers": "",
            "reason": "Test",
        }
        history_store.upsert_daily_snapshot(db_path, snapshot)


def test_low_stress_regime():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "history.db")
        scores = [1] * 10
        write_scores(db_path, scores)
        history = history_store.fetch_recent_history(db_path, 10)
        regime = history_store.compute_regime(history, window_days=7, trend_days=3, min_days=5)

        if regime["regime_phase"] != "Fase 1 - AUGE":
            raise AssertionError("Expected Phase 1 regime for low stress history")
        if regime["regime_trend"] != "Estable":
            raise AssertionError("Expected stable trend for flat scores")


def test_rising_stress_trend():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "history.db")
        scores = [1, 1, 2, 3, 4, 4, 4, 5, 5, 5]
        write_scores(db_path, scores)
        history = history_store.fetch_recent_history(db_path, 10)
        regime = history_store.compute_regime(history, window_days=7, trend_days=3, min_days=5)

        if regime["regime_phase"] != "Fase 3 - QUIEBRE":
            raise AssertionError("Expected Phase 3 regime for sustained high stress")
        if regime["regime_trend"] != "Ascendente":
            raise AssertionError("Expected rising trend for increasing scores")


def main():
    test_low_stress_regime()
    test_rising_stress_trend()
    print("OK: History store regime checks passed.")


if __name__ == "__main__":
    main()
