#!/usr/bin/env python3
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Optional

VOLTAGE_RE = re.compile(r"VOLTAGE=(\d+(?:\.\d+)?)")


def load_config(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"Config parse error in {path}: {e}")
    return {
             "images_dir": "~/pictures",
             "order": "random",
             "low_threshold":  3.2,
             "plugged_in_threshold": 4.7,
             "last_image": None
           }


def read_voltage(battery_script: str) -> Optional[float]:
    try:
        out = subprocess.check_output(["bash", battery_script], text=True).strip()
        m = VOLTAGE_RE.search(out)
        return float(m.group(1)) if m else None
    except Exception:
        return None


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    cfg = load_config(base_dir / "config.json")
    battery_script = base_dir / "check_battery.sh"
    unplugged_threshold = cfg.get("plugged_in_threshold")

    misses = 0
    while misses < 3:
        v = read_voltage(battery_script)

        if v is not None and v <= unplugged_threshold:
            misses += 1
        else:
            misses = 0

        time.sleep(10)

    ts = subprocess.check_output(["date", "-Is"], text=True).strip()
    log_path = Path.home() / "eink_frame.log"
    with open(log_path, "a") as file:
        file.write(f"Power unplugged, shutting down - {ts}\n")

    subprocess.run(["bash", "-lc", "cd $HOME/wittypi && ./runScript.sh"], check=False)
    subprocess.run(["sudo", "/sbin/shutdown", "-h", "now"], check=False)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
