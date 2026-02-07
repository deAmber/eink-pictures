#!/bin/bash
set -euo pipefail

LOG="$HOME/eink_pictures.log"
exec >>"$LOG" 2>&1
echo "---- $(date -Is) boot cycle start ----"

WITTYPIDIR="$HOME/wittypi"

echo "---- $(date -Is) boot cycle start ----"

# Run the manager to update the display
python "$HOME"/eink-pictures/manager.py 2>&1
RC=${PIPESTATUS[0]}
echo "manager.py exit code: $RC"

# Check if on Battery
PLUGGED=$(python3 - <<'PY'
import json, re, subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

cfg_path = BASE_DIR / "config.json"
cfg = {}
if cfg_path.exists():
    try: cfg = json.loads(cfg_path.read_text())
    except: pass

bat = str(Path(BASE_DIR / "check_battery.sh").expanduser())
plug_th = float(cfg.get("plugged_in_threshold", 4.7))

try:
    out = subprocess.check_output(["bash", bat], text=True).strip()
    m = re.search(r"VOLTAGE=(\d+(?:\.\d+)?)", out)
    v = float(m.group(1)) if m else None
except Exception:
    v = None

print("1" if (v is not None and v >= plug_th) else "0")
PY
)

# If plugged in start the watcher to wait for being unplugged
if [ "$PLUGGED" = "1" ]; then
  echo "External power detected (by voltage). Not shutting down."
  echo "Starting unplug watcher..."
  UNIT="eink-power-watch@$(id -un).service"
  sudo systemctl start --no-block "$UNIT" || echo "FAILED to queue start for $UNIT"
  exit 0
fi

# Give logs time to flush, then power off
echo "---- $(data -Is) on battery (by voltage). Shutting down now. ----"

# Schedule NEXT BOOT via WittyPi (schedule.wpi should use WAIT)
if [ -x "$WITTYPIDIR/runScript.sh" ]; then
  echo "Running WittyPi runScript.sh to schedule next startup..."
  (cd "$WITTYPIDIR" && ./runScript.sh) 2>&1
else
  echo "WARNING: WittyPi runScript.sh not found or not executable at $WITTYPIDIR/runScript.sh"
fi

sync
sleep 2
sudo /sbin/shutdown -h now