#!/bin/bash
# Setup script for Deep Research with Memora
echo "🔧 Setting up Deep Research Agent with Memora..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install AnyCrawl and SearXNG explicitly
echo "📦 Installing AnyCrawl and SearXNG..."
pip install anycrawl
pip install searxng

# Install Memora from git
pip install git+https://github.com/agentic-box/memora.git

# Start Memora server
echo "📡 Starting Memora server..."
memora-server --graph-port 8765 &

# Create .env file from template
if [ ! -f .env ]; then
    cp .env.template .env
    echo "✅ Created .env file - please add your API keys"
else
    echo "✅ .env file already exists"
fi
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your API keys to .env file (including ANYCRAWL_API_KEY)"
echo "2. Run: python research.py"
echo "3. Visit http://localhost:8765/graph for memory visualization"