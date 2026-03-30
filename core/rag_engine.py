# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from typing import Any

import google.generativeai as genai

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

try:
    import chromadb
    from chromadb.utils import embedding_functions
    HAS_CHROMADB = True
except ImportError:  # pragma: no cover
    chromadb = None
    embedding_functions = None
    HAS_CHROMADB = False


_chroma_client = None
_collection = None
_skill_map: dict[str, str] = {}
_bridge_rows: list[dict[str, Any]] = []
LINEAR_SKILL_ID = "jh_數學1上_OperationsOnLinearExpressions"


def _table_exists(db, table_name: str) -> bool:
    row = db.session.execute(
        db.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name},
    ).first()
    return row is not None


def _parse_subskill_nodes(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [str(item).strip() for item in data if str(item).strip()]
        except Exception:
            pass
    return [item.strip() for item in text.replace(",", ";").split(";") if item.strip()]


def _clean_metadata_value(value: Any) -> str | int | float | bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return float(value)
    if isinstance(value, str):
        return value
    if np is not None:
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            return float(value)
    return str(value)


def _clean_metadata_dict(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
    cleaned: dict[str, str | int | float | bool] = {}
    for key, value in metadata.items():
        normalized = _clean_metadata_value(value)
        if normalized is not None:
            cleaned[str(key)] = normalized
    return cleaned


def _label_node(node: str) -> str:
    return {
        "sign_handling": "正負號判讀",
        "add_sub": "整數加減",
        "mul_div": "整數乘除",
        "mixed_ops": "四則混合",
        "order_of_operations": "運算順序",
        "absolute_value": "絕對值",
        "conjugate_rationalize": "共軛有理化",
        "divide_terms": "因式分解後約分",
        "multiply_terms": "分子分母乘法",
        "outer_minus_scope": "括號前負號整包變號",
        "monomial_distribution": "單項分配到括號",
        "nested_bracket_scope": "多層括號作用範圍",
        "like_term_combination": "同類項合併",
        "structure_isomorphism": "題型結構對齊",
        "term_collection_with_constants": "含常數項的合併化簡",
        "coefficient_sign_handling": "係數與符號處理",
        "fractional_expression_simplification": "分式線性式化簡",
    }.get(node, node.replace("_", " "))


def _label_family(family_name: str) -> str:
    return {
        "linear_flat_mul_div": "一元一次式乘除",
        "linear_combine_like_terms": "一元一次式同類項合併",
        "linear_flat_simplify_with_constants": "含常數項的一元一次式化簡",
        "linear_outer_minus_scope": "括號前負號變號 / 去括號變號",
        "linear_monomial_distribution": "單項式分配律 / 括號展開",
        "linear_nested_simplify": "多括號綜合化簡 / 巢狀括號化簡",
        "linear_fraction_expression_simplify": "分式一元一次式化簡",
    }.get(family_name, family_name)


def _dedupe_texts(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        output.append(text)
    return output


def _linear_retrieval_hints(row: dict[str, Any]) -> tuple[str, list[str]]:
    if str(row.get("skill_id") or "").strip() != LINEAR_SKILL_ID:
        return "", []

    family_name = str(row.get("family_name") or "").strip()
    if family_name == "linear_outer_minus_scope":
        return (
            "去括號時每一項都變號，去掉括號後符號會改變",
            ["去括號變號", "負號進括號", "每一項都變號", "整包變號"],
        )
    if family_name == "linear_monomial_distribution":
        return (
            "使用分配律把前面的數字乘進每一項，負號和數字都要一起乘進括號，像 -2(x-20) 這類括號要先乘開",
            ["分配律展開", "乘進括號", "每一項都要乘", "括號展開", "負號乘進括號", "前面的數字乘進去"],
        )
    if family_name == "linear_nested_simplify":
        return (
            "先算裡面的括號，再去內層括號往外化簡，展開後再合併同類項，像 11x-2[3x-(5x-4)] 這類題目要分步整理",
            ["多層括號", "含中括號的化簡", "先去內層括號再往外算", "展開後再合併同類項"],
        )
    return "", []


def _build_document_text(row: dict[str, Any]) -> str:
    nodes = _parse_subskill_nodes(row.get("subskill_nodes"))
    extra_theme, extra_node_hints = _linear_retrieval_hints(row)
    node_labels = _dedupe_texts([_label_node(node) for node in nodes] + extra_node_hints)
    node_text = "、".join(node_labels) if node_labels else ""
    theme = str(row.get("theme") or "").strip()
    if extra_theme:
        theme = f"{theme}，{extra_theme}" if theme else extra_theme
    parts = [
        row.get("skill_ch_name") or row.get("skill_name") or row.get("skill_id", ""),
    ]
    if row.get("family_name"):
        parts.append(f"題型：{_label_family(str(row['family_name']))}")
    if theme:
        parts.append(f"主題：{theme}")
    if node_text:
        parts.append(f"子技能：{node_text}")
    if row.get("curriculum"):
        parts.append(f"課綱：{row['curriculum']} {row.get('grade', '')}年級")
    if row.get("chapter"):
        parts.append(f"章節：{row['chapter']}")
    if row.get("section"):
        parts.append(f"小節：{row['section']}")
    if row.get("paragraph"):
        parts.append(f"段落：{row['paragraph']}")
    return " | ".join(str(part) for part in parts if str(part).strip())


def _summarize_bridge_rows(rows: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    linear_preview: list[dict[str, Any]] = []
    for row in rows:
        skill_id = str(row.get("skill_id", "") or "").strip()
        if not skill_id:
            continue
        counts[skill_id] = counts.get(skill_id, 0) + 1
        if skill_id == LINEAR_SKILL_ID and len(linear_preview) < 5:
            linear_preview.append(
                {
                    "family_id": str(row.get("family_id", "") or "").strip(),
                    "family_name": str(row.get("family_name", "") or "").strip(),
                    "subskill_nodes": _parse_subskill_nodes(row.get("subskill_nodes")),
                }
            )
    print(
        "[RAG LOAD] "
        f"total_rows={len(rows)} per_skill_counts={counts} "
        f"linear_skill_rows={counts.get(LINEAR_SKILL_ID, 0)}"
    )
    if linear_preview:
        print(f"[RAG LOAD] linear_preview={linear_preview}")


def _load_bridge_rows(app) -> list[dict[str, Any]]:
    from models import db

    if _table_exists(db, "skill_family_bridge"):
        rows = db.session.execute(
            db.text("""
                SELECT
                    b.skill_id,
                    COALESCE(si.skill_ch_name, b.skill_ch_name, b.skill_name) AS skill_ch_name,
                    COALESCE(si.skill_en_name, b.skill_en_name, '') AS skill_en_name,
                    b.family_id,
                    b.family_name,
                    b.theme,
                    b.subskill_nodes,
                    b.curriculum,
                    b.grade,
                    b.volume,
                    b.chapter,
                    b.section,
                    b.paragraph,
                    b.notes
                FROM skill_family_bridge b
                LEFT JOIN skills_info si ON si.skill_id = b.skill_id
                WHERE COALESCE(si.is_active, 1) = 1
                ORDER BY b.skill_id, b.family_id
            """)
        ).mappings().all()
        if rows:
            return [dict(row) for row in rows]

    if _table_exists(db, "skills_info") and _table_exists(db, "skill_curriculum"):
        rows = db.session.execute(
            db.text("""
                SELECT DISTINCT
                    si.skill_id,
                    si.skill_ch_name,
                    COALESCE(si.skill_en_name, '') AS skill_en_name,
                    NULL AS family_id,
                    NULL AS family_name,
                    si.category AS theme,
                    NULL AS subskill_nodes,
                    sc.curriculum,
                    sc.grade,
                    sc.volume,
                    sc.chapter,
                    sc.section,
                    sc.paragraph,
                    NULL AS notes
                FROM skills_info si
                JOIN skill_curriculum sc ON si.skill_id = sc.skill_id
                WHERE sc.curriculum = 'junior_high'
                  AND si.is_active = 1
                ORDER BY si.skill_id
            """)
        ).mappings().all()
        return [dict(row) for row in rows]

    return []


def _index_documents(rows: list[dict[str, Any]]):
    global _chroma_client, _collection, _skill_map, _bridge_rows

    if not HAS_CHROMADB:
        print("[RAG] chromadb not installed; RAG disabled.")
        _chroma_client = None
        _collection = None
        _skill_map = {}
        return

    _skill_map = {}
    _chroma_client = chromadb.Client()
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    try:
        _chroma_client.delete_collection("math_skills")
    except Exception:
        pass

    _collection = _chroma_client.create_collection(
        name="math_skills",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    documents: list[str] = []
    ids: list[str] = []
    metadatas: list[dict[str, Any]] = []

    for row in rows:
        skill_id = str(row.get("skill_id", "") or "").strip()
        family_id = str(row.get("family_id", "") or "").strip()
        if not skill_id:
            continue
        display_name = str(row.get("skill_ch_name") or row.get("skill_name") or skill_id).strip()
        _skill_map.setdefault(skill_id, display_name)
        doc_text = _build_document_text(row)
        if not doc_text:
            continue
        documents.append(doc_text)
        doc_id = f"{skill_id}:{family_id}" if family_id else skill_id
        ids.append(doc_id)
        metadatas.append(_clean_metadata_dict({
            "skill_id": skill_id,
            "family_id": family_id,
            "family_name": row.get("family_name"),
            "subskill_nodes": row.get("subskill_nodes"),
            "curriculum": row.get("curriculum"),
            "grade": row.get("grade"),
            "chapter": row.get("chapter"),
            "section": row.get("section"),
            "skill_ch_name": row.get("skill_ch_name"),
        }))

    if not documents:
        print("[RAG] No documents to index.")
        _collection = None
        return

    linear_ids = [doc_id for doc_id, meta in zip(ids, metadatas) if meta.get("skill_id") == LINEAR_SKILL_ID]
    print(
        "[RAG CHROMA PREP] "
        f"ids_total={len(ids)} contains_linear_skill={bool(linear_ids)} "
        f"linear_ids_preview={linear_ids[:10]}"
    )

    _collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas,
    )
    _bridge_rows = list(rows)
    collection_count = 0
    linear_count = 0
    try:
        collection_count = int(_collection.count())
    except Exception:
        collection_count = 0
    try:
        linear_result = _collection.get(where={"skill_id": LINEAR_SKILL_ID})
        linear_count = len(linear_result.get("ids") or [])
    except Exception:
        linear_count = 0
    print(
        "[RAG CHROMA READY] "
        f"collection_count={collection_count} linear_collection_ids={linear_count}"
    )
    print(f"[RAG] ✅ ChromaDB 初始化完成，已索引 {len(documents)} 筆知識節點")
    for sample in rows[:5]:
        print(f"  {sample.get('skill_id')}:{sample.get('family_id')} → {sample.get('skill_ch_name') or sample.get('skill_name')}")


def init_rag(app=None):
    """
    讀取 bridge table，將課程技能層、family 層與 subskill 層對齊後再做 embedding。
    """
    if not HAS_CHROMADB:
        print("[RAG] chromadb not installed; RAG disabled.")
        return
    if not app:
        print("[RAG] 請提供 Flask app 以初始化 RAG。")
        return

    with app.app_context():
        rows = _load_bridge_rows(app)

    if not rows:
        print("[RAG] 找不到可索引的技能資料。")
        return

    print(f"[RAG] ✅ 從資料庫讀取到 {len(rows)} 筆對齊資料")
    _summarize_bridge_rows(rows)
    _index_documents(rows)


def rag_search(query, top_k=5):
    """
    回傳 RAG 相關技能節點。
    """
    if (not HAS_CHROMADB) or _collection is None:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=top_k,
    )

    output = []
    if results and results.get("ids") and results["ids"]:
        for i, item_id in enumerate(results["ids"][0]):
            metadata = results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {}
            output.append({
                "skill_id": metadata.get("skill_id") or item_id.split(":", 1)[0],
                "family_id": metadata.get("family_id"),
                "family_name": metadata.get("family_name"),
                "chinese_name": metadata.get("skill_ch_name") or _skill_map.get(metadata.get("skill_id"), metadata.get("skill_id")),
                "subskill_nodes": _parse_subskill_nodes(metadata.get("subskill_nodes")),
                "curriculum": metadata.get("curriculum"),
                "grade": metadata.get("grade"),
                "chapter": metadata.get("chapter"),
                "section": metadata.get("section"),
                "distance": results["distances"][0][i] if results.get("distances") else 0,
            })
    return output


def debug_rag_queries(queries: list[str] | None = None, top_k: int = 5) -> list[dict[str, Any]]:
    probes = queries or [
        "-(x+5) 去括號為什麼都變號",
        "-2(x-20) 怎麼展開",
        "11x-2[3x-(5x-4)] 怎麼化簡",
        "括號前面有負號怎麼處理",
    ]
    all_results: list[dict[str, Any]] = []
    for query in probes:
        hits = rag_search(query, top_k=top_k)
        rows = [
            {
                "skill_id": hit.get("skill_id"),
                "family_id": hit.get("family_id"),
                "distance": hit.get("distance"),
            }
            for hit in hits
        ]
        print(f"[RAG RETRIEVE] query={query} top_hits={rows}")
        all_results.append({"query": query, "hits": hits})
    return all_results


def rag_chat(query, top_skill_id):
    """
    用第一筆對齊資料做受控回答。
    """
    if not HAS_CHROMADB:
        return {"reply": "RAG is unavailable because chromadb is not installed."}

    top_row = None
    for row in _bridge_rows:
        if row.get("skill_id") == top_skill_id:
            top_row = row
            break

    if top_row is None and _collection is not None:
        search_rows = rag_search(query, top_k=1)
        if search_rows:
            top_row = search_rows[0]

    if not top_row:
        return {"reply": "目前找不到對應的知識節點。"}

    ch_name = top_row.get("skill_ch_name") or top_row.get("skill_name") or top_row.get("chinese_name") or top_skill_id
    family_name = top_row.get("family_name") or ""
    subskills = _parse_subskill_nodes(top_row.get("subskill_nodes"))
    subskill_text = "、".join(_label_node(node) for node in subskills) if subskills else "核心概念"

    prompt = f"""
你是一位台灣國中數學助教。
請用繁體中文回答，語氣簡短，讓國中生看得懂。
只能提示，不要直接給完整答案。

學生問題：
{query}

目前對應技能：
{ch_name}
{f'（{family_name}）' if family_name else ''}

重點子技能：
{subskill_text}

請輸出：
1. 先提醒一個最重要的觀念
2. 再給一個小提示
3. 最後給一個下一步方向
""".strip()

    try:
        from core.ai_analyzer import gemini_model
        if not gemini_model:
            return {"reply": "目前 AI 助教尚未啟用。"}

        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
            ),
        )
        return {"reply": response.text}
    except Exception as e:
        print(f"[RAG Chat] Error: {e}")
        return {"reply": f"AI 回覆發生錯誤：{str(e)}"}
