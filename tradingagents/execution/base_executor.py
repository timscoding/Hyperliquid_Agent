"""
Base Executor Abstract Interface

Defines the interface for order execution across different platforms.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Literal
from datetime import datetime


class BaseExecutor(ABC):
    """
    Abstract base class for order execution.

    All execution implementations (simulated, Hyperliquid, etc.) must inherit
    from this class and implement the required methods.
    """

    @abstractmethod
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
        Place an order on the exchange.

        Args:
            asset: Asset symbol (e.g., "BTC", "ETH")
            side: Order side ("buy" or "sell")
            size: Order size in base asset units
            order_type: "market" or "limit"
            price: Limit price (required for limit orders)
            reduce_only: If True, only reduce existing position

        Returns:
            Dict with order result:
            {
                "success": bool,
                "order_id": str,
                "filled_size": float,
                "average_price": float,
                "status": str,
                "timestamp": datetime,
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    def get_position(self, asset: str) -> Dict:
        """
        Get current position for an asset.

        Args:
            asset: Asset symbol

        Returns:
            Dict with position data:
            {
                "asset": str,
                "size": float,  # Positive for long, negative for short
                "entry_price": float,
                "unrealized_pnl": float,
                "liquidation_price": Optional[float],
                "leverage": float
            }
        """
        pass

    @abstractmethod
    def get_account_value(self) -> Dict:
        """
        Get account equity and margin information.

        Returns:
            Dict with account data:
            {
                "account_value": float,
                "margin_used": float,
                "available_margin": float,
                "total_unrealized_pnl": float,
                "buying_power": float
            }
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> Dict:
        """
        Cancel an open order.

        Args:
            order_id: ID of the order to cancel

        Returns:
            Dict with cancellation result:
            {
                "success": bool,
                "order_id": str,
                "error": Optional[str]
            }
        """
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict:
        """
        Get status of a specific order.

        Args:
            order_id: Order ID

        Returns:
            Dict with order status:
            {
                "order_id": str,
                "status": str,  # "open", "filled", "canceled", "rejected"
                "filled_size": float,
                "remaining_size": float,
                "average_price": float
            }
        """
        pass

    def close_position(self, asset: str) -> Dict:
        """
        Close an existing position (convenience method).

        Args:
            asset: Asset symbol

        Returns:
            Order result dict
        """
        position = self.get_position(asset)

        if position["size"] == 0:
            return {
                "success": False,
                "error": "No position to close"
            }

        side = "sell" if position["size"] > 0 else "buy"
        size = abs(position["size"])

        return self.place_order(
            asset=asset,
            side=side,
            size=size,
            order_type="market",
            reduce_only=True
        )

    def get_timestamp(self) -> datetime:
        """Get current timestamp."""
        return datetime.utcnow()
