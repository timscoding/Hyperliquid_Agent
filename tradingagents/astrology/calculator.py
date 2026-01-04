"""
Planetary Calculator Module

Calculates planetary positions for a given date using Kerykeion.
"""

from kerykeion import AstrologicalSubject
from datetime import datetime
import pytz
from typing import Dict, Optional


class PlanetaryCalculator:
    """
    Calculates planetary positions for financial market timing.

    Uses Kerykeion to compute astrological charts and extract
    planetary positions for trading analysis.
    """

    def __init__(self, timezone: str = "UTC", location: Optional[Dict] = None):
        """
        Initialize the planetary calculator.

        Args:
            timezone: Timezone for calculations (default: UTC)
            location: Dict with city, nation, lng, lat, tz_str
                     Default: NYSE coordinates (New York)
        """
        self.timezone = pytz.timezone(timezone)

        # Default: NYSE coordinates for market timing
        self.location = location or {
            "city": "New York",
            "nation": "US",
            "lng": -74.0060,
            "lat": 40.7128,
            "tz_str": "America/New_York"
        }

    def get_chart(self, trade_date: str) -> AstrologicalSubject:
        """
        Create an astrological chart for the given trade date.

        Args:
            trade_date: Date in format "YYYY-MM-DD"

        Returns:
            AstrologicalSubject object with calculated positions
        """
        dt = datetime.strptime(trade_date, "%Y-%m-%d")
        dt = self.timezone.localize(dt.replace(hour=12, minute=0))

        subject = AstrologicalSubject(
            name="Market",
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            **self.location
        )

        return subject

    def get_planetary_positions(self, subject: AstrologicalSubject) -> Dict:
        """
        Extract planetary positions from an astrological chart.

        Args:
            subject: AstrologicalSubject with calculated positions

        Returns:
            Dict with planetary data (sign, position, retrograde status)
        """
        planets = {}

        # Extract data for each planet
        planet_names = [
            "sun", "moon", "mercury", "venus", "mars",
            "jupiter", "saturn", "uranus", "neptune", "pluto"
        ]

        for planet_name in planet_names:
            planet_data = getattr(subject, planet_name, None)
            if planet_data:
                planets[planet_name] = {
                    "sign": planet_data.get("sign", ""),
                    "position": planet_data.get("position", 0.0),
                    "retrograde": planet_data.get("retrograde", False),
                    "quality": planet_data.get("quality", ""),
                    "element": planet_data.get("element", ""),
                }

        return planets

    def get_summary(self, subject: AstrologicalSubject) -> str:
        """
        Get a human-readable summary of planetary positions.

        Args:
            subject: AstrologicalSubject with calculated positions

        Returns:
            Formatted string summary
        """
        positions = self.get_planetary_positions(subject)

        summary_lines = []
        for planet, data in positions.items():
            retrograde_marker = " (R)" if data["retrograde"] else ""
            summary_lines.append(
                f"{planet.capitalize()}: {data['position']:.2f}° {data['sign']}{retrograde_marker}"
            )

        return "\n".join(summary_lines)
