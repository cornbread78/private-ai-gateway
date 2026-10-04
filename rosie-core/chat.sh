#!/bin/bash

# Gateway configuration
GATEWAY_URL="http://127.0.0.1:8080/chat"
NAME="Rosie"

if [ -n "$1" ]; then
  NAME="$1"
fi

echo "============================================================"
echo "=== Voice-Enabled Gateway Interactive Terminal Chat ==="
echo "Current AI Name: $NAME"
echo "Commands: /v or /voice (speech input), /reset (clear memory), /history (view db), /exit (quit)"
echo "============================================================"

while true; do
  echo ""
  read -p "You > " USER_INPUT

  # Handle exit
  if [[ "$USER_INPUT" == "/exit" ]]; then
    echo "Exiting chat."
    break
  fi

  # Handle memory reset
  if [[ "$USER_INPUT" == "/reset" ]]; then
    curl -s -X POST "http://127.0.0.1:8080/reset"
    echo "Memory cleared!"
    continue
  fi

  # Handle history
  if [[ "$USER_INPUT" == "/history" ]]; then
    curl -s http://127.0.0.1:8080/history
    echo ""
    continue
  fi

  # Handle Voice Mode
  if [[ "$USER_INPUT" == "/v" ]] || [[ "$USER_INPUT" == "/voice" ]]; then
    echo "[Listening...] Speak now into your microphone..."
    USER_INPUT=$(termux-speech-to-text)
    if [ -z "$USER_INPUT" ]; then
      echo "[Voice Error] No speech detected."
      continue
    fi
    echo "You (Spoken) > $USER_INPUT"
  fi

  if [ -z "$USER_INPUT" ]; then
    continue
  fi

  # Send prompt payload to Gateway
  RESPONSE=$(curl -s -X POST "$GATEWAY_URL" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$USER_INPUT\"}")

  # Parse JSON response content
  BOT_REPLY=$(echo "$RESPONSE" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    if "choices" in data and len(data["choices"]) > 0:
        print(data["choices"][0]["message"]["content"])
    else:
        print("No response from assistant.")
except Exception as e:
    print("Error parsing response.")
')

  echo -e "\n$NAME >\n$BOT_REPLY\n"

  # Speak output out loud
  if [ -n "$BOT_REPLY" ]; then
    # Filter out code blocks before sending to text-to-speech engine
    CLEAN_TTS=$(echo "$BOT_REPLY" | sed '/```/,/```/d')
    if [ -n "$CLEAN_TTS" ]; then
      echo "$CLEAN_TTS" | termux-tts-speak &
    fi
  fi

done
