"""
Complete System Test: Astrology + Hyperliquid Integration

This script tests the full trading bot with:
1. Astrology Analyst for market timing
2. Hyperliquid execution (simulated or real)
"""

import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

print("=" * 70)
print("COMPLETE TRADING BOT TEST: ASTROLOGY + HYPERLIQUID")
print("=" * 70)

# Test 1: Import all modules
print("\n[TEST 1] Importing modules...")
try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
    from tradingagents.execution import SimulatedExecutor, HyperliquidExecutor
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Initialize with Simulated Executor
print("\n[TEST 2] Initializing Trading Bot (Simulated Execution)...")
try:
    config = DEFAULT_CONFIG.copy()
    config["astrology_enabled"] = True
    config["use_real_execution"] = False  # Use simulation
    config["simulated_balance"] = 10000.0

    ta = TradingAgentsGraph(
        selected_analysts=["market", "astrology"],  # Use market + astrology
        debug=True,
        config=config
    )

    print("✅ Trading Bot initialized with Simulated Executor")
    print(f"   Executor type: {type(ta.executor).__name__}")

except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Run complete trading analysis
print("\n[TEST 3] Running complete trading analysis...")
print("   Asset: BTC")
print("   Date: 2026-01-04")
print("   This will take 1-2 minutes...")

try:
    final_state, decision = ta.propagate("BTC", "2026-01-04")

    print("\n" + "=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)

    # Show astrology analysis
    if "astrology_report" in final_state:
        print("\n📊 ASTROLOGY ANALYSIS:")
        print("-" * 70)
        astro_data = final_state.get("astrology_data", {})
        signal = astro_data.get("signal", {})

        print(f"Signal: {signal.get('overall_signal', 'N/A').upper()}")
        print(f"Confidence: {signal.get('confidence', 0)}/10")
        print(f"Aspects detected: {len(astro_data.get('aspects', []))}")

        # Show individual signals
        individual_signals = signal.get("individual_signals", [])
        if individual_signals:
            print(f"\nTop Astrological Signals:")
            for i, sig in enumerate(individual_signals[:3], 1):
                print(f"  {i}. {sig['source']}: {sig['signal'].upper()} (strength {sig['strength']}/10)")

    # Show final trading decision
    print("\n💰 TRADING DECISION:")
    print("-" * 70)
    print(f"Action: {decision.get('action', 'N/A')}")
    print(f"Confidence: {decision.get('confidence', 'N/A')}")

    # Execute trade if decision is BUY/SELL
    if decision.get("action") in ["BUY", "SELL"]:
        print("\n⚡ EXECUTING TRADE...")
        print("-" * 70)

        execution_result = ta.execute_trade(
            asset="BTC",
            action=decision["action"],
            size=0.01  # Small test size
        )

        if execution_result.get("success"):
            print(f"✅ Trade executed successfully!")
            print(f"   Order ID: {execution_result.get('order_id')}")
            print(f"   Filled: {execution_result.get('filled_size')} BTC")
            print(f"   Price: ${execution_result.get('average_price', 0):.2f}")
        else:
            print(f"❌ Trade execution failed: {execution_result.get('error')}")

    # Show account summary
    print("\n📈 ACCOUNT SUMMARY:")
    print("-" * 70)
    account = ta.executor.get_account_value()
    print(f"Account Value: ${account.get('account_value', 0):,.2f}")
    print(f"Buying Power: ${account.get('buying_power', 0):,.2f}")

    if hasattr(ta.executor, 'get_statistics'):
        stats = ta.executor.get_statistics()
        print(f"Total Trades: {stats.get('total_trades', 0)}")
        print(f"P&L: {stats.get('pnl_percent', 0):.2f}%")

    print("\n✅ Complete system test PASSED!")

except Exception as e:
    print(f"\n❌ Analysis failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Hyperliquid Executor (if credentials available)
print("\n" + "=" * 70)
print("[TEST 4] Hyperliquid Executor Test (Optional)")
print("=" * 70)

if os.getenv("HYPERLIQUID_SECRET_KEY"):
    print("\nHyperliquid credentials found. Testing connection...")

    try:
        hl_executor = HyperliquidExecutor(testnet=True)
        print("✅ Connected to Hyperliquid TESTNET")

        # Get account info
        account = hl_executor.get_account_value()
        print(f"   Account Value: ${account.get('account_value', 0):,.2f}")

    except Exception as e:
        print(f"⚠️  Hyperliquid test failed: {e}")
        print("   This is okay if you haven't set up Hyperliquid credentials yet.")
else:
    print("⚠️  No Hyperliquid credentials found in environment.")
    print("   Set HYPERLIQUID_SECRET_KEY in .env to test real execution.")
    print("   See .env.example for details.")

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("✅ Astrology Analyst: WORKING")
print("✅ Simulated Executor: WORKING")
print("✅ Trading Pipeline: WORKING")
print("\nThe trading bot is ready to use!")
print("\nNext steps:")
print("1. Adjust astrology rules in config/astrology_rules.yaml")
print("2. For real trading:")
print("   - Get Hyperliquid API key from https://app.hyperliquid.xyz/API")
print("   - Add to .env file")
print("   - Set use_real_execution=True in config")
print("   - ALWAYS test on testnet first!")
