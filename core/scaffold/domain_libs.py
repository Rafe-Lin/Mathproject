# -*- coding: utf-8 -*-
"""
Re-export domain libs from prompts.domain_function_library for backward compatibility.
core.domain_functions and core.engine.scaler 依賴此路徑。
"""
from core.prompts.domain_function_library import (
    RadicalOps,
    IntegerOps,
    FractionOps,
)

__all__ = ["RadicalOps", "IntegerOps", "FractionOps"]
