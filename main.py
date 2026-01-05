from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"  # GitHub Models: gpt-4o-mini has higher token limits
config["quick_think_llm"] = "gpt-4o-mini"  # GitHub Models: gpt-4o-mini for quick tasks
config["max_debate_rounds"] = 1  # Increase debate rounds

# Configure data vendors (default uses yfinance and alpha_vantage)
config["data_vendors"] = {
    "core_stock_apis": "yfinance",           # Options: yfinance, alpha_vantage, local
    "core_crypto_apis": "alpha_vantage",     # Crypto OHLCV via DIGITAL_CURRENCY_DAILY
    "technical_indicators": "yfinance",      # Options: yfinance, alpha_vantage, local
    "fundamental_data": "alpha_vantage",     # Options: openai, alpha_vantage, local
    "crypto_fundamentals": "coinmarketcap",  # Crypto market data (market cap, supply, etc.)
    "news_data": "alpha_vantage",            # Primary: alpha_vantage, auto-fallback to local on rate limit
}

# Initialize with custom config (debug=False to avoid Windows console encoding issues)
ta = TradingAgentsGraph(debug=False, config=config)

# forward propagate - use BTC for crypto trading
_, decision = ta.propagate("BTC", "2025-01-15")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
