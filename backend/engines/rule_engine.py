"""
Rule Engine - Backward Compatibility Module

This module provides backward compatibility for code that imports from
backend.engines.rule_engine. The actual implementation is in enhanced_rule_engine.py.

Old import patterns still work:
    from backend.engines.rule_engine import RuleEngine
    from backend.engines.rule_engine import RuleResult, RiskLevel
"""

# Re-export everything from enhanced_rule_engine for backward compatibility
from backend.engines.enhanced_rule_engine import (
    EnhancedRuleEngine as RuleEngine,
    RuleResult,
    RiskLevel,
)

# Also export EnhancedRuleEngine directly if needed
from backend.engines.enhanced_rule_engine import EnhancedRuleEngine

__all__ = [
    'RuleEngine',
    'EnhancedRuleEngine',
    'RuleResult',
    'RiskLevel',
]
