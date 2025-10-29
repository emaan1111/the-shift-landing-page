#!/usr/bin/env python3
"""
Simple script to run the Flask server on a custom port
Usage: python3 run_local.py [port]
Default port: 5001
"""
import sys
import os

# Get port from command line or use default
port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001

# Read server.py and modify the port
with open('server.py', 'r') as f:
    code = f.read()
    
# Replace the app.run line to use our port and disable debug mode's reloader
code = code.replace(
    "app.run(host='0.0.0.0', port=5000, debug=True)",
    f"app.run(host='0.0.0.0', port={port}, debug=True, use_reloader=False)"
)

# Execute the modified code
exec(code)
