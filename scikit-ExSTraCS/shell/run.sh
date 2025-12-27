#!/usr/bin/env bash
set -euo pipefail

# Path to the Python interpreter (your python env)
PY="python"

# Path to the training script
SCRIPT="../test/test_ExSTraCS_CMD.py"

# use transfer learning (1) or not (0)
USE_TL=1

# Optional: logs directory
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

# Loop index from 0 to 9 (10 runs)
for i in $(seq 0 9); do
  # Args: index dataset learning_iterations N p_spec level use_tl(transfer learning)
  echo "start \"$PY\" \"$SCRIPT\" $i"
  # Uncomment below if you want to run other datasets too

  #nohup "$PY" "$SCRIPT" "$i" mpr6 100000 500 0.66 1 "$USE_TL" > "${LOG_DIR}/mpr6_run${i}.log" 2>&1 &
  #nohup "$PY" "$SCRIPT" "$i" mpr11  100000  1000  0.66 2 "$USE_TL" > "${LOG_DIR}/mpr11_run${i}.log" 2>&1 &
  #nohup "$PY" "$SCRIPT" "$i" mpr20  100000  2000  0.66 3 "$USE_TL" > "${LOG_DIR}/mpr20_run${i}.log" 2>&1 &
  nohup "$PY" "$SCRIPT" "$i" mpr37  1000000 10000 0.5  4 "$USE_TL" > "${LOG_DIR}/mpr37_run${i}.log" 2>&1 &
  # nohup "$PY" "$SCRIPT" "$i" mpr70  2000000 20000 0.5  5 "$USE_TL" > "${LOG_DIR}/mpr70_run${i}.log" 2>&1 &
  # nohup "$PY" "$SCRIPT" "$i" mpr135 3000000 50000 0.5  6 "$USE_TL" > "${LOG_DIR}/mpr135_run${i}.log" 2>&1 &
done

echo "All jobs started in background."
echo "Check logs in: $LOG_DIR"
