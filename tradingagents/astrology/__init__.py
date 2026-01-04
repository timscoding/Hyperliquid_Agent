"""
Astrology Module for TradingAgents

This module provides astrological analysis capabilities for financial trading,
including planetary position calculations, aspect detection, and trading signal generation
based on astrological configurations.
"""

from .calculator import PlanetaryCalculator
from .aspects import AspectDetector
from .rules_engine import AstrologyRulesEngine

__all__ = [
    "PlanetaryCalculator",
    "AspectDetector",
    "AstrologyRulesEngine",
]
