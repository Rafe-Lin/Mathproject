# -*- coding: utf-8 -*-
import json
import logging
import numpy as np
from typing import Any, List, Dict
from config import Config

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    from rank_bm25 import BM25Okapi
    import jieba
    HAS_ADV_LIBS = True
except ImportError:
    HAS_ADV_LIBS = False

from core.rag_engine import _load_bridge_rows, _build_document_text, _parse_subskill_nodes, rag_search, _label_node

logger = logging.getLogger(__name__)

_adv_chroma_client = None
_adv_collection = None
_bm25 = None
_embedding_model = None
_documents: List[str] = []
_ids: List[str] = []
_metadatas: List[Dict[str, Any]] = []
_skill_map: Dict[str, str] = {}
_bridge_rows: List[Dict[str, Any]] = []

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

def init_adv_rag(app):
    global _adv_chroma_client, _adv_collection, _bm25, _embedding_model
    global _documents, _ids, _metadatas, _skill_map, _bridge_rows

    if not HAS_ADV_LIBS:
        logger.warning("[Advanced RAG] Missing dependencies (jieba, rank_bm25, sentence-transformers, or chromadb). Disabled.")
        return

    try:
        from core.ai_analyzer import gemini_model
    except ImportError:
        pass

    with app.app_context():
        rows = _load_bridge_rows(app)
        
    if not rows:
        logger.info("[Advanced RAG] No skill data found.")
        return

    _bridge_rows = list(rows)
    _embedding_model = SentenceTransformer('shibing624/text2vec-base-chinese')
    _adv_chroma_client = chromadb.Client()

    try:
        _adv_chroma_client.delete_collection("math_skills_adv")
    except Exception:
        pass

    _adv_collection = _adv_chroma_client.create_collection(name="math_skills_adv")

    _documents = []
    _ids = []
    _metadatas = []
    _skill_map = {}

    for row in rows:
        skill_id = str(row.get("skill_id", "") or "").strip()
        family_id = str(row.get("family_id", "") or "").strip()
        if not skill_id:
            continue
        
        display_name = str(row.get("skill_ch_name") or row.get("skill_name") or skill_id).strip()
        _skill_map[skill_id] = display_name
        doc_text = _build_document_text(row)
        if not doc_text:
            continue
            
        doc_id = f"{skill_id}:{family_id}" if family_id else skill_id
        if doc_id in _ids:
            continue
            
        _documents.append(doc_text)
        _ids.append(doc_id)
        
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
        _metadatas.append({k: _to_chroma_metadata_value(v) for k, v in metadata_raw.items()})

    if not _documents:
        logger.info("[Advanced RAG] No documents to index.")
        return

    # Embed and add to DB
    logger.info(f"[Advanced RAG] Building index for {_documents.__len__()} items (this may take a bit)...")
    
    import os, pickle, hashlib
    docs_string = "".join(_documents)
    docs_hash = hashlib.md5(docs_string.encode('utf-8')).hexdigest()
    cache_file = os.path.join(app.root_path, '..', 'configs', 'adv_embeddings_cache.pkl')
    
    embeddings = None
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                if cache_data.get('hash') == docs_hash:
                    embeddings = cache_data.get('embeddings')
                    logger.info("[Advanced RAG] Loaded embeddings from cache!")
        except Exception:
            pass
            
    if embeddings is None:
        embeddings = _embedding_model.encode(_documents).tolist()
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump({'hash': docs_hash, 'embeddings': embeddings}, f)
        except Exception:
            pass

    _adv_collection.add(
        documents=_documents,
        ids=_ids,
        metadatas=_metadatas,
        embeddings=embeddings
    )

    # Initialize BM25
    tokenized_docs = [list(jieba.cut(doc)) for doc in _documents]
    _bm25 = BM25Okapi(tokenized_docs)
    logger.info("[Advanced RAG] Initialization complete!")


def get_llm_keywords(query: str) -> List[str]:
    """Uses Local LLM or Gemini to extract key search words from the student's problem."""
    try:
        prompt = f"""
        請從以下學生的數學問題中，提取出最關鍵的數學單元名稱或核心概念關鍵字，
        請只回傳一行，包含 3 到 5 個關鍵詞，以空白分隔。不要加上任何說明文字。
        學生問題：{query}
        """

        # First attempt with Gemini (can easily switch to Ollama request like in original app)
        from core.ai_analyzer import gemini_model
        if gemini_model:
            import google.generativeai as genai
            response = gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.1, max_output_tokens=30)
            )
            keywords_text = response.text.replace('\n', ' ').strip()
            return [kw for kw in keywords_text.split() if kw]
    except Exception as e:
        logger.error(f"[Advanced RAG Keyword Extraction] Failed: {e}")
    return []

