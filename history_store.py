import base64
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import requests

DEFAULT_DB_PATH = os.environ.get("HISTORY_DB_PATH", os.path.join("output", "history.db"))
DEFAULT_GIST_FILENAME = os.environ.get("HISTORY_GIST_FILENAME", "history.db.b64")
DEFAULT_CALIBRATION_PATH = os.environ.get("REGIME_CALIBRATION_PATH", os.path.join("output", "regime_calibration.json"))

COLUMNS = [
    "date",
    "run_ts",
    "event",
    "stress_score",
    "stress_level",
    "phase_daily",
    "phase_score",
    "regime_phase",
    "regime_score",
    "regime_trend",
    "regime_confidence",
    "spx",
    "vix",
    "spread",
    "us10y",
    "dxy",
    "net_liq_b",
    "gold",
    "btc",
    "triggers",
    "reason",
]


def get_db_path():
    return os.environ.get("HISTORY_DB_PATH", DEFAULT_DB_PATH)


def get_gist_filename():
    return os.environ.get("HISTORY_GIST_FILENAME", DEFAULT_GIST_FILENAME)


def ensure_db(db_path):
    directory = os.path.dirname(db_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                date TEXT PRIMARY KEY,
                run_ts TEXT NOT NULL,
                event TEXT,
                stress_score INTEGER,
                stress_level TEXT,
                phase_daily TEXT,
                phase_score REAL,
                regime_phase TEXT,
                regime_score REAL,
                regime_trend TEXT,
                regime_confidence TEXT,
                spx REAL,
                vix REAL,
                spread REAL,
                us10y REAL,
                dxy REAL,
                net_liq_b REAL,
                gold REAL,
                btc REAL,
                triggers TEXT,
                reason TEXT
            )
            """
        )
        conn.commit()


def load_db_from_gist(gist_token, gist_id, db_path, gist_filename=None):
    if not gist_token or not gist_id:
        return False

    filename = gist_filename or get_gist_filename()
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {"Authorization": f"token {gist_token}"}

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        gist_data = response.json()
        file_entry = gist_data.get("files", {}).get(filename)
        if not file_entry or not file_entry.get("content"):
            return False
        if file_entry.get("truncated"):
            print("History gist content truncated; skipping load.")
            return False

        payload = base64.b64decode(file_entry["content"].encode("utf-8"))
        directory = os.path.dirname(db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(db_path, "wb") as handle:
            handle.write(payload)
        return True
    except Exception as exc:
        print(f"History gist load failed: {exc}")
        return False


def save_db_to_gist(gist_token, gist_id, db_path, gist_filename=None):
    if not gist_token or not gist_id:
        return False

    if not os.path.exists(db_path):
        return False

    filename = gist_filename or get_gist_filename()
    try:
        with open(db_path, "rb") as handle:
            encoded = base64.b64encode(handle.read()).decode("utf-8")

        url = f"https://api.github.com/gists/{gist_id}"
        headers = {"Authorization": f"token {gist_token}"}
        payload = {"files": {filename: {"content": encoded}}}
        response = requests.patch(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return True
    except Exception as exc:
        print(f"History gist save failed: {exc}")
        return False


def upsert_daily_snapshot(db_path, snapshot):
    columns = ", ".join(COLUMNS)
    placeholders = ", ".join(["?"] * len(COLUMNS))
    updates = ", ".join([f"{col}=excluded.{col}" for col in COLUMNS if col != "date"])

    values = [snapshot.get(col) for col in COLUMNS]

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            f"""
            INSERT INTO daily_snapshots ({columns})
            VALUES ({placeholders})
            ON CONFLICT(date) DO UPDATE SET {updates}
            """,
            values,
        )
        conn.commit()


def update_regime_fields(db_path, date_str, regime):
    if not regime:
        return

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE daily_snapshots
            SET regime_phase = ?,
                regime_score = ?,
                regime_trend = ?,
                regime_confidence = ?
            WHERE date = ?
            """,
            (
                regime.get("regime_phase"),
                regime.get("regime_score"),
                regime.get("regime_trend"),
                regime.get("regime_confidence"),
                date_str,
            ),
        )
        conn.commit()


def fetch_recent_history(db_path, limit):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM daily_snapshots ORDER BY date DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]


def fetch_history(db_path):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM daily_snapshots ORDER BY date ASC"
        ).fetchall()

    return [dict(row) for row in rows]


def prune_history(db_path, retention_days):
    if retention_days <= 0:
        return

    cutoff = (datetime.now(timezone.utc).date() - timedelta(days=retention_days)).isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM daily_snapshots WHERE date < ?", (cutoff,))
        conn.commit()


