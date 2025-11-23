#!/usr/bin/env bash
set -e
MYPID=$$
echo "mypid=$MYPID"
echo "=== matching processes ==="
ps -eo pid,cmd | grep "[K]risBot.py" || true
PIDS=$(ps -eo pid,cmd | grep "[K]risBot.py" | awk '{print $1}' | grep -v "^$MYPID$" || true)
echo "PIDS=[$PIDS]"
if [ -n "$PIDS" ]; then
  for p in $PIDS; do
    echo "killing $p"
    kill -TERM $p 2>/dev/null || kill -KILL $p 2>/dev/null || true
  done
fi
sleep 1
echo "=== processes after kill ==="
ps -eo pid,cmd | grep "[K]risBot.py" || true

echo "=== Run local search test ==="
/home/login/Downloads/Annon/.venv/bin/python /home/login/Downloads/Annon/test_search_local.py || true

echo "=== user_data.json (tail) ==="
tail -n 200 user_data.json || true
