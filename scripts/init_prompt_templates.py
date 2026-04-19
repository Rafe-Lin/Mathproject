# -*- coding: utf-8 -*-
"""
===========================================================
init_prompt_templates.py
Prompt Registry 初始化 / 版本同步腳本
===========================================================

【檔案用途】
本腳本負責將專案中的 AI 教學 Prompt，
由 YAML Registry（唯一真相來源，Source of Truth）
同步進資料庫 prompt_templates 資料表中。

此腳本的核心目的不是單純「補資料」，
而是作為 Prompt 的「版本同步工具」與「環境重建工具」。

-----------------------------------------------------------
【核心目標】
1. 讓新環境在沒有 prompt_templates 資料表時：
   - 自動建立資料表
   - 自動將 YAML 中的正式 Prompt 寫入資料庫

2. 讓既有環境在已有 prompt_templates 資料表時：
   - 將資料庫中的 Prompt 更新成目前 YAML 的正式版本
   - 補齊遺漏的 Prompt
   - 讓下一位接手者可快速同步到團隊目前統一版本

3. 建立可重建（reproducible）與可交接（handoff-ready）的
   Prompt 管理流程。

-----------------------------------------------------------
【唯一真相來源（Source of Truth）】
本專案的正式 Prompt 標準版本統一存放於：

    configs/prompts/prompt_registry.yaml

規則如下：
- YAML = 正式版本 / 團隊共識版本 / 可版控版本
- DB = 執行中版本 / 後台可覆蓋版本
- 若要發佈新的 Prompt 版本：
  必須先更新 prompt_registry.yaml
  再執行本腳本同步到資料庫

-----------------------------------------------------------
【執行模式說明】
本專案的 Prompt Bootstrap 分成兩種模式：

1. app.py 啟動時（保守模式）
   bootstrap_prompt_registry(update_existing=False)

   用途：
   - 只補缺少的 Prompt
   - 不覆蓋既有 DB 內容
   - 保護 admin UI / 管理員已手動調整的 Prompt

2. init_prompt_templates.py 執行時（同步模式）
   bootstrap_prompt_registry(update_existing=True)

   用途：
   - 若 DB 沒有 prompt → 新增
   - 若 DB 已有 prompt → 更新成 YAML 最新版本
   - 確保所有接手者都能同步到相同 Prompt 狀態

-----------------------------------------------------------
【團隊開發規則】
正式開發流程如下：

A. 平時測試 / 微調
- 可以在 Admin UI 或 DB 中修改 Prompt
- 用於測試教學效果或暫時調整

B. 確認版本後
- 將最終版本寫回 configs/prompts/prompt_registry.yaml

C. 發版 / 交接 / 重建環境
- 執行：
    python scripts/init_prompt_templates.py
- 讓資料庫中的 Prompt 與 YAML 統一

也就是說：

    YAML 是正式版本
    DB 是執行中狀態
    本腳本負責把 DB 同步到 YAML

-----------------------------------------------------------
【重要規則】
1. 不可把 DB 中的臨時修改直接視為正式版本
2. 正式 Prompt 更新後，必須同步更新 YAML
3. 若要交接給下一位學員，應以 YAML 為準
4. 本腳本執行後，應讓 DB prompt 狀態與 YAML 一致
5. 若 YAML 有變更，執行本腳本即可完成版本同步

-----------------------------------------------------------
【安全設計原則】
1. YAML parsing 錯誤必須明確拋出，不可 silent fail
2. 若找不到 YAML 檔案，必須中止並明確 log
3. 由 app.py 啟動時不得強制覆蓋管理員已修改內容
4. 由本腳本手動執行時，允許強制同步正式版本

-----------------------------------------------------------
【腳本用途總結】
本腳本的定位是：

- Prompt 初始化工具
- Prompt 發版同步工具
- Prompt 交接重建工具
- Prompt Source of Truth 落地工具

-----------------------------------------------------------
【適用情境】
- 新環境第一次建置
- 新學員接手專案
- Prompt Registry 改版後同步
- 清空資料庫後重建 Prompt
- 將教學 Prompt 還原到團隊正式版本

-----------------------------------------------------------
【執行指令】
    python scripts/init_prompt_templates.py

-----------------------------------------------------------
【建立日期】
2026-04-20

【維護原則】
若未來有更好的 Prompt：
1. 先更新 configs/prompts/prompt_registry.yaml
2. 再執行本腳本同步到資料庫
3. 團隊其餘成員重跑本腳本即可取得相同版本

-----------------------------------------------------------
【備註】
本腳本是 Prompt 管理流程中的「發版同步層」，
不是日常 runtime 的 prompt resolve 邏輯本身。

請勿在此腳本中加入與 Prompt 推理、教學策略判斷、
或模型呼叫相關的商業邏輯。
===========================================================
"""
import sys
import os
from datetime import datetime
from sqlalchemy import inspect

# 確保腳本能在專案根目錄下找到模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db
from core.prompts.prompt_loader import bootstrap_prompt_registry


def log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")


def init_prompt_templates():
    log("========== Prompt Registry Sync START ==========")

    try:
        with app.app_context():
            inspector = inspect(db.engine)

            # 1️⃣ 檢查 Table
            if not inspector.has_table("prompt_templates"):
                log("[DB] table 'prompt_templates' 不存在 → 建立中...")
                db.create_all()
                log("[DB] table 建立完成")
            else:
                log("[DB] table 'prompt_templates' 已存在")

            # 2️⃣ YAML Bootstrap（強制同步）
            log("[BOOTSTRAP] source=YAML update_existing=True")

            result = bootstrap_prompt_registry(update_existing=True)

            # 👉 建議你的 loader 回傳 dict
            # {created: X, updated: Y, skipped: Z}
            if isinstance(result, dict):
                created = result.get("created", 0)
                updated = result.get("updated", 0)
                skipped = result.get("skipped", 0)

                log(f"[RESULT] created={created} updated={updated} skipped={skipped}")
            else:
                log("[WARN] bootstrap 沒有回傳統計資訊")

            log("[SUCCESS] Prompt Templates 同步完成")

    except Exception as e:
        log("❌ [ERROR] Prompt Registry Sync 失敗")
        log(f"❌ {str(e)}")
        raise

    finally:
        log("========== Prompt Registry Sync END ==========")


if __name__ == "__main__":
    init_prompt_templates()