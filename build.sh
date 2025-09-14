# Cloudflare Pages build script
#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Create startup script for Streamlit
cat > start.sh << 'EOF'
#!/bin/bash
export STREAMLIT_SERVER_PORT=${PORT:-8501}
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start Streamlit app
streamlit run webui/app_beta.py --server.port=$STREAMLIT_SERVER_PORT --server.address=$STREAMLIT_SERVER_ADDRESS
EOF

chmod +x start.sh

echo "Build completed successfully!"