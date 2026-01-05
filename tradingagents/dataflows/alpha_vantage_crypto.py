"""Alpha Vantage Crypto API integration for TradingAgents.

Provides:
- get_crypto_daily: DIGITAL_CURRENCY_DAILY endpoint for OHLCV data
- get_crypto_news: NEWS_SENTIMENT endpoint with CRYPTO: prefix
"""

from datetime import datetime
from .alpha_vantage_common import _make_api_request, _filter_csv_by_date_range, format_datetime_for_api


def get_crypto_daily(
    symbol: str,
    market: str,
    start_date: str,
    end_date: str
) -> str:
    """
    Returns daily OHLCV data for a cryptocurrency against a market currency.

    Uses Alpha Vantage DIGITAL_CURRENCY_DAILY endpoint.

    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH, HYPE, UNI, LINK, XRP, AAVE, TAO)
        market: Market currency (default: USD)
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format

    Returns:
        CSV string containing daily OHLCV data filtered to the date range.
    """
    params = {
        "symbol": symbol,
        "market": market,
        "datatype": "csv",
    }

    response = _make_api_request("DIGITAL_CURRENCY_DAILY", params)

    return _filter_csv_by_date_range(response, start_date, end_date)


def get_crypto_news(
    symbols: str,
    start_date: str,
    end_date: str,
    topics: str = None,
) -> str:
    """
    Returns news sentiment data for cryptocurrencies.

    Uses Alpha Vantage NEWS_SENTIMENT endpoint with CRYPTO: prefix.

    Args:
        symbols: Comma-separated crypto symbols (e.g., "BTC,ETH")
                 Will be automatically prefixed with CRYPTO:
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
        topics: Optional filter topics (e.g., "blockchain", "technology")

    Returns:
        JSON string containing news sentiment data.
    """
    # Format symbols with CRYPTO: prefix
    formatted_tickers = ",".join([
        f"CRYPTO:{sym.strip()}" for sym in symbols.split(",")
    ])

    params = {
        "tickers": formatted_tickers,
        "time_from": format_datetime_for_api(start_date),
        "time_to": format_datetime_for_api(end_date),
        "sort": "LATEST",
        "limit": "50",
    }

    if topics:
        params["topics"] = topics

    return _make_api_request("NEWS_SENTIMENT", params)
