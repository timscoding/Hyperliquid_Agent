# 🤖 TradingAgents - AI-Powered Cryptocurrency Trading System

**Research-backed astrological market timing combined with multi-agent AI for cryptocurrency trading on Hyperliquid DEX.**

---

## ✨ Features

### 🔮 **Advanced Astrology Analysis**
- **150+ Astrological Rules** - Research-backed planetary aspects, positions, lunar phases, and retrogrades
- **Crypto-Optimized** - Special weighting for Uranus (innovation), Neptune (speculation), Pluto (transformation)
- **Lunar Phase Tracking** - Full moons mark tops 55% of the time (research-backed)
- **Mercury Retrograde Detection** - Historically 1.5% lower returns during retrograde periods
- **Bitcoin Natal Chart Awareness** - Transits to Bitcoin's birth chart (Jan 3, 2009)
- **Enhanced Scoring** - Tight orb bonuses, applying aspect bonuses, crypto weight multipliers

### 🧠 **Multi-Agent AI System**
- **Specialized Analysts** - Astrology, Technical, Fundamental, Sentiment analysis
- **LangGraph Orchestration** - Coordinated decision-making
- **GPT-4o Integration** - Advanced reasoning for market analysis

### 📊 **Hyperliquid DEX Integration**
- **Testnet & Mainnet Support** - Safe testing before live trading
- **Market & Limit Orders** - Full order type support
- **Position Management** - Real-time position tracking
- **Risk Management** - Configurable position sizing and leverage

---

## 📚 Documentation

- **[Setup & Testing Guide](SETUP_AND_TESTING_GUIDE.md)** - Complete installation and testing walkthrough
- **[GitHub Models Setup](docs/GITHUB_MODELS_SETUP.md)** - Free API testing with GitHub Models
- **[Astrology Rules](config/astrology_rules.yaml)** - Full astrological rule configuration
- **[API Documentation](docs/API.md)** - API endpoints and usage (if applicable)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Git
- GitHub Account (for free API testing)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/timscoding/Hyperliquid_Agent.git
cd TradingAgents

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

**Minimum .env for testing:**
```bash
# GitHub Models (FREE for testing)
OPENAI_API_KEY=ghp_your_github_personal_access_token
OPENAI_API_BASE=https://models.inference.ai.azure.com

# Hyperliquid (optional for testing)
HYPERLIQUID_TESTNET=true
```

See [GitHub Models Setup Guide](docs/GITHUB_MODELS_SETUP.md) for detailed instructions.

### Run Tests

```bash
# Test astrology calculations
python -m pytest tests/test_astrology.py

# Test Hyperliquid connection (requires API key)
python -m pytest tests/test_hyperliquid.py

# Run full system test
python test_trading_system.py
```

### Run Agent

```bash
# Simulation mode (no real trades)
python main.py --mode simulation --ticker BTC

# Paper trading mode
python main.py --mode paper --ticker ETH

# Live trading (use with caution!)
python main.py --mode live --ticker SOL
```

---

## 🏗️ Architecture

```
TradingAgents/
├── tradingagents/
│   ├── agents/
│   │   └── analysts/
│   │       └── astrology_analyst.py    # Crypto-focused astrology analysis
│   ├── astrology/
│   │   ├── calculator.py               # Planetary calculations
│   │   ├── aspects.py                  # Aspect detection
│   │   └── rules_engine.py             # Enhanced scoring system
│   ├── execution/
│   │   └── hyperliquid_executor.py     # Hyperliquid DEX integration
│   └── graph/
│       └── trading_graph.py            # LangGraph orchestration
├── config/
│   └── astrology_rules.yaml            # 150+ astrological rules
├── tests/
│   └── test_astrology.py               # Comprehensive tests
└── docs/
    ├── SETUP_AND_TESTING_GUIDE.md      # Complete setup guide
    └── GITHUB_MODELS_SETUP.md          # Free API setup
```

---

## 🔮 Astrology System Overview

### Research-Backed Rules

Based on academic studies and crypto market analysis:

1. **Dichev & Janes (2001)** - Moon phase correlation study
2. **UC Berkeley Study** - Mercury retrograde S&P 500 impact
3. **Bramesh Technical Analysis** - Planetary cycles research
4. **Bitcoin Natal Chart Analysis** - Multiple astrologers
5. **Crypto Historical Events** - LUNA (lunar eclipse), FTX (lunar eclipse)

### Key Components

**Planetary Aspects** (120+ rules):
- Jupiter aspects → Expansion, bull markets
- Saturn aspects → Restriction, bear markets
- Uranus aspects → Innovation, volatility (crypto-critical)
- Neptune aspects → Speculation, bubbles
- Mars aspects → Momentum, flash crashes
- Moon aspects → Sentiment, volatility

**Planetary Positions** (44 rules):
- Planets in signs (e.g., Uranus in Aquarius = crypto golden age)
- Dignity (rulership, exaltation, fall, detriment)

**Lunar Phases** (10 rules):
- New Moon → Accumulation phase (bullish)
- Full Moon → Distribution phase (bearish, 55% top accuracy)
- Lunar Eclipse → Crisis indicator (LUNA, FTX crashes)

**Retrograde Periods** (8 rules):
- Mercury Retrograde → -1.5% returns, tech failures
- Venus Retrograde → Valuation reassessment
- Mars Retrograde → Momentum stall

### Scoring System

```python
Base Strength (0-10)
+ Tight Orb Bonus (+2 if orb < 3°)
+ Applying Aspect Bonus (+1 if approaching exact)
× Crypto Weight Multiplier (1.3x for Uranus, 1.2x for Neptune/Pluto, 1.15x for Moon)
= Final Strength (capped at 10)
```

