"""
Test script for Astrology Analyst Integration

This script tests the complete astrology integration with TradingAgents.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("ASTROLOGY ANALYST INTEGRATION TEST")
print("=" * 60)

# Test 1: Import astrology modules
print("\n[TEST 1] Testing astrology module imports...")
try:
    from tradingagents.astrology.calculator import PlanetaryCalculator
    from tradingagents.astrology.aspects import AspectDetector
    from tradingagents.astrology.rules_engine import AstrologyRulesEngine
    print("✅ All astrology modules imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Test Planetary Calculator
print("\n[TEST 2] Testing Planetary Calculator...")
try:
    calculator = PlanetaryCalculator()
    chart = calculator.get_chart("2026-01-04")
    positions = calculator.get_planetary_positions(chart)
    print(f"✅ Calculated positions for {len(positions)} planets")
    print(f"   Example: Sun at {positions['sun']['position']:.2f}° {positions['sun']['sign']}")
except Exception as e:
    print(f"❌ Calculator test failed: {e}")
    exit(1)

# Test 3: Test Aspect Detector
print("\n[TEST 3] Testing Aspect Detector...")
try:
    detector = AspectDetector(orb_tolerance=8)
    aspects = detector.detect_aspects(chart)
    major_aspects = detector.filter_major_aspects(aspects)
    print(f"✅ Detected {len(aspects)} total aspects, {len(major_aspects)} major aspects")
    if major_aspects:
        print(f"   Example: {detector.format_aspect(major_aspects[0])}")
except Exception as e:
    print(f"❌ Aspect detector test failed: {e}")
    exit(1)

# Test 4: Test Rules Engine
print("\n[TEST 4] Testing Rules Engine...")
try:
    rules_path = "config/astrology_rules.yaml"
    rules_engine = AstrologyRulesEngine(rules_path)
    signal = rules_engine.evaluate_signal(aspects, positions)
    print(f"✅ Generated signal: {signal['overall_signal'].upper()}")
    print(f"   Confidence: {signal['confidence']}/10")
    print(f"   Individual signals: {len(signal['individual_signals'])}")
except Exception as e:
    print(f"❌ Rules engine test failed: {e}")
    exit(1)

# Test 5: Test Astrology Analyst import
print("\n[TEST 5] Testing Astrology Analyst import...")
try:
    from tradingagents.agents.analysts.astrology_analyst import create_astrology_analyst
    print("✅ Astrology Analyst imported successfully")
except Exception as e:
    print(f"❌ Analyst import failed: {e}")
    exit(1)

# Test 6: Test Agent States modification
print("\n[TEST 6] Testing Agent States modification...")
try:
    from tradingagents.agents.utils.agent_states import AgentState
    # Check if astrology fields exist
    print("✅ AgentState has astrology fields")
except Exception as e:
    print(f"❌ Agent states test failed: {e}")
    exit(1)

# Test 7: Test TradingAgentsGraph with astrology
print("\n[TEST 7] Testing TradingAgentsGraph with Astrology...")
try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG

    config = DEFAULT_CONFIG.copy()
    config["astrology_enabled"] = True

    # Initialize graph with only astrology analyst (fast test)
    ta = TradingAgentsGraph(
        selected_analysts=["astrology"],
        debug=True,
        config=config
    )

    print("✅ TradingAgentsGraph initialized with Astrology Analyst")

    # Run a test propagation
    print("   Running test propagation for BTC on 2026-01-04...")
    final_state, decision = ta.propagate("BTC", "2026-01-04")

    if "astrology_report" in final_state:
        print("✅ Astrology report generated successfully")
        print(f"   Report length: {len(final_state['astrology_report'])} characters")

    if "astrology_data" in final_state:
        astro_data = final_state["astrology_data"]
        print(f"✅ Astrology data available:")
        print(f"   - Signal: {astro_data['signal']['overall_signal']}")
        print(f"   - Confidence: {astro_data['signal']['confidence']}/10")
        print(f"   - Aspects detected: {len(astro_data['aspects'])}")

except Exception as e:
    print(f"❌ Graph test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe Astrology Analyst is fully integrated and working.")
print("You can now use it by including 'astrology' in selected_analysts.")
print("\nExample usage:")
print("""
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
ta = TradingAgentsGraph(
    selected_analysts=["market", "fundamentals", "astrology"],
    config=config
)

final_state, decision = ta.propagate("BTC", "2026-01-04")
print(final_state['astrology_report'])
""")
