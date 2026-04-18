# 中學數學自適應學習系統（RAG × PPO）

## 基本資訊

-   報告日期：2026-03-26
-   階段：Phase 2 Integration
-   目標：整合 RAG 診斷 + PPO 技能路由

------------------------------------------------------------------------

## 今日完成項目

### 系統層

-   Phase 1 rule-based progression ✅
-   PPO routing（stay/remediate/return）✅
-   Controller（trigger/lock/return/bridge）✅
-   RAG diagnosis mapping layer ✅
-   PPO policy findings mapping layer ✅
-   routing timeline + summary ✅
-   reward observability ✅
-   E2E 測試通過 ✅

------------------------------------------------------------------------

## 系統架構

Student → RAG → Mapping → Controller → PPO → Skill → 題目 → 下一題

------------------------------------------------------------------------

## 同學三（RAG）整合

-   hybrid retrieval 保留
-   新增 mapping layer：
    -   concept → prerequisite skill
    -   輸出 diagnosis packet

------------------------------------------------------------------------

## 同學二（PPO）整合

-   PPO 作為 skill routing policy
-   action space：stay / remediate / return
-   findings → mapping：
    -   trigger hints
    -   reward shaping
    -   action prior

------------------------------------------------------------------------

## 已達成能力

-   跨技能補救（polynomial → integer）
-   return + bridge 機制
-   完整 decision trace
-   timeline / summary 分析

------------------------------------------------------------------------

## 尚未完成

-   系統 ablation 實驗
-   參數校準
-   數據集建構

------------------------------------------------------------------------

## 下一步實驗

### 組別

-   baseline
-   RAG only
-   PPO only
-   full system

### 指標

-   accuracy
-   fail_streak
-   remediation_count
-   return_rate
-   avg_reward

------------------------------------------------------------------------

## 結論

已完成系統整合，下一階段進入實驗驗證。
