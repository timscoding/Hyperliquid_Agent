# 🚀 Kompletter Setup & Testing Guide für TradingAgents

## 📋 **Inhaltsverzeichnis**

1. [Initiales Setup](#initiales-setup)
2. [API Key Sicherheit](#api-key-sicherheit)
3. [Phase 1: Technische Tests](#phase-1-technische-tests)
4. [Phase 2: Paper Trading](#phase-2-paper-trading)
5. [Phase 3: Backtesting](#phase-3-backtesting)
6. [Phase 4: Live Trading](#phase-4-live-trading)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 **Initiales Setup**

### **Schritt 1: Environment Setup**

```bash
# 1. Navigiere zum Projekt
cd TradingAgents

# 2. Erstelle Virtual Environment (empfohlen)
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Installiere Dependencies
pip install -r requirements.txt

# 4. Verifiziere Installation
python -c "import kerykeion; import yaml; print('✅ Dependencies OK')"
```

### **Schritt 2: Environment Variables einrichten**

```bash
# 1. Kopiere .env.example zu .env
cp .env.example .env

# 2. Editiere .env und füge deine API Keys hinzu
# Windows: notepad .env
# Linux/Mac: nano .env
```

**Minimale .env Konfiguration:**
```bash
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-...

# Alpha Vantage (OPTIONAL - für Fundamentals)
ALPHA_VANTAGE_API_KEY=your_key_here

# Hyperliquid (OPTIONAL - erst später für Live Trading)
# HYPERLIQUID_SECRET_KEY=0x...
# HYPERLIQUID_TESTNET=true
```

### **Schritt 3: Konfiguration prüfen**

Editiere `tradingagents/default_config.py`:

```python
DEFAULT_CONFIG = {
    # LLM settings
    "deep_think_llm": "gpt-4o-mini",  # Günstiger für Tests
    "quick_think_llm": "gpt-4o-mini", # Günstiger für Tests

    # Astrology
    "astrology_enabled": True,

    # Execution (für Tests)
    "use_real_execution": False,  # Simulation
    "simulated_balance": 10000.0,
}
```

---

## 🔐 **API Key Sicherheit**

### **✅ SO machst du es RICHTIG:**

#### **1. `.env` Datei nutzen (LOKAL)**

```bash
# .env Datei erstellen (bereits gemacht)
# Diese Datei ist in .gitignore und wird NICHT committed

# Prüfen ob .gitignore funktioniert:
git status
# .env sollte NICHT in der Liste erscheinen!
```

#### **2. Environment Variables (SERVER/CLOUD)**

Wenn du auf einem Server/Cloud hostest:

**Heroku:**
```bash
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set HYPERLIQUID_SECRET_KEY=0x...
```

**AWS Lambda:**
```bash
# In AWS Console → Lambda → Environment Variables
# Oder via AWS CLI:
aws lambda update-function-configuration \
  --function-name trading-bot \
  --environment Variables={OPENAI_API_KEY=sk-...}
```

**Docker:**
```dockerfile
# docker-compose.yml
services:
  trading-bot:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    env_file:
      - .env  # Lokal
```

#### **3. Secrets Management (PRODUCTION)**

Für ernsthafte Production Use:

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name trading-bot/api-keys \
  --secret-string '{"openai":"sk-...","hyperliquid":"0x..."}'

# Dann in Code:
import boto3
secret = boto3.client('secretsmanager').get_secret_value(
    SecretId='trading-bot/api-keys'
)
```

### **❌ NIEMALS:**

- ✗ API Keys in Code hardcoden
- ✗ `.env` Datei in Git committen
- ✗ Keys in Screenshots/Logs zeigen
- ✗ Keys per Email/Chat teilen
- ✗ Same Keys für Dev & Production

### **Sicherheits-Checkliste:**

```bash
# 1. Prüfe .gitignore
cat .gitignore | grep .env
# Sollte enthalten: .env

# 2. Prüfe Git Status
git status
# .env sollte NICHT gelistet sein

# 3. Key-Rotation
# Rotiere Keys alle 90 Tage oder bei Leak sofort

# 4. Permissions
chmod 600 .env  # Nur Owner kann lesen
```

---

## 🧪 **Phase 1: Technische Tests**

### **Test 1: Basis-Funktionalität**

```bash
# Test 1: Module Imports
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.astrology import PlanetaryCalculator
print('✅ Imports OK')
"

# Test 2: Astrology Module
python test_astrology_integration.py

# Test 3: Complete System
python test_complete_system.py
```

**Erwartete Ausgabe:**
```
✅ All modules imported successfully
✅ Astrology Analyst: WORKING
✅ Simulated Executor: WORKING
✅ Trading Pipeline: WORKING
```

### **Test 2: Einzelne Komponenten**

**Erstelle:** `test_components.py`

```python
"""Test einzelne Komponenten isoliert"""

# Test 1: Nur Astrology
from tradingagents.astrology import PlanetaryCalculator, AspectDetector, AstrologyRulesEngine

calc = PlanetaryCalculator()
chart = calc.get_chart("2026-01-04")
detector = AspectDetector()
aspects = detector.detect_aspects(chart)

print(f"✅ Detected {len(aspects)} aspects")

# Test 2: Nur Simulated Executor
from tradingagents.execution import SimulatedExecutor

executor = SimulatedExecutor(initial_balance=10000)
result = executor.place_order("BTC", "buy", 0.1, "market", price=50000)

print(f"✅ Executor: {result['status']}")
print(f"   Balance: ${executor.balance:.2f}")

# Test 3: TradingAgents ohne Execution
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["use_real_execution"] = False

ta = TradingAgentsGraph(
    selected_analysts=["astrology"],  # Nur Astrology = schnell
    debug=True,
    config=config
)

state, decision = ta.propagate("BTC", "2026-01-04")
print(f"✅ Decision: {decision['action']}")
```

**Ausführen:**
```bash
python test_components.py
```

### **Test 3: Error Handling**

**Erstelle:** `test_error_handling.py`

```python
"""Test Error Handling und Edge Cases"""

from tradingagents.execution import SimulatedExecutor

executor = SimulatedExecutor(initial_balance=1000)

# Test 1: Insufficient balance
result = executor.place_order("BTC", "buy", 10, "market", price=50000)
assert result["success"] == False, "Should fail with insufficient balance"
print("✅ Insufficient balance handled correctly")

# Test 2: Invalid action
from tradingagents.graph.trading_graph import TradingAgentsGraph
ta = TradingAgentsGraph(selected_analysts=["astrology"], debug=False)
result = ta.execute_trade("BTC", "INVALID", 0.1)
assert result["success"] == False, "Should fail with invalid action"
print("✅ Invalid action handled correctly")

# Test 3: Missing API key
import os
old_key = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = ""

try:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm.invoke("test")
    print("❌ Should have failed without API key")
except Exception as e:
    print(f"✅ Missing API key handled: {type(e).__name__}")
finally:
    if old_key:
        os.environ["OPENAI_API_KEY"] = old_key

print("\n✅ All error handling tests passed!")
```

---

## 📊 **Phase 2: Paper Trading**

Paper Trading = Simulation mit Live-Daten aber ohne echtes Geld.

### **Setup Paper Trading**

**Erstelle:** `paper_trading.py`

```python
"""
Paper Trading Script

Simuliert Trading mit Live-Daten aber ohne echtes Geld.
Ideal zum Testen der Strategie ohne Risiko.
"""

import os
from datetime import datetime, timedelta
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
import json

class PaperTradingBot:
    def __init__(self, initial_balance=10000):
        self.config = DEFAULT_CONFIG.copy()
        self.config["use_real_execution"] = False  # Simulation!
        self.config["simulated_balance"] = initial_balance

        self.ta = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals", "astrology"],
            debug=True,
            config=self.config
        )

        self.trade_history = []
        self.start_balance = initial_balance

    def run_daily_analysis(self, asset, date):
        """Führe tägliche Analyse durch"""
        print(f"\n{'='*60}")
        print(f"Date: {date} | Asset: {asset}")
        print('='*60)

        # Analyse durchführen
        state, decision = self.ta.propagate(asset, date)

        # Trade ausführen wenn Signal
        if decision["action"] in ["BUY", "SELL"]:
            result = self.ta.execute_trade(
                asset=asset,
                action=decision["action"],
                size=0.1  # 0.1 BTC pro Trade
            )

            # Trade History speichern
            trade = {
                "date": date,
                "asset": asset,
                "action": decision["action"],
                "size": 0.1,
                "price": result.get("average_price", 0),
                "success": result.get("success", False),
                "astrology_signal": state.get("astrology_data", {}).get("signal", {}),
            }
            self.trade_history.append(trade)

            print(f"\n💰 TRADE EXECUTED:")
            print(f"   {decision['action']} {trade['size']} {asset}")
            print(f"   Price: ${trade['price']:.2f}")

        # Account Status
        account = self.ta.executor.get_account_value()
        pnl = account["account_value"] - self.start_balance
        pnl_pct = (pnl / self.start_balance) * 100

        print(f"\n📈 Account Status:")
        print(f"   Value: ${account['account_value']:,.2f}")
        print(f"   P&L: ${pnl:,.2f} ({pnl_pct:.2f}%)")

        return decision, result if decision["action"] in ["BUY", "SELL"] else None

    def save_results(self, filename="paper_trading_results.json"):
        """Speichere Ergebnisse"""
        account = self.ta.executor.get_account_value()

        results = {
            "start_balance": self.start_balance,
            "end_balance": account["account_value"],
            "total_pnl": account["account_value"] - self.start_balance,
            "pnl_percent": ((account["account_value"] - self.start_balance) / self.start_balance) * 100,
            "total_trades": len(self.trade_history),
            "trades": self.trade_history
        }

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Results saved to {filename}")
        return results

# =====================
# PAPER TRADING RUN
# =====================

if __name__ == "__main__":
    bot = PaperTradingBot(initial_balance=10000)

    # Test über 7 Tage
    start_date = datetime(2026, 1, 1)

    for i in range(7):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        bot.run_daily_analysis("BTC", date)

    # Speichere Ergebnisse
    results = bot.save_results()

    print("\n" + "="*60)
    print("PAPER TRADING SUMMARY")
    print("="*60)
    print(f"Start Balance: ${results['start_balance']:,.2f}")
    print(f"End Balance: ${results['end_balance']:,.2f}")
    print(f"Total P&L: ${results['total_pnl']:,.2f} ({results['pnl_percent']:.2f}%)")
    print(f"Total Trades: {results['total_trades']}")
```

**Ausführen:**
```bash
python paper_trading.py
```

### **Paper Trading Metrics Tracking**

**Erstelle:** `analyze_paper_trading.py`

```python
"""Analysiere Paper Trading Ergebnisse"""

import json
import pandas as pd

# Lade Results
with open("paper_trading_results.json") as f:
    results = json.load(f)

trades = pd.DataFrame(results["trades"])

# Metriken berechnen
total_trades = len(trades)
winning_trades = len(trades[trades["success"] == True])
win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

print("="*60)
print("PAPER TRADING ANALYSIS")
print("="*60)
print(f"Total Trades: {total_trades}")
print(f"Win Rate: {win_rate:.1f}%")
print(f"Total P&L: ${results['total_pnl']:.2f}")
print(f"ROI: {results['pnl_percent']:.2f}%")

# Astrology Signal Analysis
if not trades.empty:
    print("\nAstrology Signals:")
    for _, trade in trades.iterrows():
        signal = trade.get("astrology_signal", {})
        print(f"  {trade['date']}: {signal.get('overall_signal', 'N/A')} "
              f"(conf: {signal.get('confidence', 0):.1f}/10)")
```

---

## 📈 **Phase 3: Backtesting**

Backtesting = Testing mit historischen Daten.

### **Simple Backtesting Setup**

**Erstelle:** `backtest.py`

```python
"""
Backtesting Script

Teste die Strategie mit historischen Daten.
WICHTIG: TradingAgents nutzt Live-API-Calls für Daten,
daher müssen wir Mock-Daten oder historische API-Responses nutzen.
"""

from datetime import datetime, timedelta
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
import pandas as pd
import matplotlib.pyplot as plt

class Backtester:
    def __init__(self, start_date, end_date, initial_balance=10000):
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")

        config = DEFAULT_CONFIG.copy()
        config["use_real_execution"] = False
        config["simulated_balance"] = initial_balance

        self.ta = TradingAgentsGraph(
            selected_analysts=["astrology"],  # Nur Astrology für Speed
            debug=False,
            config=config
        )

        self.results = []

    def run_backtest(self, asset="BTC"):
        """Führe Backtest durch"""
        current_date = self.start_date

        while current_date <= self.end_date:
            date_str = current_date.strftime("%Y-%m-%d")

            print(f"Testing {date_str}...")

            try:
                state, decision = self.ta.propagate(asset, date_str)

                # Trade ausführen
                result = None
                if decision["action"] in ["BUY", "SELL"]:
                    result = self.ta.executor.place_order(
                        asset=asset,
                        side=decision["action"].lower(),
                        size=0.1,
                        order_type="market",
                        price=50000  # Mock price
                    )

                # Speichere Ergebnis
                account = self.ta.executor.get_account_value()
                self.results.append({
                    "date": date_str,
                    "action": decision["action"],
                    "account_value": account["account_value"],
                    "astro_signal": state.get("astrology_data", {}).get("signal", {}).get("overall_signal", "neutral"),
                })

            except Exception as e:
                print(f"  Error: {e}")

            current_date += timedelta(days=1)

    def plot_results(self):
        """Plotte Backtest Ergebnisse"""
        df = pd.DataFrame(self.results)

        plt.figure(figsize=(12, 6))
        plt.plot(df["date"], df["account_value"])
        plt.title("Backtest: Account Value Over Time")
        plt.xlabel("Date")
        plt.ylabel("Account Value ($)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("backtest_results.png")
        print("✅ Chart saved to backtest_results.png")

# RUN BACKTEST
if __name__ == "__main__":
    backtester = Backtester(
        start_date="2026-01-01",
        end_date="2026-01-30",
        initial_balance=10000
    )

    backtester.run_backtest("BTC")
    backtester.plot_results()
```

**Ausführen:**
```bash
pip install matplotlib pandas  # Falls noch nicht installiert
python backtest.py
```

---

## 🚀 **Phase 4: Live Trading**

**⚠️ NUR NACH ERFOLGREICHEN TESTS!**

### **Checkliste vor Live Trading:**

- [ ] ✅ Alle technischen Tests bestanden
- [ ] ✅ Paper Trading min. 1 Woche erfolgreich
- [ ] ✅ Backtest zeigt positive Ergebnisse
- [ ] ✅ Hyperliquid Testnet erfolgreich getestet
- [ ] ✅ Risk Management konfiguriert
- [ ] ✅ Stop-Loss Strategie definiert
- [ ] ✅ Position Sizing berechnet
- [ ] ✅ Monitoring Setup bereit

### **Schritt 1: Hyperliquid Testnet**

```bash
# 1. Erstelle Hyperliquid Account
# Gehe zu: https://app.hyperliquid.xyz/

# 2. Wechsle zu TESTNET (oben rechts)

# 3. Generiere API Key
# API Tab → Generate API Key → Kopiere Private Key

# 4. Füge zu .env hinzu
echo "HYPERLIQUID_SECRET_KEY=0xDEIN_PRIVATE_KEY_HIER" >> .env
echo "HYPERLIQUID_TESTNET=true" >> .env
```

### **Schritt 2: Testnet Trading Test**

**Erstelle:** `test_hyperliquid_testnet.py`

```python
"""Test Real Hyperliquid Testnet Trading"""

from tradingagents.execution import HyperliquidExecutor
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

print("Testing Hyperliquid TESTNET Connection...")

# Test 1: Executor Connection
try:
    executor = HyperliquidExecutor(testnet=True)
    print("✅ Connected to Hyperliquid Testnet")

    # Get account info
    account = executor.get_account_value()
    print(f"   Account Value: ${account['account_value']:,.2f}")
    print(f"   Available Margin: ${account['available_margin']:,.2f}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("   Check your .env file and API key!")
    exit(1)

# Test 2: Small Test Order
print("\nPlacing test order (SMALL SIZE)...")
try:
    result = executor.place_order(
        asset="BTC",
        side="buy",
        size=0.001,  # Very small test size!
        order_type="market"
    )

    if result["success"]:
        print(f"✅ Test order placed successfully!")
        print(f"   Order ID: {result['order_id']}")
        print(f"   Filled: {result['filled_size']} BTC")
        print(f"   Price: ${result['average_price']:.2f}")

        # Close position immediately
        print("\nClosing test position...")
        close_result = executor.place_order(
            asset="BTC",
            side="sell",
            size=0.001,
            order_type="market",
            reduce_only=True
        )

        if close_result["success"]:
            print("✅ Position closed")

    else:
        print(f"❌ Order failed: {result.get('error')}")

except Exception as e:
    print(f"❌ Order error: {e}")

print("\n" + "="*60)
print("Testnet Test Complete!")
print("If successful, you can proceed to TradingAgents integration.")
print("="*60)
```

**Ausführen:**
```bash
python test_hyperliquid_testnet.py
```

### **Schritt 3: TradingAgents mit Testnet**

**Erstelle:** `live_testnet_bot.py`

```python
"""
Live Trading Bot (TESTNET)

Nutzt echte Hyperliquid Testnet API aber kein echtes Geld.
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv
import time

load_dotenv()

# Konfiguration
config = DEFAULT_CONFIG.copy()
config["use_real_execution"] = True  # Real Hyperliquid!
config["hyperliquid_testnet"] = True  # Aber Testnet!

# Initialize Bot
print("Initializing Trading Bot with Hyperliquid TESTNET...")
ta = TradingAgentsGraph(
    selected_analysts=["market", "astrology"],
    debug=True,
    config=config
)

print(f"✅ Bot initialized with {type(ta.executor).__name__}")

# Run single analysis
print("\nRunning analysis...")
state, decision = ta.propagate("BTC", "2026-01-04")

print(f"\nDecision: {decision['action']}")

# Execute if signal
if decision["action"] in ["BUY", "SELL"]:
    print(f"\n⚡ Executing {decision['action']} on TESTNET...")

    result = ta.execute_trade(
        asset="BTC",
        action=decision["action"],
        size=0.01  # Small size
    )

    if result["success"]:
        print(f"✅ Order placed on Hyperliquid Testnet!")
        print(f"   Order ID: {result.get('order_id')}")
    else:
        print(f"❌ Order failed: {result.get('error')}")

# Account Status
account = ta.executor.get_account_value()
print(f"\n📊 Account: ${account['account_value']:,.2f}")
```

### **Schritt 4: Mainnet (VORSICHTIG!)**

**Erst nach mind. 1 Woche erfolgreichem Testnet Trading!**

```python
# In .env:
HYPERLIQUID_TESTNET=false  # ⚠️ MAINNET!

# In config:
config["use_real_execution"] = True
config["hyperliquid_testnet"] = False  # REAL MONEY!

# ⚠️ WICHTIG:
# - Starte mit KLEINEN Positionen (0.001 BTC)
# - Setze Stop-Loss Limits
# - Überwache 24/7
# - Habe Kill-Switch bereit
```

---

## 📡 **Monitoring & Maintenance**

### **Monitoring Setup**

**Erstelle:** `monitor.py`

```python
"""
Trading Bot Monitor

Überwacht laufenden Bot und sendet Alerts.
"""

import time
from datetime import datetime
from tradingagents.execution import HyperliquidExecutor

class BotMonitor:
    def __init__(self, executor):
        self.executor = executor
        self.alerts = []

    def check_health(self):
        """Health Check"""
        try:
            account = self.executor.get_account_value()

            # Check 1: Account Value
            if account["account_value"] < 1000:
                self.alert("⚠️ Low account value!")

            # Check 2: Liquidation Risk (if applicable)
            if account.get("margin_used", 0) > account["account_value"] * 0.8:
                self.alert("🚨 HIGH LIQUIDATION RISK!")

            return True
        except Exception as e:
            self.alert(f"❌ Health check failed: {e}")
            return False

    def alert(self, message):
        """Send Alert"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert = f"[{timestamp}] {message}"
        print(alert)
        self.alerts.append(alert)

        # TODO: Send to Telegram/Email/SMS

    def monitor_loop(self, interval=60):
        """Continuous monitoring"""
        while True:
            self.check_health()
            time.sleep(interval)

# Usage:
if __name__ == "__main__":
    executor = HyperliquidExecutor(testnet=True)
    monitor = BotMonitor(executor)
    monitor.monitor_loop(interval=60)  # Check every minute
```

### **Logging Setup**

**Erstelle:** `setup_logging.py`

```python
"""Setup comprehensive logging"""

import logging
import os
from datetime import datetime

def setup_logging():
    """Configure logging for trading bot"""

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Log filename with timestamp
    log_file = f"logs/trading_bot_{datetime.now().strftime('%Y%m%d')}.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )

    return logging.getLogger("TradingBot")

# Usage in your bot:
# logger = setup_logging()
# logger.info("Bot started")
# logger.warning("Low balance!")
# logger.error("Trade failed!")
```

---

## 🔧 **Troubleshooting**

### **Häufige Probleme:**

#### **1. "OpenAI API Key not found"**
```bash
# Lösung:
echo "OPENAI_API_KEY=sk-..." >> .env
source .env  # Linux/Mac
```

#### **2. "Hyperliquid connection failed"**
```bash
# Prüfe:
1. Ist HYPERLIQUID_SECRET_KEY korrekt?
2. Ist es ein testnet oder mainnet key?
3. Ist hyperliquid-python-sdk installiert?

pip install --upgrade hyperliquid-python-sdk
```

#### **3. "Kerykeion import error"**
```bash
pip install --upgrade kerykeion
# Fallback:
pip install kerykeion==4.14.0
```

#### **4. "Insufficient balance"**
```bash
# Für Testnet:
# Gehe zu Hyperliquid Testnet Faucet und hole Testnet-Funds

# Für Simulation:
config["simulated_balance"] = 100000  # Erhöhe Balance
```

---

## 📝 **Quick Reference**

### **Wichtige Dateien:**

| Datei | Zweck |
|-------|-------|
| `.env` | API Keys (NIEMALS committen!) |
| `.gitignore` | Verhindert Commit von .env |
| `default_config.py` | Bot Konfiguration |
| `astrology_rules.yaml` | Astrologische Trading-Regeln |
| `hyperliquid_config.yaml` | Risk Management Settings |

### **Test Commands:**

```bash
# Basis Tests
python test_astrology_integration.py
python test_complete_system.py

# Paper Trading
python paper_trading.py

# Backtesting
python backtest.py

# Testnet Trading
python test_hyperliquid_testnet.py
python live_testnet_bot.py
```

### **Safety Commands:**

```bash
# Kill all running bots
pkill -f "python.*trading"

# Close all positions (emergency)
python -c "
from tradingagents.execution import HyperliquidExecutor
executor = HyperliquidExecutor(testnet=True)
# Close all positions manually
"
```

---

## ✅ **Final Checklist**

Vor Live Trading (Mainnet):

- [ ] Alle Tests bestanden (technical, paper, backtest)
- [ ] Testnet Trading erfolgreich (min. 1 Woche)
- [ ] `.env` ist in `.gitignore`
- [ ] API Keys sind sicher gespeichert
- [ ] Risk Management konfiguriert
- [ ] Stop-Loss Strategie definiert
- [ ] Monitoring Setup aktiv
- [ ] Emergency Stop-Mechanismus vorhanden
- [ ] Klein anfangen (<$100 Exposure)
- [ ] 24/7 Überwachung möglich

---

**Viel Erfolg mit deinem Trading Bot! 🚀**

*Disclaimer: Trading ist riskant. Nutze nur Geld, das du verlieren kannst. Dieser Bot ist experimentell.*
