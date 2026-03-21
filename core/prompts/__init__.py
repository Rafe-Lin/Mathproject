# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/prompts
功能說明 (Description): Prompt 構建器模組
執行語法 (Usage): from core.prompts import PromptBuilder
版本資訊 (Version): V2.1 (Complete Implementation)
更新日期 (Date): 2026-01-30
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

from .prompt_builder import (
    PromptBuilder,
    BARE_MINIMAL_PROMPT,
    UNIVERSAL_GEN_CODE_PROMPT,
)

__all__ = [
    'PromptBuilder',
    'BARE_MINIMAL_PROMPT',
    'UNIVERSAL_GEN_CODE_PROMPT',
]

