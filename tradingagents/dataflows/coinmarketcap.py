"""CoinMarketCap API integration for TradingAgents.

Provides crypto-specific "fundamentals":
- get_crypto_metadata: /v2/cryptocurrency/info
- get_crypto_quotes: /v2/cryptocurrency/quotes/latest
- get_crypto_fundamentals: Combined metadata + quotes (replaces traditional fundamentals)
"""

import os
import requests
import json
from typing import Optional

API_BASE_URL = "https://pro-api.coinmarketcap.com"


def get_api_key() -> str:
    """Retrieve the CoinMarketCap API key from environment variables."""
    api_key = os.getenv("COINMARKETCAP_API_KEY")
    if not api_key:
        raise ValueError("COINMARKETCAP_API_KEY environment variable is not set.")
    return api_key


class CoinMarketCapError(Exception):
    """Exception raised for CoinMarketCap API errors."""
    pass


def _make_api_request(endpoint: str, params: dict) -> dict:
    """Helper function to make CoinMarketCap API requests.

    Args:
        endpoint: API endpoint path (e.g., "/v2/cryptocurrency/info")
        params: Query parameters

    Returns:
        JSON response data

    Raises:
        CoinMarketCapError: When API returns an error
    """
    headers = {
        "X-CMC_PRO_API_KEY": get_api_key(),
        "Accept": "application/json",
    }

    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=params)

    try:
        data = response.json()
    except json.JSONDecodeError:
        raise CoinMarketCapError(f"Invalid JSON response: {response.text}")

    if response.status_code != 200:
        error_msg = data.get("status", {}).get("error_message", "Unknown error")
        raise CoinMarketCapError(f"CoinMarketCap API error: {error_msg}")

    return data


def get_crypto_metadata(symbol: str) -> str:
    """
    Retrieve metadata for a cryptocurrency.

    Uses CoinMarketCap /v2/cryptocurrency/info endpoint.

    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH)

    Returns:
        Formatted string containing:
        - Name, description
        - Website, technical docs
        - Tags (DeFi, Layer1, etc.)
        - Platform info
    """
    params = {"symbol": symbol}

    try:
        data = _make_api_request("/v2/cryptocurrency/info", params)

        # Extract the first result for the symbol
        crypto_data = data.get("data", {}).get(symbol, [])
        if isinstance(crypto_data, list) and len(crypto_data) > 0:
            crypto_data = crypto_data[0]
        elif not crypto_data:
            return f"No metadata found for {symbol}"

        # Format the response
        result = f"""
=== {crypto_data.get('name', symbol)} ({symbol}) Metadata ===

Description: {crypto_data.get('description', 'N/A')[:500]}...

Category: {crypto_data.get('category', 'N/A')}
Tags: {', '.join(crypto_data.get('tags', [])) or 'N/A'}

Website: {', '.join([url.get('url', '') for url in crypto_data.get('urls', {}).get('website', [])]) or 'N/A'}
Technical Docs: {', '.join([url.get('url', '') for url in crypto_data.get('urls', {}).get('technical_doc', [])]) or 'N/A'}

Date Added: {crypto_data.get('date_added', 'N/A')}
Platform: {crypto_data.get('platform', {}).get('name', 'Native') if crypto_data.get('platform') else 'Native'}
"""
        return result.strip()

    except CoinMarketCapError as e:
        return f"Error fetching metadata for {symbol}: {str(e)}"
    except Exception as e:
        return f"Unexpected error fetching metadata for {symbol}: {str(e)}"


def get_crypto_quotes(symbol: str) -> str:
    """
    Retrieve latest market quotes for a cryptocurrency.

    Uses CoinMarketCap /v2/cryptocurrency/quotes/latest endpoint.

    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH)

    Returns:
        Formatted string containing:
        - Market cap, volume 24h
        - Circulating/total/max supply
        - Price changes (1h, 24h, 7d, 30d)
        - Market dominance
    """
    params = {"symbol": symbol, "convert": "USD"}

    try:
        data = _make_api_request("/v2/cryptocurrency/quotes/latest", params)

        # Extract the first result for the symbol
        crypto_data = data.get("data", {}).get(symbol, [])
        if isinstance(crypto_data, list) and len(crypto_data) > 0:
            crypto_data = crypto_data[0]
        elif not crypto_data:
            return f"No quotes found for {symbol}"

        quote = crypto_data.get("quote", {}).get("USD", {})

        # Format numbers
        def fmt_num(n, prefix="$", suffix=""):
            if n is None:
                return "N/A"
            if n >= 1_000_000_000:
                return f"{prefix}{n/1_000_000_000:.2f}B{suffix}"
            elif n >= 1_000_000:
                return f"{prefix}{n/1_000_000:.2f}M{suffix}"
            elif n >= 1_000:
                return f"{prefix}{n/1_000:.2f}K{suffix}"
            return f"{prefix}{n:.2f}{suffix}"

        def fmt_pct(n):
            if n is None:
                return "N/A"
            return f"{n:+.2f}%"

        result = f"""
=== {crypto_data.get('name', symbol)} ({symbol}) Market Data ===

Price: ${quote.get('price', 0):.4f}
Market Cap: {fmt_num(quote.get('market_cap'))}
Volume (24h): {fmt_num(quote.get('volume_24h'))}
Market Dominance: {fmt_pct(quote.get('market_cap_dominance'))}

Supply:
  - Circulating: {fmt_num(crypto_data.get('circulating_supply'), prefix='', suffix=f' {symbol}')}
  - Total: {fmt_num(crypto_data.get('total_supply'), prefix='', suffix=f' {symbol}')}
  - Max: {fmt_num(crypto_data.get('max_supply'), prefix='', suffix=f' {symbol}')}

Price Changes:
  - 1h:  {fmt_pct(quote.get('percent_change_1h'))}
  - 24h: {fmt_pct(quote.get('percent_change_24h'))}
  - 7d:  {fmt_pct(quote.get('percent_change_7d'))}
  - 30d: {fmt_pct(quote.get('percent_change_30d'))}

Rank: #{crypto_data.get('cmc_rank', 'N/A')}
Last Updated: {quote.get('last_updated', 'N/A')}
"""
        return result.strip()

    except CoinMarketCapError as e:
        return f"Error fetching quotes for {symbol}: {str(e)}"
    except Exception as e:
        return f"Unexpected error fetching quotes for {symbol}: {str(e)}"


def get_crypto_fundamentals(symbol: str, curr_date: str = None) -> str:
    """
    Retrieve combined fundamental data for a cryptocurrency.

    Replaces traditional stock fundamentals (balance sheet, cash flow, income)
    with crypto-specific metrics from CoinMarketCap.

    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH)
        curr_date: Current date (not used, for API compatibility)

    Returns:
        Combined metadata + market quotes formatted as fundamental analysis.
    """
    metadata = get_crypto_metadata(symbol)
    quotes = get_crypto_quotes(symbol)

    result = f"""
╔══════════════════════════════════════════════════════════════════╗
║           CRYPTO FUNDAMENTALS REPORT: {symbol}
╚══════════════════════════════════════════════════════════════════╝

{quotes}

{metadata}

══════════════════════════════════════════════════════════════════
NOTE: Cryptocurrencies do not have traditional financial statements
(Balance Sheet, Cash Flow, Income Statement). The above metrics
represent the crypto-equivalent fundamental analysis.
══════════════════════════════════════════════════════════════════
"""
    return result.strip()
