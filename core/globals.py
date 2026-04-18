# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/globals.py
功能說明 (Description): 全域變數定義檔，用於存放跨模組共用的變數 (如 TASK_QUEUES)，以解決 Circular Import 問題。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
import queue

# 用於暫存正在執行的任務佇列 (簡易版 In-memory store)
# Key: task_id, Value: queue.Queue
TASK_QUEUES = {}