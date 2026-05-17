#!/bin/bash
# Startup script para Azure App Service
python -m streamlit run main.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false
