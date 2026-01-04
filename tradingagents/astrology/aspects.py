"""
Aspect Detector Module

Detects astrological aspects between planets using Kerykeion.
"""

from kerykeion import AstrologicalSubject, AspectsFactory
from typing import List, Dict


class AspectDetector:
    """
    Detects astrological aspects between planets.

    Aspects are angular relationships between planets that indicate
    harmonious or challenging energies in astrological analysis.
    """

    # Major aspects and their angles
    MAJOR_ASPECTS = {
        "conjunction": 0,
        "opposition": 180,
        "trine": 120,
        "square": 90,
        "sextile": 60,
    }

    # Aspect interpretations for trading
    ASPECT_NATURE = {
        "conjunction": "neutral",  # Can be harmonious or challenging
        "trine": "harmonious",
        "sextile": "harmonious",
        "opposition": "challenging",
        "square": "challenging",
    }

    def __init__(self, orb_tolerance: int = 8):
        """
        Initialize the aspect detector.

        Args:
            orb_tolerance: Maximum orb (deviation in degrees) for aspect detection
        """
        self.orb_tolerance = orb_tolerance

    def detect_aspects(self, chart_subject: AstrologicalSubject) -> List[Dict]:
        """
        Detect all aspects in an astrological chart.

        Args:
            chart_subject: AstrologicalSubject with calculated planetary positions

        Returns:
            List of detected aspects with metadata
        """
        aspects_factory = AspectsFactory(chart_subject)

        detected = []
        for aspect in aspects_factory.all_aspects:
            # Extract aspect data
            aspect_data = {
                "planet1": aspect["p1_name"],
                "planet2": aspect["p2_name"],
                "aspect_type": aspect["aspect"],
                "orb": aspect["orbit"],
                "applying": aspect.get("applying", None),
                "nature": self.ASPECT_NATURE.get(aspect["aspect"], "neutral"),
            }

            detected.append(aspect_data)

        return detected

    def filter_major_aspects(self, aspects: List[Dict]) -> List[Dict]:
        """
        Filter to only major aspects (conjunction, opposition, trine, square, sextile).

        Args:
            aspects: List of all detected aspects

        Returns:
            List of major aspects only
        """
        return [
            aspect for aspect in aspects
            if aspect["aspect_type"] in self.MAJOR_ASPECTS
        ]

    def get_strongest_aspects(
        self,
        aspects: List[Dict],
        limit: int = 5
    ) -> List[Dict]:
        """
        Get the strongest aspects based on tightness of orb.

        Args:
            aspects: List of aspects
            limit: Maximum number of aspects to return

        Returns:
            List of strongest aspects sorted by orb (tightest first)
        """
        sorted_aspects = sorted(aspects, key=lambda x: abs(x["orb"]))
        return sorted_aspects[:limit]

    def get_harmonious_aspects(self, aspects: List[Dict]) -> List[Dict]:
        """
        Get only harmonious aspects (trine, sextile).

        Args:
            aspects: List of aspects

        Returns:
            List of harmonious aspects
        """
        return [
            aspect for aspect in aspects
            if aspect["nature"] == "harmonious"
        ]

    def get_challenging_aspects(self, aspects: List[Dict]) -> List[Dict]:
        """
        Get only challenging aspects (square, opposition).

        Args:
            aspects: List of aspects

        Returns:
            List of challenging aspects
        """
        return [
            aspect for aspect in aspects
            if aspect["nature"] == "challenging"
        ]

    def format_aspect(self, aspect: Dict) -> str:
        """
        Format an aspect for display.

        Args:
            aspect: Aspect dictionary

        Returns:
            Formatted string
        """
        applying_str = "applying" if aspect.get("applying") else "separating"
        return (
            f"{aspect['planet1'].capitalize()} "
            f"{aspect['aspect_type']} "
            f"{aspect['planet2'].capitalize()} "
            f"(orb: {aspect['orb']:.2f}°, {applying_str})"
        )
