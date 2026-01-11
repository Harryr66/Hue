#!/bin/bash
# Unset environment variables that might override .env file
unset GROK_API_KEY
unset SERPAPI_KEY
echo "✅ Unset GROK_API_KEY and SERPAPI_KEY"
echo "Now run: python3 test_grok_api.py"
