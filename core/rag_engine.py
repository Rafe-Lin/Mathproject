# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from typing import Any

import google.generativeai as genai
from core.adaptive.catalog_loader import load_catalog

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


def _to_chroma_metadata_value(value: Any) -> str | int | float | bool:
    if isinstance(value, (str, int, float, bool)):
        return value
    if value is None:
        return ""
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _label_node(node: str) -> str:
    return {
        "sign_handling": "sign handling",
        "add_sub": "add/sub",
        "mul_div": "mul/div",
        "mixed_ops": "mixed operations",
        "order_of_operations": "order of operations",
        "absolute_value": "absolute value",
        "bracket_scope": "bracket scope",
        "power_notation_basics": "power notation basics",
        "signed_power_interpretation": "signed power interpretation",
        "parenthesized_negative_base": "parenthesized negative base",
        "minus_outside_power": "minus outside power",
        "power_precedence_in_mixed_ops": "power precedence in mixed ops",
        "signed_power_evaluation": "signed power evaluation",
        "mixed_power_arithmetic": "mixed power arithmetic",
        "same_base_multiplication_rule": "same-base multiplication rule",
        "power_building_from_repetition": "power from repetition",
        "power_of_power_rule": "power of power rule",
        "product_power_distribution": "product power distribution",
        "fraction_power_distribution": "fraction power distribution",
        "conjugate_rationalize": "conjugate rationalization",
        "divide_terms": "divide terms",
        "multiply_terms": "multiply terms",
    }.get(node, node.replace("_", " "))


def _build_document_text(row: dict[str, Any]) -> str:
    nodes = _parse_subskill_nodes(row.get("subskill_nodes"))
    node_text = ", ".join(_label_node(node) for node in nodes) if nodes else ""
    parts = [
        row.get("skill_ch_name") or row.get("skill_name") or row.get("skill_id", ""),
    ]
    if row.get("family_name"):
        parts.append(f"family: {row['family_name']}")
    if row.get("theme"):
        parts.append(f"theme: {row['theme']}")
    if node_text:
        parts.append(f"subskills: {node_text}")
    if row.get("curriculum"):
        parts.append(f"curriculum: {row['curriculum']} {row.get('grade', '')}")
    if row.get("chapter"):
        parts.append(f"chapter: {row['chapter']}")
    if row.get("section"):
        parts.append(f"section: {row['section']}")
    if row.get("paragraph"):
        parts.append(f"paragraph: {row['paragraph']}")
    return " | ".join(str(part) for part in parts if str(part).strip())


def _load_catalog_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for entry in load_catalog():
            rows.append(
                {
                    "skill_id": entry.skill_id,
                    "skill_ch_name": entry.skill_name,
                    "skill_name": entry.skill_name,
                    "family_id": entry.family_id,
                    "family_name": entry.family_name,
                    "theme": entry.theme,
                    "subskill_nodes": list(entry.subskill_nodes or []),
                    "curriculum": "junior_high",
                    "grade": "",
                    "chapter": "",
                    "section": "",
                    "paragraph": "",
                }
            )
    except Exception:
        return []
    return rows


def _load_bridge_rows(app) -> list[dict[str, Any]]:
    from models import db

    rows_out: list[dict[str, Any]] = []

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
            rows_out = [dict(row) for row in rows]

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
        rows_out.extend([dict(row) for row in rows])

    catalog_rows = _load_catalog_rows()
    if not rows_out:
        return catalog_rows

    existing_keys = {
        (str(r.get("skill_id") or "").strip(), str(r.get("family_id") or "").strip())
        for r in rows_out
    }
    for row in catalog_rows:
        key = (str(row.get("skill_id") or "").strip(), str(row.get("family_id") or "").strip())
        if key in existing_keys:
            continue
        rows_out.append(row)
    return rows_out


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
        metadata_raw = {
            "skill_id": skill_id,
            "family_id": family_id,
            "family_name": row.get("family_name"),
            "subskill_nodes": row.get("subskill_nodes"),
            "curriculum": row.get("curriculum"),
            "grade": row.get("grade"),
            "chapter": row.get("chapter"),
            "section": row.get("section"),
            "skill_ch_name": row.get("skill_ch_name"),
        }
        metadatas.append({k: _to_chroma_metadata_value(v) for k, v in metadata_raw.items()})

    if not documents:
        print("[RAG] No documents to index.")
        _collection = None
        return

    import os, pickle, hashlib
    docs_string = "".join(documents)
    docs_hash = hashlib.md5(docs_string.encode('utf-8')).hexdigest()
    cache_file = os.path.join(app.root_path, '..', 'configs', 'rag_embeddings_cache.pkl')
    
    embeddings = None
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                if cache_data.get('hash') == docs_hash:
                    embeddings = cache_data.get('embeddings')
        except Exception:
            pass
            
    if embeddings is None:
        embeddings = _embedding_model.encode(documents).tolist()
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump({'hash': docs_hash, 'embeddings': embeddings}, f)
        except Exception:
            pass

    _collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas,
        embeddings=embeddings
    )
    _bridge_rows = list(rows)
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