def extract_advanced_rag(query: str, K_VALUE=42, top_k=5):
    """Executes the dense + sparse hybrid RRF retrieval as per experiment script."""
    keywords = get_llm_keywords(query)
    q_dense = query + " " + " ".join(keywords) if keywords else query
    q_sparse = " ".join(keywords) if keywords else query

    vec_dense = _embedding_model.encode([q_dense]).tolist()
    res_dense = _adv_collection.query(query_embeddings=vec_dense, n_results=50)
    dense_ids = res_dense['ids'][0] if res_dense and res_dense['ids'] else []

    tokenized_query = list(jieba.cut(q_sparse))
    bm25_scores = _bm25.get_scores(tokenized_query)
    # Get top 50 indices
    top_n_idx = np.argsort(bm25_scores)[::-1][:50]
    sparse_ids = [_ids[i] for i in top_n_idx]

    rrf_scores = {}
    rrf_k = 60
    for rank, doc_id in enumerate(dense_ids):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (rrf_k + rank + 1)
    for rank, doc_id in enumerate(sparse_ids):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (rrf_k + rank + 1)

    sorted_hybrid_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    ans_list_advanced = [x[0] for x in sorted_hybrid_ids][:K_VALUE]

    # Map the retrieved IDs back to the desired output format
    output = []
    added = set()
    for doc_id in ans_list_advanced:
        if doc_id in added:
            continue
        try:
            idx = _ids.index(doc_id)
            metadata = _metadatas[idx]
            output.append({
                "skill_id": metadata.get("skill_id") or doc_id.split(":", 1)[0],
                "family_id": metadata.get("family_id"),
                "family_name": metadata.get("family_name"),
                "chinese_name": metadata.get("skill_ch_name") or _skill_map.get(metadata.get("skill_id"), metadata.get("skill_id")),
                "subskill_nodes": _parse_subskill_nodes(metadata.get("subskill_nodes")),
                "curriculum": metadata.get("curriculum"),
                "grade": metadata.get("grade"),
                "chapter": metadata.get("chapter"),
                "section": metadata.get("section"),
                "distance": 0, # Since we use RRF score, distance is not exact space distance
                "rrf_score": rrf_scores[doc_id]
            })
            added.add(doc_id)
            if len(output) >= top_k:
                break
        except ValueError:
            pass

    return output


def adv_rag_search(query: str, top_k=5):
    """
    Hybrid RAG Search controller with Configured Threshold
    """
    if not HAS_ADV_LIBS or _adv_collection is None:
        logger.warning("[Advanced RAG] Not ready. Fallback to Naive RAG.")
        return rag_search(query, top_k)

    # 1. First run Naive RAG to test distance
    naive_results = rag_search(query, top_k=top_k)
    naive_dist = naive_results[0]['distance'] if naive_results and 'distance' in naive_results[0] else float('inf')

    # 2. Check if we can route to Fast Path (Naive)
    try:
        from flask import current_app
        threshold = current_app.config.get('ADVANCED_RAG_NAIVE_THRESHOLD', getattr(Config, 'ADVANCED_RAG_NAIVE_THRESHOLD', 0.85))
    except RuntimeError:
        threshold = getattr(Config, 'ADVANCED_RAG_NAIVE_THRESHOLD', 0.85)
    
    # 距離分數越低代表越接近。
    if naive_dist <= threshold:
        logger.info(f"[Hybrid Routing] Naive distance {naive_dist:.3f} <= {threshold:.3f}. Using Fast Path (Naive).")
        # Ensure we attach a flag so frontend can see
        for res in naive_results:
            res['routing'] = 'Naive Fast-Path'
        return naive_results

    # 3. Else run Advanced RAG 
    logger.info(f"[Hybrid Routing] Naive distance {naive_dist:.3f} > {threshold:.3f}. Using Advanced RAG Recovery Path.")
    adv_results = extract_advanced_rag(query, K_VALUE=42, top_k=top_k)
    for res in adv_results:
        res['routing'] = 'Advanced RAG'
    
    return adv_results


def adv_rag_chat(query: str, retrieved_skills: list):
    """
    Generates Answer utilizing multiple retrieved contents from Advanced RAG.
    If no text is available, asks LLM to generate a very short textbook lesson.
    """
    if not retrieved_skills:
        return {"reply": "我找不到與問題相關的單元，或許你可以換個問法？"}

    try:
        from core.ai_analyzer import gemini_model
        if not gemini_model:
            return {"reply": "目前 AI 助教尚未啟用。"}

        # Compile retrieved resources
        units_text = ""
        for i, skill in enumerate(retrieved_skills):
            ch_name = skill.get("chinese_name", "")
            fam_name = skill.get("family_name", "")
            subs = skill.get("subskill_nodes", [])
            subs_str = "、".join(_label_node(n) for n in subs) if subs else "核心基礎"
            units_text += f"{i+1}. 單元: {ch_name} (類別: {fam_name}) - 重點: {subs_str}\n"

        prompt = f"""
你是一位台灣國中數學助教。學生遇到了一個不會的問題，我們透過 RAG 系統檢索出了五個最相關的單元教材資訊。

學生問題：
{query}

檢索出的相關知識點：
{units_text}

請你根據這些檢索出的單元，為學生準備一個「簡短教材與提示」：
1. 針對學生的問題，提供一個最貼切的核心觀念（如果資料庫沒有詳細教材，請直接運用你豐富的數學知識寫出一個精簡的教學，不要太長）。
2. 給予學生面對此題目的第一步小提示（不要直接講出答案）。
3. 語氣簡潔友好，適合國中生理解。
"""
        import google.generativeai as genai
        import google.generativeai as genai
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
            ),
        )
        return {"reply": response.text}

    except Exception as e:
        logger.error(f"[Adv RAG Chat] Error: {e}")
        return {"reply": f"AI 回覆發生錯誤：{str(e)}"}
