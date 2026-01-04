"""
Astrology Analyst Agent

Provides astrological analysis for financial trading based on planetary positions and aspects.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from tradingagents.astrology.calculator import PlanetaryCalculator
from tradingagents.astrology.aspects import AspectDetector
from tradingagents.astrology.rules_engine import AstrologyRulesEngine
import os


def create_astrology_analyst(llm):
    """
    Create the Astrology Analyst agent node.

    Args:
        llm: Language model for generating analysis reports

    Returns:
        Astrology analyst node function
    """

    def astrology_analyst_node(state):
        """
        Astrology analyst node that calculates planetary positions,
        detects aspects, and generates trading signals.

        Args:
            state: Current agent state with trade_date and company_of_interest

        Returns:
            Updated state with astrology_report and astrology_data
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # Initialize astrology components
        calculator = PlanetaryCalculator()
        detector = AspectDetector(orb_tolerance=8)

        # Determine rules file path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
        rules_path = os.path.join(project_root, "config", "astrology_rules.yaml")

        rules_engine = AstrologyRulesEngine(rules_path)

        # Calculate astrological data
        try:
            chart = calculator.get_chart(current_date)
            aspects = detector.detect_aspects(chart)
            positions = calculator.get_planetary_positions(chart)
            signal = rules_engine.evaluate_signal(aspects, positions)

            # Get strongest aspects for report
            major_aspects = detector.filter_major_aspects(aspects)
            strongest_aspects = detector.get_strongest_aspects(major_aspects, limit=5)

            # Format aspects for display
            aspects_text = "\n".join([
                f"- {detector.format_aspect(asp)}"
                for asp in strongest_aspects
            ])

            # Format planetary positions summary
            positions_summary = calculator.get_summary(chart)

        except Exception as e:
            # Handle errors gracefully
            aspects_text = f"Error calculating aspects: {str(e)}"
            positions_summary = "Unable to calculate positions"
            signal = {
                "overall_signal": "neutral",
                "confidence": 0,
                "individual_signals": [],
                "summary": f"Astrological calculation error: {str(e)}"
            }
            aspects = []
            positions = {}

        # Create system message with astrological context
        system_message = f"""You are an astrological analyst for financial markets. Your role is to interpret planetary configurations and provide timing insights for trading decisions.

**Astrological Analysis for {current_date}**

Overall Assessment: **{signal['overall_signal'].upper()}**
Confidence Level: **{signal['confidence']}/10**

**Key Planetary Aspects** (Most Significant):
{aspects_text}

**Planetary Positions**:
{positions_summary}

**Signal Breakdown**:
- Bullish signals: {signal.get('scores', {}).get('bullish', 0)}
- Bearish signals: {signal.get('scores', {}).get('bearish', 0)}
- Neutral signals: {signal.get('scores', {}).get('neutral', 0)}

**Individual Signals**:
{self._format_individual_signals(signal.get('individual_signals', []))}

**Your Task**:
Provide a detailed astrological market timing report including:

1. **Astrological Overview**: Summarize the key planetary configurations for this date
2. **Market Timing Implications**: How these aspects traditionally correlate with market movements
3. **Key Aspects Analysis**: Deep dive into the 2-3 most significant aspects
4. **Trading Recommendation**: Based on astrological timing, suggest whether conditions favor buying, selling, or holding
5. **Risk Factors**: Note any challenging aspects that could indicate volatility or reversals
6. **Summary Table**: Provide a markdown table summarizing the key astrological factors

Remember to:
- Be specific about the astrological configurations
- Connect aspects to traditional market correlations (e.g., Jupiter-Venus trines historically favor appreciation)
- Consider both harmonious and challenging aspects
- Provide nuanced analysis, not just "bullish" or "bearish"
- Reference specific planetary energies (e.g., "Saturn's restrictive influence", "Jupiter's expansive nature")
"""

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the astrological data provided to generate insights for trading decisions."
                " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                " {system_message}"
                " Current date: {current_date}, Asset: {ticker}"
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm
        result = chain.invoke(state["messages"])

        # Extract report content
        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "astrology_report": report,
            "astrology_data": {
                "aspects": aspects,
                "positions": positions,
                "signal": signal,
            },
        }

    def _format_individual_signals(signals):
        """Format individual signals for display."""
        if not signals:
            return "No specific signals detected"

        lines = []
        for sig in signals[:8]:  # Limit to top 8 signals
            lines.append(
                f"  • {sig['source']}: {sig['signal'].upper()} "
                f"(strength {sig['strength']}/10) - {sig['reasoning']}"
            )
        return "\n".join(lines)

    # Attach helper method
    astrology_analyst_node._format_individual_signals = _format_individual_signals

    return astrology_analyst_node
