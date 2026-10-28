#!/usr/bin/env bash
# Save the live SLAM map to <package>/maps/<name>.{yaml,pgm}.
# Usage: ./save_map.sh [map_name]          (default: obstacle_arena)
# Env:   TB3_WS=/path/to/tb3_autonomous_ws  (default: $HOME/tb3_autonomous_ws)
set -eo pipefail

NAME="${1:-obstacle_arena}"
WS="${TB3_WS:-$HOME/tb3_autonomous_ws}"
SRC_MAPS="$WS/src/tb3_autonomous/maps"
mkdir -p "$SRC_MAPS"

echo ">> Saving /map to $SRC_MAPS/$NAME.{yaml,pgm}"
ros2 run nav2_map_server map_saver_cli -f "$SRC_MAPS/$NAME" \
  --ros-args -p use_sim_time:=true -p save_map_timeout:=10.0

# Also copy into the installed share dir so navigation.launch.py finds it without a rebuild.
if PREFIX="$(ros2 pkg prefix tb3_autonomous 2>/dev/null)"; then
  DEST="$PREFIX/share/tb3_autonomous/maps"
  mkdir -p "$DEST"
  cp -f "$SRC_MAPS/$NAME.yaml" "$SRC_MAPS/$NAME.pgm" "$DEST/" 2>/dev/null || true
  echo ">> Copied to $DEST"
fi
echo ">> Done. Verify with: ros2 launch tb3_autonomous navigation.launch.py"
