# -*- coding: utf-8 -*-
"""Prompt composition layer for the teaching subsystem."""

import logging
from core.prompts.registry import get_prompt_with_source

logger = logging.getLogger(__name__)

def compose_prompt(base_key=None, task_key=None, extra_blocks=None, **kwargs):
    """
    統一組裝 prompt 的模組。
    
    :param base_key: 基礎設定/核心角色 (例如: chat_guardrail_prompt)
    :param task_key: 任務相關設定 (例如: chat_tutor_prompt, rag_tutor_prompt)
    :param extra_blocks: 附加的字串陣列 (例如: 動態注入的本輪提問、JSON schema 硬性要求)
    :param kwargs: 傳遞給 `format()` 的變數
    :return: (最終組裝的 prompt 字串, 使用到的來源紀錄字串)
    """
    blocks = []
    sources = []
    
    # 1. 處理 Base Prompt (通常是全局設定或防護機制，放最前面)
    if base_key:
        try:
            content, source = get_prompt_with_source(base_key)
            try:
                # 嘗試渲染，如果沒有變數會原封不動，有變數則吃 kwargs
                content = content.format(**kwargs)
            except KeyError:
                pass
            blocks.append(content)
            sources.append(f"{base_key}({source})")
        except Exception as e:
            logger.error(f"[Composer] 載入 base_key '{base_key}' 失敗: {e}")
            
    # 2. 處理 Task Prompt (主要任務內容)
    if task_key:
        try:
            # 對於 chat_tutor_prompt，由於我們有 legacy fallback key 'chat_ai_prompt'，
            # 這裡我們允許特例或透過來源回傳。為了乾淨，直接以 task_key 為主
            fallback_key = "chat_ai_prompt" if task_key == "chat_tutor_prompt" else None
            content, source = get_prompt_with_source(task_key, fallback_key)
            
            if task_key == "rag_tutor_prompt":
                kwargs.setdefault("route_label", "Unknown")
            
            try:
                formatted_content = content.format(**kwargs)
            except KeyError as e:
                logger.warning(f"[Composer] Task prompt '{task_key}' 缺少變數 {e}，進行強制替換或容錯處理")
                formatted_content = content + "\n\n[系統補完]\n缺少變數: " + str(e)
                
            blocks.append(formatted_content)
            sources.append(f"{task_key}({source})")
        except Exception as e:
            logger.error(f"[Composer] 載入 task_key '{task_key}' 失敗: {e}")
            
    # 3. 處理 Extra Blocks (例如後綴的 JSON 嚴格要求、其他無法預設的本輪輸入字串)
    if extra_blocks and isinstance(extra_blocks, list):
        for eb in extra_blocks:
            if eb and isinstance(eb, str):
                blocks.append(eb.strip())
                
    final_prompt = "\n\n".join(blocks)
    
    source_str = " | ".join(sources) if sources else "unknown"
    logger.info(f"[Prompt Composer] 組裝完畢 | base={base_key} | task={task_key} | sources={source_str}")
    
    return final_prompt, source_str
