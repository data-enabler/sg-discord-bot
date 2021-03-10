#!/usr/bin/env bash
while true; do
  pipenv run python main.py
  echo "Script exited with code $?, restarting in 5 seconds..."
  sleep 5
done