**Signal Determination:**
- Bullish if: bullish_score > bearish_score AND bullish_score > neutral_score
- Confidence: Weighted ratio of dominant signal (0-10 scale)

---

## 🎯 Trading Assets Configuration

Edit `config/trading_assets.yaml`:

```yaml
trading_assets:
  - symbol: "BTC"
    max_position_pct: 30      # Max 30% of portfolio
    leverage: 1               # No leverage
    min_trade_size: 0.001     # Minimum 0.001 BTC

  - symbol: "ETH"
    max_position_pct: 20
    leverage: 1
    min_trade_size: 0.01

  - symbol: "SOL"
    max_position_pct: 15
    leverage: 1
    min_trade_size: 0.1
```

Hyperliquid uses simple symbols without pairs: `"BTC"`, not `"BTC-USD"`.

---

## ⚙️ Configuration

### LLM Models

**For Testing (Free):**
```python
# .env
OPENAI_API_KEY=ghp_...  # GitHub PAT
OPENAI_API_BASE=https://models.inference.ai.azure.com

# config
"deep_think_llm": "gpt-4o-mini"
"quick_think_llm": "gpt-4o-mini"
```

**For Production:**
```python
# .env
OPENAI_API_KEY=sk-proj-...  # Real OpenAI key

# config
"deep_think_llm": "gpt-4o"
"quick_think_llm": "gpt-4o-mini"
```

### Astrology Settings

Edit `config/astrology_rules.yaml`:

```yaml
settings:
  orb_tolerance: 8              # Aspect detection orb
  tight_orb_bonus: 2            # Bonus for orb < 3°
  applying_aspect_bonus: 1      # Bonus for applying aspects
  crypto_mode: true             # Enable crypto weighting

  crypto_weight_multipliers:
    uranus: 1.3                 # Innovation (crypto-critical)
    neptune: 1.2                # Speculation/bubbles
    pluto: 1.2                  # Transformation
    moon: 1.15                  # Sentiment/volatility
    mercury_retrograde: 1.25    # Tech failures
```

---

## 🧪 Testing Phases

### Phase 1: Local Testing
```bash
# No real money, test all components
python main.py --mode simulation --ticker BTC --date 2025-01-15
```

### Phase 2: Hyperliquid Testnet
```bash
# Testnet trading with fake money
HYPERLIQUID_TESTNET=true python main.py --mode paper --ticker ETH
```

### Phase 3: Small Live Positions
```bash
# Real money, small sizes
python main.py --mode live --ticker BTC --max-position 100
```

### Phase 4: Full Deployment
```bash
# Production with all assets
python main.py --mode live --config config/production.yaml
```

See [SETUP_AND_TESTING_GUIDE.md](SETUP_AND_TESTING_GUIDE.md) for detailed phase-by-phase instructions.

---

## 🔐 Security

**NEVER commit API keys!**

✅ **Correct:**
```bash
# .env (in .gitignore)
HYPERLIQUID_SECRET_KEY=0x...
OPENAI_API_KEY=sk-...
```

❌ **WRONG:**
```python
# Never hardcode in code!
api_key = "sk-abc123"  # ❌ DON'T DO THIS
```

**Additional Security:**
- Use Hyperliquid **testnet** first
- Start with small position sizes
- Set up **2FA** on all exchanges
- Use **read-only API keys** for testing
- Monitor trades with **alerts**

---

## 📊 Performance Metrics

The system tracks:
- **Win Rate** - Percentage of profitable trades
- **Sharpe Ratio** - Risk-adjusted returns
- **Max Drawdown** - Largest peak-to-trough decline
- **Average Hold Time** - Typical position duration
- **Astrology Signal Accuracy** - Backtested correlations

Detailed metrics available in `logs/performance/`

---

## 🤝 Contributing

We welcome contributions! Areas of interest:

1. **More Astrology Rules** - Additional planetary configurations
2. **Additional Analysts** - On-chain analysis, derivatives data
3. **Backtesting Engine** - Historical performance validation
4. **Risk Management** - Advanced position sizing algorithms
5. **Documentation** - Tutorials, examples, translations

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## ⚠️ Disclaimer

**This software is for educational and research purposes only.**

- Cryptocurrency trading involves substantial risk of loss
- Past performance does not guarantee future results
- Astrological analysis is not recognized by mainstream finance
- No financial advice is provided
- Use at your own risk
- Start with testnet and small positions

**The developers are not responsible for any financial losses incurred through use of this system.**

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Research Sources:
- Dichev & Janes (2001) - Lunar phase market correlation
- UC Berkeley - Mercury retrograde studies
- Bramesh Technical Analysis - Planetary cycles research
- W.D. Gann - Master Time Factor methods
- Financial Astrology Almanac - M.G. Bucholtz
- Bitcoin Natal Chart Analysis - Multiple astrologers

### Technologies:
- [LangChain](https://langchain.com) - Multi-agent orchestration
- [Kerykeion](https://github.com/g-battaglia/kerykeion) - Astrological calculations
- [Hyperliquid SDK](https://hyperliquid.xyz) - DEX integration
- [OpenAI GPT-4o](https://openai.com) - Language models

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/timscoding/Hyperliquid_Agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/timscoding/Hyperliquid_Agent/discussions)
- **Documentation**: [Full Docs](docs/)

---

**Built with 🔮 and 🤖 for the crypto community**

*"As above, so below; as the universe, so the soul." - Hermes Trismegistus*
