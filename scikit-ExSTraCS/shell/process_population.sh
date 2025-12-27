#!/usr/bin/env bash
set -euo pipefail

# Path to the Python interpreter (your conda env)
PY="python"

# Path to the script
SCRIPT="../utils/ProcessPopulation.py"

# Optional: logs directory
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

# Loop index from 0 to 9 (ten runs)
for i in $(seq 0 9); do
  # Args: index dataset
  echo "start \"$SCRIPT\" $i"

  #nohup "$PY" "$SCRIPT" "$i" mpr6 > "${LOG_DIR}/processpop_mpr6_run${i}.log" 2>&1 &

  # Uncomment below if you want to run other datasets too
  # nohup "$PY" "$SCRIPT" "$i" mpr11  > "${LOG_DIR}/processpop_mpr11_run${i}.log" 2>&1 &
  nohup "$PY" "$SCRIPT" "$i" mpr20  > "${LOG_DIR}/processpop_mpr20_run${i}.log" 2>&1 &
  # nohup "$PY" "$SCRIPT" "$i" mpr37  > "${LOG_DIR}/processpop_mpr37_run${i}.log" 2>&1 &
  # nohup "$PY" "$SCRIPT" "$i" mpr70  > "${LOG_DIR}/processpop_mpr70_run${i}.log" 2>&1 &
  # nohup "$PY" "$SCRIPT" "$i" mpr135 > "${LOG_DIR}/processpop_mpr135_run${i}.log" 2>&1 &
done

echo "All jobs started in background."
echo "Check logs in: $LOG_DIR"
