# Deep Research Agent with Memora

A comprehensive research agent that uses **Memora** for persistent semantic memory management, 
enabling deep, context-aware research with cross-session knowledge retention.

## Features

- **Semantic Memory**: Persistent research storage with semantic search via Memora
- **Agentic Research Loop**: Multi-step research orchestration with Claude AI
- **Web Integration**: Search and crawl web sources for real-time information
- **Knowledge Graph**: Visualize research connections and findings
- **Context Accumulation**: Build on previous research sessions
- **Citation Management**: Proper source attribution in reports

## Installation

### Prerequisites
- Python 3.9+
- OpenAI or Anthropic API key
- Memora installed via pip

### Quick Start

```bash
# Clone and setup
git clone https://github.com/memora-deep-research/deep-research
cd deep-research

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install git+https://github.com/agentic-box/memora.git
