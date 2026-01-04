"""
Simulated Executor

Simulates order execution for backtesting and testing.
"""

from .base_executor import BaseExecutor
from typing import Dict, Optional, Literal
from datetime import datetime
import uuid


class SimulatedExecutor(BaseExecutor):
    """
    Simulates order execution without connecting to a real exchange.

    Useful for backtesting, testing, and development.
    """

    def __init__(self, initial_balance: float = 10000.0, slippage: float = 0.001):
        """
        Initialize simulated executor.

        Args:
            initial_balance: Starting account balance in USD
            slippage: Simulated slippage percentage (default 0.1%)
        """
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.slippage = slippage
        self.positions = {}  # asset -> {"size": float, "entry_price": float}
        self.orders = {}  # order_id -> order_dict
        self.order_history = []
        self.trade_count = 0

    def place_order(
        self,
        asset: str,
        side: Literal["buy", "sell"],
        size: float,
        order_type: Literal["market", "limit"],
        price: Optional[float] = None,
        reduce_only: bool = False,
    ) -> Dict:
        """Place a simulated order."""

        order_id = str(uuid.uuid4())
        timestamp = self.get_timestamp()

        # For simulation, we assume immediate market execution
        if order_type == "market":
            # Simulate market price (in production, this would be fetched from data)
            execution_price = price if price else 50000.0  # Default BTC price

            # Apply slippage
            if side == "buy":
                execution_price *= (1 + self.slippage)
            else:
                execution_price *= (1 - self.slippage)

            # Calculate cost
            cost = size * execution_price

            # Check if we have enough balance for buy orders
            if side == "buy" and cost > self.balance:
                return {
                    "success": False,
                    "order_id": order_id,
                    "filled_size": 0,
                    "average_price": 0,
                    "status": "rejected",
                    "timestamp": timestamp,
                    "error": f"Insufficient balance. Need ${cost:.2f}, have ${self.balance:.2f}"
                }

            # Update position
            if asset not in self.positions:
                self.positions[asset] = {"size": 0, "entry_price": 0}

            current_position = self.positions[asset]

            if side == "buy":
                # Calculate new average entry price
                total_size = current_position["size"] + size
                if total_size > 0:
                    new_entry = (
                        (current_position["size"] * current_position["entry_price"]) +
                        (size * execution_price)
                    ) / total_size
                else:
                    new_entry = execution_price

                self.positions[asset] = {
                    "size": total_size,
                    "entry_price": new_entry
                }
                self.balance -= cost

            else:  # sell
                new_size = current_position["size"] - size
                self.positions[asset]["size"] = new_size

                # Add proceeds to balance
                self.balance += cost

                # Calculate realized PnL
                if current_position["size"] > 0:
                    pnl = (execution_price - current_position["entry_price"]) * size
                    # Could track PnL here

            self.trade_count += 1

            result = {
                "success": True,
                "order_id": order_id,
                "filled_size": size,
                "average_price": execution_price,
                "status": "filled",
                "timestamp": timestamp,
                "error": None
            }

            self.order_history.append(result)
            return result

        else:  # limit order
            # In simulation, we don't support pending limit orders
            # Just execute as market for simplicity
            return self.place_order(asset, side, size, "market", price, reduce_only)

    def get_position(self, asset: str) -> Dict:
        """Get current position for an asset."""

        if asset not in self.positions:
            return {
                "asset": asset,
                "size": 0,
                "entry_price": 0,
                "unrealized_pnl": 0,
                "liquidation_price": None,
                "leverage": 1.0
            }

        position = self.positions[asset]

        # For simulation, calculate unrealized PnL using current "market price"
        # In production, fetch real market price
        current_price = 50000.0  # Placeholder

        unrealized_pnl = 0
        if position["size"] != 0:
            unrealized_pnl = (current_price - position["entry_price"]) * position["size"]

        return {
            "asset": asset,
            "size": position["size"],
            "entry_price": position["entry_price"],
            "unrealized_pnl": unrealized_pnl,
            "liquidation_price": None,  # No liquidation in spot simulation
            "leverage": 1.0
        }

    def get_account_value(self) -> Dict:
        """Get account equity."""

        total_unrealized_pnl = 0
        for asset in self.positions:
            pos = self.get_position(asset)
            total_unrealized_pnl += pos["unrealized_pnl"]

        account_value = self.balance + total_unrealized_pnl

        return {
            "account_value": account_value,
            "margin_used": 0,  # Spot trading, no margin
            "available_margin": account_value,
            "total_unrealized_pnl": total_unrealized_pnl,
            "buying_power": self.balance
        }

    def cancel_order(self, order_id: str) -> Dict:
        """Cancel order (not used in simulation)."""
        return {
            "success": False,
            "order_id": order_id,
            "error": "Order cancellation not supported in simulation"
        }

    def get_order_status(self, order_id: str) -> Dict:
        """Get order status."""

        for order in self.order_history:
            if order["order_id"] == order_id:
                return {
                    "order_id": order_id,
                    "status": order["status"],
                    "filled_size": order["filled_size"],
                    "remaining_size": 0,
                    "average_price": order["average_price"]
                }

        return {
            "order_id": order_id,
            "status": "not_found",
            "filled_size": 0,
            "remaining_size": 0,
            "average_price": 0
        }

    def get_statistics(self) -> Dict:
        """Get trading statistics (simulation-specific method)."""

        return {
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "total_trades": self.trade_count,
            "positions": len([p for p in self.positions.values() if p["size"] != 0]),
            "pnl_percent": ((self.get_account_value()["account_value"] - self.initial_balance) / self.initial_balance) * 100
        }
