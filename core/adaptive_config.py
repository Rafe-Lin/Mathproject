# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): adaptive_config.py
功能說明 (Description): 儲存自適應學習引擎所需的所有常數與設定值。
=============================================================================
"""

# --- 能力值範圍 ---
ABILITY_DEFAULT, ABILITY_MAX = 20.0, 200.0  # 綜合能力 A (0-200)
CONCEPT_DEFAULT, CONCEPT_MAX = 20.0, 100.0  # 觀念能力 U (0-100)
CALCULATION_DEFAULT, CALCULATION_MAX = 20.0, 100.0 # 計算熟練度 C (0-100)

# --- 作答時間因子 ---
AVG_ANSWER_TIME_SECONDS = 60  # 平均作答時間 (秒)
MAX_ANSWER_TIME_SECONDS = 180 # 最大作答時間 (秒)

# 時間因子 T_factor
T_FACTOR_FAST = 1.2    # 答題快
T_FACTOR_NORMAL = 1.0  # 答題速度正常
T_FACTOR_SLOW = 0.8    # 答題慢

# --- 懲罰因子 ---
ERROR_PENALTY_FACTOR = 0.6 # 答錯時的基礎懲罰係數

# --- 推薦系統 (RS) 規則權重 ---
W_LEVEL = 0.4       # 規則 1: 難度適中性
W_NON_REPEAT = 0.3  # 規則 2: 變化性 (避免重複)
W_CONCEPT = 0.15    # 規則 3: 觀念強化
W_CALCULATION = 0.1 # 規則 4: 計算強化
W_IMPORTANCE = 0.05 # 規則 5: 知識點重要性

# RS 分數計算中的相關參數
RS_LEVEL_RANGE = 20  # 學生能力 A 值上下浮動的範圍
RS_NON_REPEAT_HISTORY_COUNT = 5 # 檢查最近 5 題避免重複
