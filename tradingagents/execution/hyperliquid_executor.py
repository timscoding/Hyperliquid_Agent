"""
Hyperliquid Executor

Executes real orders on Hyperliquid DEX.
"""

from .base_executor import BaseExecutor
from typing import Dict, Optional, Literal
from datetime import datetime
import os


class HyperliquidExecutor(BaseExecutor):
    """
    Executes orders on Hyperliquid DEX.

    Supports both testnet and mainnet trading.
    """

    def __init__(self, testnet: bool = True, config: Optional[Dict] = None):
        """
        Initialize Hyperliquid executor.

        Args:
            testnet: If True, use testnet API
            config: Optional configuration dict with settings
        """
        self.testnet = testnet
        self.config = config or {}

        # Import Hyperliquid SDK
        try:
            from hyperliquid.info import Info
            from hyperliquid.exchange import Exchange
            from hyperliquid.utils import constants
            from eth_account import Account
        except ImportError:
            raise ImportError(
                "Hyperliquid SDK not installed. "
                "Install with: pip install hyperliquid-python-sdk eth-account"
            )

        # Get credentials from environment
        self.secret_key = os.getenv("HYPERLIQUID_SECRET_KEY")
        self.account_address = os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS")

        if not self.secret_key:
            raise ValueError(
                "HYPERLIQUID_SECRET_KEY not found in environment. "
                "Set it in .env file or environment variables."
            )

        # Initialize account
        self.account = Account.from_key(self.secret_key)

        # If address not provided, derive from private key
        if not self.account_address:
            self.account_address = self.account.address

        # Set API base URL
        if testnet:
            self.base_url = constants.TESTNET_API_URL
        else:
            self.base_url = constants.MAINNET_API_URL

        # Initialize clients
        self.info = Info(self.base_url, skip_ws=True)
        self.exchange = Exchange(
            account=self.account,
            base_url=self.base_url
        )

        # Default slippage for market orders
        self.default_slippage = self.config.get("default_slippage", 0.05)

    def place_order(
        self,
        asset: str,
        side: Literal["buy", "sell"],
        size: float,
        order_type: Literal["market", "limit"],
        price: Optional[float] = None,
        reduce_only: bool = False,
    ) -> Dict:
        """
        Place an order on Hyperliquid.

        Args:
            asset: Asset symbol (e.g., "BTC", "ETH")
            side: "buy" or "sell"
            size: Order size
            order_type: "market" or "limit"
            price: Limit price (required for limit orders)
            reduce_only: If True, only reduce position

        Returns:
            Order result dict
        """
        is_buy = (side == "buy")
        timestamp = self.get_timestamp()

        try:
            if order_type == "market":
                # Place market order
                result = self.exchange.market_order(
                    coin=asset,
                    is_buy=is_buy,
                    sz=size,
                    slippage=self.default_slippage,
                    reduce_only=reduce_only
                )

            else:  # limit order
                if price is None:
                    return {
                        "success": False,
                        "order_id": None,
                        "filled_size": 0,
                        "average_price": 0,
                        "status": "rejected",
                        "timestamp": timestamp,
                        "error": "Limit price required for limit orders"
                    }

                result = self.exchange.limit_order(
                    coin=asset,
                    is_buy=is_buy,
                    sz=size,
                    px=price,
                    reduce_only=reduce_only
                )

            # Parse Hyperliquid response
            if result.get("status") == "ok":
                response_data = result.get("response", {}).get("data", {})
                statuses = response_data.get("statuses", [{}])

                if statuses:
                    status = statuses[0]

                    # Get order ID
                    order_id = None
                    if "resting" in status:
                        order_id = status["resting"].get("oid")
                    elif "filled" in status:
                        filled_data = status["filled"]
                        order_id = filled_data.get("oid")

                        return {
                            "success": True,
                            "order_id": order_id,
                            "filled_size": float(filled_data.get("totalSz", size)),
                            "average_price": float(filled_data.get("avgPx", price or 0)),
                            "status": "filled",
                            "timestamp": timestamp,
                            "error": None
                        }

                    return {
                        "success": True,
                        "order_id": order_id,
                        "filled_size": 0,
                        "average_price": price or 0,
                        "status": "open",
                        "timestamp": timestamp,
                        "error": None
                    }

            # Order failed
            error_msg = result.get("response", {}).get("error", "Unknown error")
            return {
                "success": False,
                "order_id": None,
                "filled_size": 0,
                "average_price": 0,
                "status": "rejected",
                "timestamp": timestamp,
                "error": error_msg
            }

        except Exception as e:
            return {
                "success": False,
                "order_id": None,
                "filled_size": 0,
                "average_price": 0,
                "status": "error",
                "timestamp": timestamp,
                "error": str(e)
            }

    def get_position(self, asset: str) -> Dict:
        """Get current position for an asset."""

        try:
            user_state = self.info.user_state(self.account_address)

            # Look for asset in positions
            for position in user_state.get("assetPositions", []):
                pos_data = position.get("position", {})

                if pos_data.get("coin") == asset:
                    size = float(pos_data.get("szi", 0))
                    entry_price = float(pos_data.get("entryPx", 0))
                    liquidation_px = pos_data.get("liquidationPx")

                    # Calculate unrealized PnL
                    unrealized_pnl = float(pos_data.get("unrealizedPnl", 0))

                    return {
                        "asset": asset,
                        "size": size,
                        "entry_price": entry_price,
                        "unrealized_pnl": unrealized_pnl,
                        "liquidation_price": float(liquidation_px) if liquidation_px else None,
                        "leverage": float(pos_data.get("leverage", {}).get("value", 1))
                    }

            # No position found
            return {
                "asset": asset,
                "size": 0,
                "entry_price": 0,
                "unrealized_pnl": 0,
                "liquidation_price": None,
                "leverage": 1.0
            }

        except Exception as e:
            raise RuntimeError(f"Error fetching position: {str(e)}")

    def get_account_value(self) -> Dict:
        """Get account equity and margin."""

        try:
            user_state = self.info.user_state(self.account_address)
            margin = user_state.get("marginSummary", {})

            account_value = float(margin.get("accountValue", 0))
            margin_used = float(margin.get("totalMarginUsed", 0))
            total_unrealized_pnl = float(margin.get("totalNtlPos", 0))

            available_margin = account_value - margin_used

            return {
                "account_value": account_value,
                "margin_used": margin_used,
                "available_margin": available_margin,
                "total_unrealized_pnl": total_unrealized_pnl,
                "buying_power": available_margin
            }

        except Exception as e:
            raise RuntimeError(f"Error fetching account value: {str(e)}")

    def cancel_order(self, order_id: str, asset: str) -> Dict:
        """
        Cancel an open order.

        Args:
            order_id: Order ID (oid from Hyperliquid)
            asset: Asset symbol (required by Hyperliquid)

        Returns:
            Cancellation result
        """
        try:
            result = self.exchange.cancel_order(
                coin=asset,
                oid=int(order_id)
            )

            if result.get("status") == "ok":
                return {
                    "success": True,
                    "order_id": order_id,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "order_id": order_id,
                    "error": result.get("response", {}).get("error", "Unknown error")
                }

        except Exception as e:
            return {
                "success": False,
                "order_id": order_id,
                "error": str(e)
            }

    def get_order_status(self, order_id: str) -> Dict:
        """
        Get order status.

        Note: Hyperliquid doesn't have a direct order status endpoint,
        so we check open orders.
        """
        try:
            user_state = self.info.user_state(self.account_address)
            open_orders = user_state.get("openOrders", [])

            for order in open_orders:
                if str(order.get("oid")) == str(order_id):
                    return {
                        "order_id": order_id,
                        "status": "open",
                        "filled_size": 0,
                        "remaining_size": float(order.get("sz", 0)),
                        "average_price": float(order.get("limitPx", 0))
                    }

            # Order not in open orders - assume filled or canceled
            return {
                "order_id": order_id,
                "status": "filled_or_canceled",
                "filled_size": 0,
                "remaining_size": 0,
                "average_price": 0
            }

        except Exception as e:
            return {
                "order_id": order_id,
                "status": "error",
                "filled_size": 0,
                "remaining_size": 0,
                "average_price": 0,
                "error": str(e)
            }

    def get_market_price(self, asset: str) -> float:
        """
        Get current market price for an asset.

        Args:
            asset: Asset symbol

        Returns:
            Current market price
        """
        try:
            meta = self.info.meta()

            for universe_item in meta.get("universe", []):
                if universe_item.get("name") == asset:
                    all_mids = self.info.all_mids()
                    return float(all_mids.get(asset, 0))

            raise ValueError(f"Asset {asset} not found")

        except Exception as e:
            raise RuntimeError(f"Error fetching market price: {str(e)}")
