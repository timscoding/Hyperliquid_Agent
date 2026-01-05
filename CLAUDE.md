# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the trading agent
python main.py

# Run tests
python -m pytest tests/
python test_astrology.py
python test_github_models.py
```

## Architecture Overview

**Multi-Agent Trading System** using LangGraph for orchestration:

```
main.py → TradingAgentsGraph → Agents (Analysts) → DataFlows → External APIs
                ↓
           Execution Layer (Hyperliquid DEX / Simulated)
```

### Core Components

1. **TradingAgentsGraph** (`tradingagents/graph/trading_graph.py`)
   - Main orchestrator that coordinates all agents
   - Manages LLM initialization (OpenAI/Anthropic/Google)
   - Creates tool nodes for each analyst type

2. **Agents** (`tradingagents/agents/`)
   - `analysts/`: market, news, fundamentals, social_media, astrology
   - `researchers/`: bull_researcher, bear_researcher
   - `risk_mgmt/`: aggressive, conservative, neutral debators
   - `trader/`: Final trading decision maker

3. **DataFlows** (`tradingagents/dataflows/`)
   - Vendor abstraction layer for data sources
   - `interface.py`: Central routing via `route_to_vendor(method, *args)`
   - Vendors: yfinance, alpha_vantage, local, openai, google

4. **Execution** (`tradingagents/execution/`)
   - `simulated_executor.py`: Paper trading
   - `hyperliquid_executor.py`: Real DEX trading

### Vendor Routing System

The `interface.py` routes data requests to configured vendors:

```python
# Config in default_config.py or main.py
config["data_vendors"] = {
    "core_stock_apis": "yfinance",      # get_stock_data
    "technical_indicators": "yfinance", # get_indicators
    "fundamental_data": "alpha_vantage",# get_fundamentals, get_balance_sheet, etc.
    "news_data": "alpha_vantage",       # get_news, get_global_news
}

# Tool-level override
config["tool_vendors"] = {
    "get_stock_data": "alpha_vantage",  # Override category default
}
```

### Adding New Data Sources

1. Create vendor module in `dataflows/` (e.g., `alpha_vantage_crypto.py`)
2. Register in `interface.py`:
   - Add to `VENDOR_METHODS` dict
   - Add to `TOOLS_CATEGORIES` if new category
3. Import in `interface.py` top imports
4. Create tool wrapper in `agents/utils/` if needed

### Configuration

- `tradingagents/default_config.py`: Default settings
- `config/astrology_rules.yaml`: 150+ astrological rules
- `config/trading_assets.yaml`: Asset configuration
- `.env`: API keys (OPENAI_API_KEY, ALPHA_VANTAGE_API_KEY, etc.)

### Key Files for Crypto Integration

- `dataflows/alpha_vantage_crypto.py`: Crypto OHLCV + news
- `dataflows/coinmarketcap.py`: Crypto fundamentals
- `agents/utils/core_stock_tools.py`: Price data tool
- `agents/utils/fundamental_data_tools.py`: Fundamentals tool
- `agents/utils/news_data_tools.py`: News tool
- `dataflows/interface.py`: Vendor routing

## Environment Variables

```bash
OPENAI_API_KEY=           # OpenAI or GitHub Models PAT
OPENAI_API_BASE=          # https://models.inference.ai.azure.com for GitHub Models
ALPHA_VANTAGE_API_KEY=    # Alpha Vantage API
COINMARKETCAP_API_KEY=    # CoinMarketCap API
HYPERLIQUID_SECRET_KEY=   # Hyperliquid wallet key
HYPERLIQUID_TESTNET=true  # Use testnet
```

## Crypto Assets

Hyperliquid uses simple symbols: `"BTC"`, `"ETH"`, `"SOL"` (NOT `"BTC-USD"`)

Asset mapping in config:
```python
"asset_mapping": {
    "BTC": "BTC", "ETH": "ETH", "SOL": "SOL",
    "HYPE": "HYPE", "UNI": "UNI", "LINK": "LINK"
}
```