def _get_float_env(name, default):
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return float(default)


def _get_int_env(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return int(default)


def _normalise_thresholds(enter_value, exit_value):
    if exit_value is None:
        return enter_value, enter_value
    if exit_value > enter_value:
        return enter_value, enter_value
    return enter_value, exit_value


def _get_regime_thresholds():
    phase2_enter, phase2_exit = _normalise_thresholds(
        _get_float_env("PHASE_2_THRESHOLD", "2.0"),
        _get_float_env("PHASE_2_EXIT_THRESHOLD", "1.5"),
    )
    phase3_enter, phase3_exit = _normalise_thresholds(
        _get_float_env("PHASE_3_THRESHOLD", "4.0"),
        _get_float_env("PHASE_3_EXIT_THRESHOLD", "3.0"),
    )

    z_phase2_enter, z_phase2_exit = _normalise_thresholds(
        _get_float_env("REGIME_Z_PHASE2_ENTER", "0.25"),
        _get_float_env("REGIME_Z_PHASE2_EXIT", "0.0"),
    )
    z_phase3_enter, z_phase3_exit = _normalise_thresholds(
        _get_float_env("REGIME_Z_PHASE3_ENTER", "1.0"),
        _get_float_env("REGIME_Z_PHASE3_EXIT", "0.6"),
    )

    p_phase2_enter, p_phase2_exit = _normalise_thresholds(
        _get_float_env("REGIME_PCT_PHASE2_ENTER", "60"),
        _get_float_env("REGIME_PCT_PHASE2_EXIT", "50"),
    )
    p_phase3_enter, p_phase3_exit = _normalise_thresholds(
        _get_float_env("REGIME_PCT_PHASE3_ENTER", "85"),
        _get_float_env("REGIME_PCT_PHASE3_EXIT", "70"),
    )

    return {
        "absolute": {
            "phase2_enter": phase2_enter,
            "phase2_exit": phase2_exit,
            "phase3_enter": phase3_enter,
            "phase3_exit": phase3_exit,
        },
        "zscore": {
            "phase2_enter": z_phase2_enter,
            "phase2_exit": z_phase2_exit,
            "phase3_enter": z_phase3_enter,
            "phase3_exit": z_phase3_exit,
        },
        "percentile": {
            "phase2_enter": p_phase2_enter,
            "phase2_exit": p_phase2_exit,
            "phase3_enter": p_phase3_enter,
            "phase3_exit": p_phase3_exit,
        },
    }


def _load_calibration(path):
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return None

    if not isinstance(payload, dict):
        return None

    value_type = payload.get("value_type")
    thresholds = {
        "phase2_enter": payload.get("phase2_enter"),
        "phase2_exit": payload.get("phase2_exit"),
        "phase3_enter": payload.get("phase3_enter"),
        "phase3_exit": payload.get("phase3_exit"),
    }

    if value_type not in {"absolute", "zscore", "percentile"}:
        return None
    if any(v is None for v in thresholds.values()):
        return None

    phase2_enter, phase2_exit = _normalise_thresholds(
        float(thresholds["phase2_enter"]), float(thresholds["phase2_exit"])
    )
    phase3_enter, phase3_exit = _normalise_thresholds(
        float(thresholds["phase3_enter"]), float(thresholds["phase3_exit"])
    )

    return {
        "value_type": value_type,
        "thresholds": {
            "phase2_enter": phase2_enter,
            "phase2_exit": phase2_exit,
            "phase3_enter": phase3_enter,
            "phase3_exit": phase3_exit,
        },
    }


def phase_from_score(score):
    thresholds = _get_regime_thresholds()["absolute"]
    if score is None:
        return "Fase desconocida"
    if score >= thresholds["phase3_enter"]:
        return "Fase 3 - QUIEBRE"
    if score >= thresholds["phase2_enter"]:
        return "Fase 2 - ESPECULACIÓN"
    return "Fase 1 - AUGE"


def _apply_hysteresis(value, previous_phase, thresholds):
    if value is None:
        return previous_phase or "Fase desconocida"

    if previous_phase == "Fase 3 - QUIEBRE":
        if value < thresholds["phase3_exit"]:
            if value >= thresholds["phase2_enter"]:
                return "Fase 2 - ESPECULACIÓN"
            return "Fase 1 - AUGE"
        return previous_phase

    if previous_phase == "Fase 2 - ESPECULACIÓN":
        if value >= thresholds["phase3_enter"]:
            return "Fase 3 - QUIEBRE"
        if value < thresholds["phase2_exit"]:
            return "Fase 1 - AUGE"
        return previous_phase

    if value >= thresholds["phase3_enter"]:
        return "Fase 3 - QUIEBRE"
    if value >= thresholds["phase2_enter"]:
        return "Fase 2 - ESPECULACIÓN"
    return "Fase 1 - AUGE"


def _percentile_rank(values, current_value):
    if not values:
        return None
    count = sum(1 for v in values if v < current_value)
    return (count / len(values)) * 100


def _select_regime_method(scores):
    method = os.environ.get("REGIME_METHOD", "auto").lower()
    if method != "auto":
        return method

    calibration = _load_calibration(DEFAULT_CALIBRATION_PATH)
    if calibration:
        return "calibrated"

    z_min = _get_int_env("REGIME_AUTO_Z_MIN_SAMPLES", "90")
    pct_min = _get_int_env("REGIME_AUTO_PCT_MIN_SAMPLES", "180")

    if len(scores) >= pct_min:
        return "percentile"
    if len(scores) >= z_min:
        return "zscore"
    return "absolute"


def compute_regime(history_rows, window_days, trend_days, min_days):
    scores = [row.get("phase_score") for row in history_rows if row.get("phase_score") is not None]
    if not scores:
        return {
            "regime_phase": None,
            "regime_score": None,
            "regime_trend": None,
            "regime_confidence": "Baja",
            "regime_window_days": window_days,
            "regime_trend_score": None,
            "regime_method": None,
        }

    window_scores = scores[-window_days:] if window_days > 0 else scores
    regime_score = sum(window_scores) / len(window_scores)

    previous_phase = None
    for row in reversed(history_rows):
        if row.get("regime_phase"):
            previous_phase = row.get("regime_phase")
            break
    if not previous_phase and scores:
        previous_phase = phase_from_score(scores[-1])

    method = _select_regime_method(scores)
    thresholds = _get_regime_thresholds()
    regime_value = None
    method_thresholds = thresholds["absolute"]

    if method == "calibrated":
        calibration = _load_calibration(DEFAULT_CALIBRATION_PATH)
        if calibration:
            method = calibration["value_type"]
            method_thresholds = calibration["thresholds"]
        else:
            method = "absolute"

    if method == "zscore":
        lookback = _get_int_env("REGIME_Z_LOOKBACK", "180")
        sample = scores[-lookback:] if lookback > 0 else scores
        mean = sum(sample) / len(sample)
        variance = sum((x - mean) ** 2 for x in sample) / len(sample)
        std = variance ** 0.5
        if std > 0:
            regime_value = (regime_score - mean) / std
            method_thresholds = thresholds["zscore"]
        else:
            method = "absolute"

    if method == "percentile":
        lookback = _get_int_env("REGIME_PCT_LOOKBACK", "180")
        sample = scores[-lookback:] if lookback > 0 else scores
        regime_value = _percentile_rank(sample, regime_score)
        method_thresholds = thresholds["percentile"]

    if method == "absolute":
        regime_value = regime_score
        method_thresholds = thresholds["absolute"]

    regime_phase = _apply_hysteresis(regime_value, previous_phase, method_thresholds)

    confidence = "Alta" if len(window_scores) >= min_days else "Baja"
    if method == "zscore":
        z_min = _get_int_env("REGIME_AUTO_Z_MIN_SAMPLES", "90")
        if len(scores) < z_min:
            confidence = "Baja"
    if method == "percentile":
        pct_min = _get_int_env("REGIME_AUTO_PCT_MIN_SAMPLES", "180")
        if len(scores) < pct_min:
            confidence = "Baja"

    trend = "Estable"
    trend_score = None
    if trend_days > 0 and len(scores) >= trend_days * 2:
        recent = scores[-trend_days:]
        previous = scores[-(trend_days * 2):-trend_days]
        if previous:
            trend_score = (sum(recent) / len(recent)) - (sum(previous) / len(previous))
            if trend_score >= 0.5:
                trend = "Ascendente"
            elif trend_score <= -0.5:
                trend = "Descendente"

    return {
        "regime_phase": regime_phase,
        "regime_score": round(regime_score, 2),
        "regime_trend": trend,
        "regime_confidence": confidence,
        "regime_window_days": window_days,
        "regime_trend_score": None if trend_score is None else round(trend_score, 2),
        "regime_method": method,
        "regime_value": None if regime_value is None else round(regime_value, 2),
    }
