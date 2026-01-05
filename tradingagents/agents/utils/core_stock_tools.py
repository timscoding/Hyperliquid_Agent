from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.config import get_config

# Known crypto symbols and names
CRYPTO_SYMBOLS = {
    "BTC", "ETH", "SOL", "AVAX", "MATIC", "HYPE", "UNI", "LINK",
    "XRP", "AAVE", "TAO", "ARB", "OP", "DOGE", "SHIB", "ADA",
    "DOT", "ATOM", "NEAR", "APT", "SUI", "SEI", "TIA", "INJ"
}

# Map full names to symbols for detection
CRYPTO_NAMES = {
    "BITCOIN": "BTC", "ETHEREUM": "ETH", "SOLANA": "SOL",
    "AVALANCHE": "AVAX", "POLYGON": "MATIC", "HYPERLIQUID": "HYPE",
    "UNISWAP": "UNI", "CHAINLINK": "LINK", "RIPPLE": "XRP",
    "AAVE": "AAVE", "BITTENSOR": "TAO", "ARBITRUM": "ARB",
    "OPTIMISM": "OP", "DOGECOIN": "DOGE", "SHIBA": "SHIB",
    "CARDANO": "ADA", "POLKADOT": "DOT", "COSMOS": "ATOM",
}


def is_crypto(symbol: str) -> bool:
    """Check if a symbol is a cryptocurrency."""
    symbol_upper = symbol.upper()
    # Check known crypto symbols
    if symbol_upper in CRYPTO_SYMBOLS:
        return True
    # Check known crypto names (e.g., "Bitcoin" -> True)
    if symbol_upper in CRYPTO_NAMES:
        return True
    # Check asset_mapping in config
    config = get_config()
    asset_mapping = config.get("asset_mapping", {})
    if symbol_upper in asset_mapping:
        return True
    return False


def get_crypto_symbol(symbol: str) -> str:
    """Convert a crypto name to its symbol (e.g., 'Bitcoin' -> 'BTC')."""
    symbol_upper = symbol.upper()
    if symbol_upper in CRYPTO_NAMES:
        return CRYPTO_NAMES[symbol_upper]
    return symbol_upper


@tool
def get_stock_data(
    symbol: Annotated[str, "ticker symbol of the company or cryptocurrency"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve price data (OHLCV) for a given ticker symbol.
    Automatically routes to crypto or stock data based on symbol.
    Args:
        symbol (str): Ticker symbol (e.g., AAPL, TSM for stocks; BTC, ETH for crypto)
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the price data for the specified ticker symbol in the specified date range.
    """
    if is_crypto(symbol):
        # Route to crypto data endpoint
        return route_to_vendor("get_crypto_daily", symbol, "USD", start_date, end_date)
    else:
        # Route to stock data endpoint
        return route_to_vendor("get_stock_data", symbol, start_date, end_date)
