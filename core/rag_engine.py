# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/rag_engine.py
功能說明 (Description): Naive RAG 引擎 — 使用 ChromaDB + all-MiniLM-L6-v2
                        僅索引系統中存在的國中練習技能，搭配 Gemini 2.5 Flash 回答
版本資訊 (Version): V2.0
更新日期 (Date): 2026-03-02
=============================================================================
"""

import os
import google.generativeai as genai

# --- ChromaDB & Embedding ---
try:
    import chromadb
    from chromadb.utils import embedding_functions
    HAS_CHROMADB = True
except ImportError:
    chromadb = None
    embedding_functions = None
    HAS_CHROMADB = False

# 全域變數
_chroma_client = None
_collection = None
_skill_map = {}  # skill_id -> skill_ch_name


# ==========================================
# Initialization (從資料庫讀取國中技能)
# ==========================================

def init_rag(app=None):
    """
    從 SkillInfo + SkillCurriculum 表中讀取國中(junior_high)的活躍技能，
    以 skill_ch_name 作為虛擬文本進行 embedding，存入 ChromaDB。
    """
    global _chroma_client, _collection, _skill_map

    if not HAS_CHROMADB:
        print("[RAG] chromadb not installed; RAG disabled.")
        _chroma_client = None
        _collection = None
        _skill_map = {}
        return

    if not app:
        print("[RAG] ⚠️ 需要 Flask app 來存取資料庫")
        return

    with app.app_context():
        from models import db
        # 從 DB 查詢國中所有活躍技能 (含中文名稱)
        rows = db.session.execute(
            db.text("""
                SELECT DISTINCT si.skill_id, si.skill_ch_name
                FROM skills_info si
                JOIN skill_curriculum sc ON si.skill_id = sc.skill_id
                WHERE sc.curriculum = 'junior_high'
                  AND si.is_active = 1
                ORDER BY si.skill_id
            """)
        ).fetchall()

    if not rows:
        print("[RAG] ⚠️ 資料庫中無國中技能資料")
        return

    # 建立 skill_id -> 中文名稱 的對照表
    _skill_map = {row[0]: row[1] for row in rows}
    skill_ids = list(_skill_map.keys())

    print(f"[RAG] ✅ 從資料庫讀取到 {len(skill_ids)} 個國中技能")

    # 初始化 ChromaDB (in-memory)
    _chroma_client = chromadb.Client()

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    try:
        _chroma_client.delete_collection("math_skills")
    except Exception:
        pass

    _collection = _chroma_client.create_collection(
        name="math_skills",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    # 以 skill_ch_name (中文名稱) 作為 document 進行 embedding
    documents = [_skill_map[sid] for sid in skill_ids]
    metadatas = [{"skill_id": sid, "ch_name": _skill_map[sid]} for sid in skill_ids]

    _collection.add(
        documents=documents,
        ids=skill_ids,
        metadatas=metadatas
    )

    print(f"[RAG] ✅ ChromaDB 初始化完成，已索引 {len(skill_ids)} 個國中技能")
    for s in skill_ids[:5]:
        print(f"  {s} → {_skill_map[s]}")


# ==========================================
# Retrieval
# ==========================================

def rag_search(query, top_k=5):
    """
    接收學生問題，回傳 Top-K 最相似的 skill_ids。
    所有結果都是系統中存在的可練習技能。
    """
    if (not HAS_CHROMADB) or _collection is None:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=top_k
    )

    output = []
    if results and results['ids'] and len(results['ids']) > 0:
        for i, sid in enumerate(results['ids'][0]):
            output.append({
                'skill_id': sid,
                'chinese_name': _skill_map.get(sid, sid),
                'distance': results['distances'][0][i] if results.get('distances') else 0
            })

    return output


# ==========================================
# RAG + LLM (Gemini 2.5 Flash)
# ==========================================

def rag_chat(query, top_skill_id):
    """
    將 Top-1 檢索結果作為上下文，使用 Gemini 2.5 Flash 簡短回答學生問題。
    """
    ch_name = _skill_map.get(top_skill_id, top_skill_id)

    if not HAS_CHROMADB:
        return {"reply": "RAG is unavailable because chromadb is not installed."}

    prompt = f"""你是數學老師，回答要精簡直接。

學生問：「{query}」
最相關單元：「{ch_name}」

規則：
- 用繁體中文回答，控制在 3-5 句話，確保每句話都完整
- 數學公式用 $$ 包裹（LaTeX 格式）
- 不要開場白，直接回答重點
- 給出關鍵公式或定義，搭配簡短說明
"""

    try:
        from core.ai_analyzer import gemini_model
        if not gemini_model:
            return {"reply": "系統尚未初始化。"}

        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
            )
        )
        return {"reply": response.text}

    except Exception as e:
        print(f"[RAG Chat] Error: {e}")
        return {"reply": f"AI 回答錯誤：{str(e)}"}
