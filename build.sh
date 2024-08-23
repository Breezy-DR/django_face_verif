#!/bin/bash
# Install build-essential and Python dev tools
apt-get update && apt-get install -y build-essential python3-dev python3-distutils

# Install Python dependencies
pip install -r requirements.txt
