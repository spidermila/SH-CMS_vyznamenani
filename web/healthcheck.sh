#!/bin/sh
set -e

python -c "import sys,urllib.request; \
resp=urllib.request.urlopen('http://127.0.0.1:5000/', timeout=5); \
sys.exit(0 if 200 <= resp.status < 400 else 1)"
