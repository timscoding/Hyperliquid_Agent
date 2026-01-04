import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-5-nano",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: yfinance, alpha_vantage, local
        "technical_indicators": "yfinance",  # Options: yfinance, alpha_vantage, local
        "fundamental_data": "alpha_vantage", # Options: openai, alpha_vantage, local
        "news_data": "alpha_vantage",        # Options: openai, alpha_vantage, google, local
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
        # Example: "get_news": "openai",               # Override category default
    },
    # Astrology settings
    "astrology_enabled": True,
    "astrology_rules_path": "config/astrology_rules.yaml",
    "astrology_orb_tolerance": 8,
    "astrology_location": {
        "city": "New York",
        "nation": "US",
        "lng": -74.0060,
        "lat": 40.7128,
        "tz_str": "America/New_York"
    },
    # Execution settings
    "use_real_execution": False,  # Set to True for real Hyperliquid trading
    "hyperliquid_testnet": True,  # Always start with testnet!
    "simulated_balance": 10000.0,
    # Asset mapping (symbol -> Hyperliquid symbol)
    "asset_mapping": {
        "BTC": "BTC",
        "ETH": "ETH",
        "SOL": "SOL",
        "AVAX": "AVAX",
        "MATIC": "MATIC",
    },
}
