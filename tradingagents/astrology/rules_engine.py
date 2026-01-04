"""
Astrology Rules Engine

Converts astrological configurations into trading signals based on user-defined rules.
"""

import yaml
import os
from typing import Dict, List, Optional


class AstrologyRulesEngine:
    """
    Evaluates astrological data against user-defined rules to generate trading signals.

    Reads rules from a YAML configuration file and applies them to aspects
    and planetary positions to produce bullish/bearish signals.
    """

    def __init__(self, rules_file_path: str):
        """
        Initialize the rules engine.

        Args:
            rules_file_path: Path to YAML file containing astrological trading rules
        """
        self.rules_file_path = rules_file_path
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict:
        """
        Load rules from YAML file.

        Returns:
            Dict containing aspect_rules, position_rules, and settings
        """
        if not os.path.exists(self.rules_file_path):
            # Return default empty rules if file doesn't exist
            return {
                "aspect_rules": {},
                "position_rules": {},
                "settings": {
                    "orb_tolerance": 8,
                    "timezone": "UTC"
                }
            }

        with open(self.rules_file_path, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f)

        return rules or {}

    def evaluate_signal(
        self,
        aspects: List[Dict],
        positions: Optional[Dict] = None
    ) -> Dict:
        """
        Convert astrological data into trading signals.

        Args:
            aspects: List of detected aspects
            positions: Dict of planetary positions (optional)

        Returns:
            Dict with overall_signal, confidence, and individual_signals
        """
        signals = []

        # Evaluate aspect-based rules
        for aspect in aspects:
            signal = self._evaluate_aspect(aspect)
            if signal:
                signals.append(signal)

        # Evaluate position-based rules (if positions provided)
        if positions:
            position_signals = self._evaluate_positions(positions)
            signals.extend(position_signals)

        # Aggregate all signals
        return self._aggregate_signals(signals)

    def _evaluate_aspect(self, aspect: Dict) -> Optional[Dict]:
        """
        Evaluate a single aspect against rules.

        Args:
            aspect: Aspect dict with planet1, planet2, aspect_type

        Returns:
            Signal dict or None if no matching rule
        """
        # Create rule key in format: planet1-planet2-aspect_type
        rule_key = f"{aspect['planet1']}-{aspect['planet2']}-{aspect['aspect_type']}"

        # Also try reverse order (planet2-planet1-aspect_type)
        reverse_key = f"{aspect['planet2']}-{aspect['planet1']}-{aspect['aspect_type']}"

        aspect_rules = self.rules.get("aspect_rules", {})

        # Check for matching rule
        if rule_key in aspect_rules:
            rule = aspect_rules[rule_key]
        elif reverse_key in aspect_rules:
            rule = aspect_rules[reverse_key]
        else:
            return None

        return {
            "signal": rule["signal"],  # "bullish", "bearish", or "neutral"
            "strength": rule["strength"],  # 0-10
            "reasoning": rule["description"],
            "source": f"{aspect['planet1']}-{aspect['planet2']} {aspect['aspect_type']}",
        }

    def _evaluate_positions(self, positions: Dict) -> List[Dict]:
        """
        Evaluate planetary positions against rules.

        Args:
            positions: Dict of planetary positions

        Returns:
            List of signals from position rules
        """
        signals = []
        position_rules = self.rules.get("position_rules", {})

        for planet, data in positions.items():
            sign = data.get("sign", "").lower()
            rule_key = f"{planet}-{sign}"

            if rule_key in position_rules:
                rule = position_rules[rule_key]
                signals.append({
                    "signal": rule["signal"],
                    "strength": rule["strength"],
                    "reasoning": rule["description"],
                    "source": f"{planet.capitalize()} in {sign.capitalize()}",
                })

        return signals

    def _aggregate_signals(self, signals: List[Dict]) -> Dict:
        """
        Combine individual signals into an overall assessment.

        Args:
            signals: List of individual signal dicts

        Returns:
            Dict with overall_signal, confidence, and individual_signals
        """
        if not signals:
            return {
                "overall_signal": "neutral",
                "confidence": 5.0,
                "individual_signals": [],
                "summary": "No astrological signals detected"
            }

        # Calculate weighted scores
        bullish_score = sum(
            s["strength"] for s in signals if s["signal"] == "bullish"
        )
        bearish_score = sum(
            s["strength"] for s in signals if s["signal"] == "bearish"
        )
        neutral_score = sum(
            s["strength"] for s in signals if s["signal"] == "neutral"
        )

        total = bullish_score + bearish_score + neutral_score

        # Determine overall signal
        if total == 0:
            overall = "neutral"
            confidence = 5.0
        elif bullish_score > bearish_score and bullish_score > neutral_score:
            overall = "bullish"
            confidence = min((bullish_score / total) * 10, 10.0)
        elif bearish_score > bullish_score and bearish_score > neutral_score:
            overall = "bearish"
            confidence = min((bearish_score / total) * 10, 10.0)
        else:
            overall = "neutral"
            confidence = 5.0

        # Create summary
        summary = self._create_summary(signals, overall, confidence)

        return {
            "overall_signal": overall,
            "confidence": round(confidence, 2),
            "individual_signals": signals,
            "summary": summary,
            "scores": {
                "bullish": bullish_score,
                "bearish": bearish_score,
                "neutral": neutral_score,
            }
        }

    def _create_summary(
        self,
        signals: List[Dict],
        overall: str,
        confidence: float
    ) -> str:
        """
        Create a human-readable summary of the astrological assessment.

        Args:
            signals: List of individual signals
            overall: Overall signal direction
            confidence: Confidence score

        Returns:
            Summary string
        """
        bullish_count = sum(1 for s in signals if s["signal"] == "bullish")
        bearish_count = sum(1 for s in signals if s["signal"] == "bearish")

        summary = f"Astrological assessment is {overall.upper()} "
        summary += f"with {confidence:.1f}/10 confidence. "
        summary += f"Detected {len(signals)} signals: "
        summary += f"{bullish_count} bullish, {bearish_count} bearish."

        return summary

    def reload_rules(self):
        """Reload rules from file (useful for updating rules without restart)."""
        self.rules = self._load_rules()
