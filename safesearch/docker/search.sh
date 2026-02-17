#!/bin/sh
set -e

QUERY="$*"
if [ -z "$QUERY" ]; then
  echo "Usage: search.sh <query>"
  exit 1
fi

ENCODED=$(python3 -c "import sys,urllib.parse; print(urllib.parse.quote_plus(sys.argv[1]))" "$QUERY")

# Always use lite.duckduckgo.com with Lynx user agent
HTML=$(curl -sL \
  -A "Lynx/2.9.2" \
  -H "Accept: text/html" \
  -d "q=${ENCODED}" \
  --max-time 20 \
  "https://lite.duckduckgo.com/lite/" 2>/dev/null)

if [ -z "$HTML" ]; then
  echo "ERROR: No response from search engine"
  exit 1
fi

# Check for CAPTCHA/bot detection
if echo "$HTML" | grep -q "anomaly-modal\|botnet\|challenge-form"; then
  echo "ERROR: Search engine is blocking automated requests from this IP."
  echo "This may happen with frequent queries. Try again later."
  exit 1
fi

echo "$HTML" | python3 /usr/local/bin/parse_results.py
