# -*- coding: utf-8 -*-
"""
綜合壓力測試：模擬會場實戰 (純淨解析版)
1. 自動拆解 14 大題為純 LaTeX 小題（排除題號與說明）。
2. 在 Terminal 即時顯示當前測試的算式內容。
3. 驗證產出是否符合國中教科書格式。
"""

import copy
import html
import os
import re
import sys
import time
import requests
from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple

# 確保可引用專案根目錄下的本地模組
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.code_utils.live_show_math_utils import classify_radical_style, radical_hard_style_preserved

# 課本 14 大題原始資料
FULL_MINUS = "\uFF0D"   # 全形 －
FULL_PLUS = "\uFF0B"    # 全形 ＋
RAW_STRINGS = [
    f"計算下列各式的值。⑴ $({FULL_MINUS}2 )\\times3 \\sqrt{{5}}$ ⑵ $4 \\sqrt{{2}}\\times \\frac{{1}}{{6}}$ ⑶ $\\frac{{2}}{{3}}\\times \\frac{{\\sqrt{{3}}}}{{3}}$",
    f"計算下列各式的值。⑴ $\\frac{{3}}{{5}}\\times5 \\sqrt{{2}}$ ⑵ $\\frac{{\\sqrt{{5}}}}{{12}}\\times({FULL_MINUS}16 )$ ⑶ $\\frac{{3\\sqrt{{7}}}}{{4}}\\times \\frac{{1}}{{9}}$",
    f"計算下列各式的值。⑴ $\\sqrt{{2}}\\times \\sqrt{{3}}$ ⑵ $({FULL_MINUS}\\frac{{2}}{{3}} \\sqrt{{5}} \\quad )\\times4 \\sqrt{{7}}$ ⑶ $7 \\sqrt{{2}}\\times5 \\sqrt{{2}}$",
    f"計算下列各式的值。⑴ $\\sqrt{{35}}\\div \\sqrt{{5}}$ ⑵ $({FULL_MINUS}12 \\sqrt{{6}} )\\div( 8 \\sqrt{{3}} )$ ⑶ $\\frac{{1}}{{\\sqrt{{3}}}}\\div \\frac{{\\sqrt{{6}}}}{{\\sqrt{{2}}}}$",
    "將下列根式化為最簡根式。⑴ $\\sqrt{5^3}$ ⑵ $\\sqrt{18}$ ⑶ $\\sqrt{8}\\times \\sqrt{45}$",
    "將下列根式化為最簡根式。⑴ $\\frac{2}{\\sqrt{10}}$ ⑵ $\\frac{5}{\\sqrt{12}}$",
    "將下列根式化為最簡根式。⑴ $\\sqrt{0.8}$ ⑵ $\\sqrt{\\frac{5}{27}}$",
    "圈圈看，下列哪些是 $\\sqrt{6}$ 的同類方根？ $\\sqrt{12}$ $\\sqrt{24}$ $\\sqrt{16}$ $\\sqrt{\\frac{2}{3}}$ $\\frac{2}{\\sqrt{3}}$ $\\sqrt{0.06}$",
    f"化簡下列各式。⑴ $2 \\sqrt{{3}}{FULL_PLUS}3 \\sqrt{{3}}$ ⑵ $4 \\sqrt{{6}}{FULL_MINUS}3 \\sqrt{{6}}$ ⑶ $5 \\sqrt{{10}}{FULL_MINUS}3 \\sqrt{{5}}{FULL_MINUS}2 \\sqrt{{10}}{FULL_PLUS}4 \\sqrt{{5}}$",
    f"化簡下列各式。⑴ $3 \\sqrt{{2}}{FULL_PLUS} \\sqrt{{8}}$ ⑵ $\\sqrt{{1\\frac{{9}}{{16}}}}{FULL_PLUS} \\sqrt{{4\\frac{{25}}{{36}}}}$ ⑶ $\\frac{{1}}{{\\sqrt{{3}}}}{FULL_MINUS}\\frac{{2}}{{3}} \\sqrt{{3}}$ ⑷ $3 \\sqrt{{3}}{FULL_PLUS}2 \\sqrt{{5}}{FULL_MINUS}( \\sqrt{{12}}{FULL_MINUS} \\sqrt{{45}} )$",
    f"化簡下列各式。⑴ $\\sqrt{{\\frac{{1}}{{2}}}}\\times \\sqrt{{\\frac{{1}}{{5}}}}\\div \\sqrt{{\\frac{{1}}{{6}}}}$ ⑵ $({FULL_MINUS}4 \\sqrt{{15}} )\\times({FULL_MINUS} \\sqrt{{\\frac{{1}}{{3}}}} ){FULL_MINUS}4 \\sqrt{{5}}$",
    f"化簡下列各式。⑴ $2 \\sqrt{{3}}\\times( \\sqrt{{12}}{FULL_MINUS} \\sqrt{{2}} )$ ⑵ $({FULL_MINUS}3 \\sqrt{{2}}{FULL_PLUS} \\sqrt{{15}} )\\div \\sqrt{{3}}$ ⑶ $( \\sqrt{{3}}{FULL_PLUS} \\sqrt{{2}} )( \\sqrt{{6}}{FULL_MINUS}1 )$",
    f"利用乘法公式化簡下列各式。⑴ $( \\sqrt{{3}}{FULL_MINUS}2 \\sqrt{{2}} )( \\sqrt{{3}}{FULL_PLUS}2 \\sqrt{{2}} )$ ⑵ $( \\sqrt{{3}}{FULL_PLUS}2 \\sqrt{{2}} \\quad )^2$",
    f"將下列各式的分母有理化。⑴ $\\frac{{1}}{{ \\sqrt{{3}}{FULL_MINUS} \\sqrt{{2}}}}$ ⑵ $\\frac{{\\sqrt{{2}}}}{{3 \\sqrt{{2}}{FULL_PLUS}4}}$",
]

BASE_URL = os.environ.get("MATHPROJECT_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
CLASSIFY_URL = f"{BASE_URL}/api/classify"
GENERATE_URL = f"{BASE_URL}/api/generate_live"
# 僅在 classify 失敗且需對照舊行為時作為後備（預設不走此路）
FALLBACK_SKILL_ID = "jh_數學2上_FourOperationsOfRadicals"
CLASSIFY_TIMEOUT = int(os.environ.get("STRESS_CLASSIFY_TIMEOUT", "180"))
GENERATE_TIMEOUT = int(os.environ.get("STRESS_GENERATE_TIMEOUT", "300"))
# 設為正整數時只跑前 N 題（快速驗證 drift / HTML 欄位）；0 = 全跑
STRESS_MAX_ITEMS = int(os.environ.get("STRESS_MAX_ITEMS", "0"))
# echo 規則：預設 strict_equal；設 similarity 可回到舊行為做 A/B
STRESS_ECHO_RULE = os.environ.get("STRESS_ECHO_RULE", "strict_equal").strip().lower()


def _strip_for_sig(s: str) -> str:
    return (s or "").replace("$", "").replace(" ", "")


def _max_paren_depth(s: str) -> int:
    d = mx = 0
    for c in s:
        if c == "(":
            d += 1
            mx = max(mx, d)
        elif c == ")":
            d = max(0, d - 1)
    return mx


def _has_implicit_multiply_skeleton(expr: str) -> bool:
    """
    LaTeX 隱式乘法骨架（無 \\times 但語意為乘）：)( 、連續 \\sqrt 、係數貼根號/括號等。
    用於避免將 (a\\sqrt{b})(c\\sqrt{d}) 誤判為純加減多根號。
    """
    t = _strip_for_sig(expr)
    if not t:
        return False
    if ")(" in t:
        return True
    if re.search(r"\\sqrt(?:\[[^\]]*\])?\{[^}]+\}\\sqrt", t):
        return True
    if re.search(r"(?<![\\w])\d+\\sqrt", t):
        return True
    if re.search(r"[\)\}\]]\\sqrt", t):
        return True
    if re.search(r"\\sqrt(?:\[[^\]]*\])?\{[^}]+\}\(", t):
        return True
    if re.search(r"\)[\d\-]", t):
        return True
    if re.search(r"(?<![\\w])\d+\(", t):
        return True
    return False


def extract_operator_signature(latex_text: str) -> Dict[str, Any]:
    """
    輕量運算符／結構簽章：全文計數 + 僅以小括號深度估算的頂層 \\times/\\div。
    """
    s = _strip_for_sig(latex_text)
    depth = 0
    top_times = 0
    top_div = 0
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "(":
            depth += 1
            i += 1
            continue
        if s[i] == ")":
            depth = max(0, depth - 1)
            i += 1
            continue
        if depth == 0 and s.startswith(r"\times", i):
            top_times += 1
            i += len(r"\times")
            continue
        if depth == 0 and s.startswith(r"\div", i):
            top_div += 1
            i += len(r"\div")
            continue
        i += 1

    return {
        "times": len(re.findall(r"\\times", s)),
        "div": len(re.findall(r"\\div", s)),
        "frac": len(re.findall(r"\\frac", s)),
        "sqrt": len(re.findall(r"\\sqrt", s)),
        "plus": s.count("+"),
        "hyphen_minus": s.count("-"),
        "top_times": top_times,
        "top_div": top_div,
        "max_paren_depth": _max_paren_depth(s),
        "implicit_mult": 1 if _has_implicit_multiply_skeleton(s) else 0,
    }


def infer_expected_type(expr: str) -> str:
    """依輸入 LaTeX 粗分預期題型（壓測用，非課綱正式分類）。"""
    s = _strip_for_sig(expr)
    if re.search(r"\\frac\{[^}]*\}\{\\sqrt", s) or re.search(
        r"\\frac\{1\}\{\\sqrt", s
    ):
        return "rationalize_den_sqrt"
    if r"\div" in s:
        return "divide"
    if r"\times" in s:
        return "multiply"
    sqrt_n = len(re.findall(r"\\sqrt", s))
    if sqrt_n == 1 and r"\times" not in s and r"\div" not in s:
        return "simplify_single"
    if sqrt_n >= 2 and r"\times" not in s and r"\div" not in s:
        # Prioritise visible add/sub families; implicit coefficient*sqrt should
        # not be mis-read as multiplication family.
        if re.search(r"(?<!^)[+\-]", s):
            return "add_sub"
        if _has_implicit_multiply_skeleton(expr):
            return "multiply"
        return "add_sub"
    return "mixed_or_other"


def _looks_like_multi_sqrt_addsub_only(o: str) -> bool:
    """兩個以上 \\sqrt，僅以 +- 連接，無 \\times/\\div/\\frac，且無隱式乘法骨架。"""
    s = _strip_for_sig(o)
    if _has_implicit_multiply_skeleton(o):
        return False
    if re.search(r"\\times|\\div|\\frac", s):
        return False
    if len(re.findall(r"\\sqrt", s)) < 2:
        return False
    return bool(re.search(r"\\sqrt(?:\[[^\]]*\])?\{[^}]+\}.*?[+-].*?\\sqrt", s))


def extract_ab2_problem_text(data: Dict[str, Any]) -> str:
    """
    優先使用 API 正規化後的欄位：question_text，否則 problem（與 live_show 前端一致）。
    """
    ab2 = data.get("ab2_result")
    if not isinstance(ab2, dict):
        return ""
    return (ab2.get("question_text") or ab2.get("problem") or "").strip()


def evaluate_problem_track(
    math_expr: str, problem_text: str
) -> Tuple[List[str], List[str], str, Dict[str, Any], str]:
    """
    單一軌（Ab2 或 Ab3）的完整檢查。
    回傳 (all_issues, drift_only_errs, expected_type, sig_out, drift_reason)。
    """
    issues = run_assertions(problem_text)
    drift_errs, expected_type, sig_out, drift_reason = run_operator_drift_assertions(
        math_expr, problem_text
    )
    all_issues = issues + drift_errs
    return all_issues, drift_errs, expected_type, sig_out, drift_reason


def run_operator_drift_assertions(
    input_expr: str, output_latex: str
) -> Tuple[List[str], str, Dict[str, Any], str]:
    """
    題型漂移檢查。回傳 (errors, expected_type, output_signature, mismatch_reason)。
    mismatch_reason 為單一摘要字串（無漂移時為空）。
    """
    expected = infer_expected_type(input_expr)
    sig_out = extract_operator_signature(output_latex)
    errs: List[str] = []
    reasons: List[str] = []

    if not (output_latex or "").strip():
        return errs, expected, sig_out, ""

    if expected == "multiply":
        if _looks_like_multi_sqrt_addsub_only(output_latex):
            errs.append("❌ 題型漂移：輸入含乘法骨架，生成卻像純加減根式")
            reasons.append("input=multiply → output add/sub-only (multi-√)")

    if expected in ("divide", "rationalize_den_sqrt"):
        if _looks_like_multi_sqrt_addsub_only(output_latex):
            errs.append(
                "❌ 題型漂移：輸入含除法/有理化骨架，生成卻像純加減根式"
            )
            reasons.append(
                f"input={expected} → output add/sub-only (multi-√)"
            )

    # simplify_single：允許單一根式或整數結果，不強制保留乘除
    return errs, expected, sig_out, "; ".join(reasons)


def clean_latex(inner: str) -> str:
    """清理算式：處理全形字元並移除所有空格。"""
    s = inner.replace(FULL_MINUS, "-").replace(FULL_PLUS, "+")
    # 把 \x0crac 救回 \frac（Python 字串裡 \f 曾被誤判為 Form Feed）
    s = s.replace("\x0c", "\\f")
    return s.replace(" ", "").strip()


def collect_pure_math_cases() -> List[Tuple[int, int, str, str]]:
    """
    從 RAW_STRINGS 提取純淨的 $...$ 片段。
    回傳 (大題編號, 小題編號, 清洗後算式, 該大題完整課本原文)。
    完整原文會一併送進 /api/classify，貼近前端「整段題幹 + 辨識」再交 generate 的流程。
    """
    test_cases = []
    for big_idx, raw_text in enumerate(RAW_STRINGS, start=1):
        matches = re.findall(r"\$(.*?)\$", raw_text)
        for sub_idx, fragment in enumerate(matches, start=1):
            cleaned = clean_latex(fragment)
            if cleaned:
                test_cases.append((big_idx, sub_idx, cleaned, raw_text))
    return test_cases


def build_classify_text_data(parent_raw_line: str, math_expr: str) -> str:
    """
    回應診斷：拔除干擾的中文前綴，只給 AI 最純淨的算式，
    迫使它的注意力 100% 集中在 LaTeX 骨架上！
    """
    safe_expr = math_expr.replace("\x0c", "\\f")
    # 🌟 直接回傳純算式，不加任何「計算下列各式...」的廢話！
    return f"${safe_expr}$"


def run_classify(text_data: str) -> Tuple[bool, Dict[str, Any], str]:
    """
    POST /api/classify。成功時回 (True, body, "")；失敗時回 (False, {{}}, 錯誤訊息)。
    """
    try:
        r = requests.post(
            CLASSIFY_URL,
            json={"text_data": text_data},
            timeout=CLASSIFY_TIMEOUT,
        )
        body = r.json() if r.content else {}
        if r.status_code != 200:
            err = body.get("error") if isinstance(body, dict) else str(body)
            return False, {}, f"HTTP {r.status_code}: {err or r.text[:200]}"
        if not isinstance(body, dict) or not body.get("success"):
            err = body.get("error", "classify success=false") if isinstance(body, dict) else "invalid JSON"
            return False, {}, str(err)
        return True, body, ""
    except Exception as e:
        return False, {}, str(e)


def normalize_classify_result(
    c_body: Dict[str, Any], math_expr: str
) -> Tuple[str, str, Dict[str, Any], List[str]]:
    """
    清理 classify 回傳，避免 Unknown skill / 非純算式 ocr_text 讓 generate 直接 400。
    回傳: (skill_id, ocr_text, json_spec, notes)
    """
    notes: List[str] = []
    raw_skill = (c_body.get("skill_id") or "").strip()
    ocr_text = (c_body.get("ocr_text") or "").strip()
    json_spec = c_body.get("json_spec")
    if not isinstance(json_spec, dict):
        json_spec = {}
    json_spec = copy.deepcopy(json_spec)

    if not ocr_text:
        ocr_text = math_expr
        notes.append("ocr_text fallback to math_expr")

    # 測試場景：Unknown skill 直接讓 generate_live 拒絕，故在壓測腳本做後備
    skill_id = raw_skill if raw_skill and raw_skill != "Unknown" else FALLBACK_SKILL_ID
    if raw_skill == "Unknown":
        notes.append(f"skill fallback to {FALLBACK_SKILL_ID}")

    json_spec["ocr_text"] = ocr_text
    return skill_id, ocr_text, json_spec, notes


def run_assertions(problem_text: str) -> List[str]:
    """執行排版品質檢驗"""
    errors = []
    if not problem_text or len(problem_text.strip()) < 2:
        return ["❌ 產出為空"]

    # 🌟 教授的最後一道防護網：沒有 $ 符號絕對不是合法的數學題！
    if problem_text.count("$") == 0:
        errors.append("❌ 嚴重瑕疵：遺失數學模式符號 $")

    # 1. 嚴禁中括號 (除非是 LaTeX 指令)
    clean_text = problem_text.replace(r"\left[", "").replace(r"\right]", "")
    if "[" in clean_text or "]" in clean_text:
        errors.append("❌ 偵測到非法中括號 [ ]")

    # 2. 嚴禁雙括號
    if "((" in problem_text or "))" in problem_text:
        errors.append("❌ 偵測到冗餘雙括號 (( ))")

    # 3. 乘號後負數保護
    if re.search(r"\\times\s*-", problem_text):
        errors.append("❌ 偵測到 \\times 接裸露負號")

    # LaTeX 致命錯誤攔截
    if problem_text.count("{") != problem_text.count("}"):
        errors.append("❌ LaTeX 大括號 { } 不成對 (渲染必死)")
    if problem_text.count("$") % 2 != 0:
        errors.append("❌ 數學模式 $ 不成對 (渲染必死)")

    return errors


def _extract_expr_from_problem_text(problem_text: str) -> str:
    m = re.search(r"\$(.*?)\$", str(problem_text or ""))
    if m:
        return clean_latex(m.group(1))
    return clean_latex(problem_text or "")


def _normalized_echo_key(text: str) -> str:
    t = str(text or "")
    t = t.replace("$", "").replace("。", "").replace("．", "").replace(".", "")
    t = t.replace("（", "(").replace("）", ")").replace("＋", "+").replace("－", "-")
    return t.replace(" ", "").strip().lower()


def _is_add_sub_only(expr: str) -> bool:
    s = str(expr or "")
    return bool(re.search(r"[+\-]", s)) and (r"\times" not in s) and (r"\div" not in s)


def _operator_lock_type(input_expr: str) -> str:
    s = str(input_expr or "")
    if r"\div" in s:
        return "divide"
    if r"\times" in s:
        return "multiply"
    return "unknown"


def _fmt_sig(sig: Dict[str, Any]) -> str:
    return (
        f"t*{sig.get('times', 0)} d/{sig.get('div', 0)} f{sig.get('frac', 0)} "
        f"sqrt{sig.get('sqrt', 0)} top*{sig.get('top_times', 0)} top/{sig.get('top_div', 0)} "
        f"dep{sig.get('max_paren_depth', 0)} imul{sig.get('implicit_mult', 0)}"
    )


def _debug_meta_line(dm: Dict[str, Any]) -> str:
    if not dm:
        return ""
    pid = dm.get("selected_pattern_id")
    fb = dm.get("fallback_used")
    ig = dm.get("iso_guard_triggered")
    parts = []
    if pid is not None:
        parts.append(f"pattern={pid}")
    parts.append(f"fallback={bool(fb)}")
    parts.append(f"iso_guard={bool(ig)}")
    return " | ".join(parts)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    test_items = collect_pure_math_cases()
    if STRESS_MAX_ITEMS > 0:
        test_items = test_items[:STRESS_MAX_ITEMS]
    total = len(test_items)
    print(f"[START] 壓力測試啟動：共 {len(RAW_STRINGS)} 大題，解析出 {total} 個純淨算式。")
    if STRESS_MAX_ITEMS > 0:
        print(f"[START] STRESS_MAX_ITEMS={STRESS_MAX_ITEMS}（子集模式）")
    print(f"[START] 流程：POST {CLASSIFY_URL}（含大題原文+小題）→ POST {GENERATE_URL}（沿用 json_spec）")
    print("=" * 80)

    passed, failed, crashed = 0, 0, 0
    ab2_pass, ab2_fail = 0, 0
    ab3_pass, ab3_fail = 0, 0
    count_ab2_ok_ab3_drift = 0
    count_ab2_bad = 0
    fail_details = []
    html_rows = []
    pattern_counts: Dict[str, int] = {}
    drift_mismatches: List[Dict[str, Any]] = []
    pattern_overwritten_count = 0
    pattern_audit_first10: List[Dict[str, Any]] = []
    style_audit_first10: List[Dict[str, Any]] = []
    mirror_audit_first10: List[Dict[str, Any]] = []
    radical_items_count = 0
    style_drift_ab2 = 0
    style_drift_ab3 = 0

    for idx, (big, sub, math_expr, parent_raw) in enumerate(test_items, start=1):
        ab2_drift_reason = ""
        ab3_drift_reason = ""
        ab2_issues: List[str] = []
        ab3_issues: List[str] = []
        print(f"\n[TEST] [{idx}/{total}] 正在處理題目 ({big}-{sub}): {math_expr}")

        text_for_classify = build_classify_text_data(parent_raw, math_expr)
        c0 = time.perf_counter()
        ok_c, c_body, c_err = run_classify(text_for_classify)
        classify_elapsed = time.perf_counter() - c0

        if not ok_c:
            print(f"  [FAIL] [CLASSIFY] {c_err}")
            failed += 1
            fail_details.append(
                {"idx": idx, "input": math_expr, "output": "", "errors": [f"classify: {c_err}"]}
            )
            html_rows.append(f"""
                <tr>
                    <td>{idx}</td>
                    <td>${html.escape(math_expr)}$</td>
                    <td>—</td>
                    <td><span style="color:red">—</span></td>
                    <td>—</td>
                    <td><span style="color:red">—</span></td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>❌ {html.escape(c_err)}</td>
                    <td>—</td>
                </tr>
            """)
            continue

        skill_id, ocr_text, json_spec, normalize_notes = normalize_classify_result(c_body, math_expr)

        _ocr_preview = (
            f"{ocr_text[:80]!r}..."
            if len(ocr_text) > 80
            else repr(ocr_text)
        )
        print(
            f"  [CLASSIFY] ({classify_elapsed:.2f}s) skill_id={skill_id} | ocr_text={_ocr_preview}"
        )
        if normalize_notes:
            print(f"  [CLASSIFY-NORMALIZE] {', '.join(normalize_notes)}")

        payload = {
            "input_text": ocr_text,
            "prompt": ocr_text,
            "ablation_mode": False,
            "model_id": "qwen3-vl-8b",
            "model": "qwen3-vl-8b",
            "skill_id": skill_id,
            "json_spec": json_spec,
        }

        try:
            start_t = time.perf_counter()
            r = requests.post(GENERATE_URL, json=payload, timeout=GENERATE_TIMEOUT)
            elapsed = time.perf_counter() - start_t

            if r.status_code == 200:
                data = r.json()
                ab3_problem_text = data.get("problem", "")
                ans = data.get("answer", "")

                dm = data.get("debug_meta")
                if not isinstance(dm, dict):
                    dm = {}
                pid = dm.get("selected_pattern_id")
                pkey = str(pid) if pid is not None else "(none)"
                pattern_counts[pkey] = pattern_counts.get(pkey, 0) + 1
                if dm.get("pattern_overwritten"):
                    pattern_overwritten_count += 1
                if len(pattern_audit_first10) < 10:
                    pattern_audit_first10.append(
                        {
                            "idx": idx,
                            "before": dm.get("selected_pattern_id_before_assemble"),
                            "after": dm.get("selected_pattern_id_after_assemble"),
                            "api_selected": pid,
                            "overwritten": dm.get("pattern_overwritten"),
                            "reason": dm.get("pattern_overwrite_reason"),
                        }
                    )

                backend_error = data.get("error", "")
                if not backend_error and not ab3_problem_text:
                    backend_error = "模型輸出格式嚴重損毀，導致沙盒拒絕執行或正則清空。"

                ab2_problem_text = extract_ab2_problem_text(data)
                ab2_raw = data.get("ab2_result")
                if not isinstance(ab2_raw, dict):
                    ab2_issues = ["Ab2 missing"]
                    ab2_drift_errs: List[str] = []
                    ab2_expected, ab2_sig, ab2_drift_reason = "—", {}, ""
                elif not ab2_problem_text:
                    ab2_issues = ["Ab2 missing"]
                    ab2_drift_errs = []
                    ab2_expected, ab2_sig, ab2_drift_reason = "—", {}, ""
                else:
                    ab2_issues, ab2_drift_errs, ab2_expected, ab2_sig, ab2_drift_reason = (
                        evaluate_problem_track(math_expr, ab2_problem_text)
                    )

                ab3_issues, ab3_drift_errs, expected_type, sig_out, ab3_drift_reason = (
                    evaluate_problem_track(math_expr, ab3_problem_text)
                )
                if not ab3_problem_text:
                    ab3_issues.append(f"❌ 致命崩潰: {backend_error}")

                _input_rs = None
                _ab2_out_rs = "—"
                _ab3_out_rs = "—"
                _ab2_sp = "—"
                _ab3_sp = "—"
                if "FourOperationsOfRadicals" in skill_id:
                    radical_items_count += 1
                    _input_rs = classify_radical_style(ocr_text)
                    if ab3_problem_text:
                        _ab3_out_rs = classify_radical_style(ab3_problem_text)
                        _ok3, _mr3 = radical_hard_style_preserved(_input_rs, _ab3_out_rs)
                        if not _ok3:
                            ab3_issues.append(f"style(Ab3): {_mr3}")
                            style_drift_ab3 += 1
                        _ab3_sp = str(dm.get("style_preserved"))
                        if dm.get("style_preserved") is False:
                            if not any(
                                (isinstance(x, str) and x.startswith("style(Ab3)"))
                                for x in ab3_issues
                            ):
                                ab3_issues.append(
                                    "style(Ab3): debug_meta style_preserved=False"
                                )
                                style_drift_ab3 += 1
                    if ab2_problem_text:
                        _ab2_out_rs = classify_radical_style(ab2_problem_text)
                        _ok2, _mr2 = radical_hard_style_preserved(_input_rs, _ab2_out_rs)
                        if not _ok2:
                            ab2_issues.append(f"style(Ab2): {_mr2}")
                            style_drift_ab2 += 1
                        _ab2_sp = str(dm.get("ab2_style_preserved"))
                        if dm.get("ab2_style_preserved") is False:
                            if not any(
                                (isinstance(x, str) and x.startswith("style(Ab2)"))
                                for x in ab2_issues
                            ):
                                ab2_issues.append(
                                    "style(Ab2): debug_meta ab2_style_preserved=False"
                                )
                                style_drift_ab2 += 1
                    if len(style_audit_first10) < 10:
                        style_audit_first10.append(
                            {
                                "idx": idx,
                                "input_style": _input_rs,
                                "ab2_out": _ab2_out_rs if ab2_problem_text else None,
                                "ab2_preserved": dm.get("ab2_style_preserved"),
                                "ab3_out": _ab3_out_rs if ab3_problem_text else None,
                                "ab3_preserved": dm.get("style_preserved"),
                            }
                        )
                    if len(mirror_audit_first10) < 10:
                        mirror_audit_first10.append(
                            {
                                "idx": idx,
                                "mirror_iso": dm.get("radical_complexity_mirror_isomorphic"),
                                "mirror_diff": dm.get("radical_complexity_mirror_diff"),
                                "iso_isomorphic": dm.get("iso_isomorphic"),
                            }
                        )
                    # New quality-gate diagnostics (Radicals-only)
                    _qg_ok = dm.get("quality_gate_passed")
                    _qg_reasons = dm.get("quality_gate_reasons") or []
                    if _qg_ok is False and isinstance(_qg_reasons, list):
                        for _r in _qg_reasons:
                            if isinstance(_r, str):
                                ab3_issues.append(_r)

                    _expr_out_ab3 = _extract_expr_from_problem_text(ab3_problem_text)
                    _cmd_cnt_ab3 = ab3_problem_text.count("化簡") + ab3_problem_text.count("計算")
                    if ("；" in ab3_problem_text) or (_cmd_cnt_ab3 > 1):
                        ab3_issues.append("single_problem_violation")

                    _in_echo_norm = _normalized_echo_key(math_expr)
                    _out_echo_norm = _normalized_echo_key(_expr_out_ab3)
                    _sim = (
                        SequenceMatcher(None, _in_echo_norm, _out_echo_norm).ratio()
                        if _expr_out_ab3
                        else 0.0
                    )
                    if _expr_out_ab3:
                        _echo_hit = (_in_echo_norm == _out_echo_norm)
                        if (not _echo_hit) and STRESS_ECHO_RULE == "similarity":
                            _echo_hit = (_sim > 0.92)
                        if _echo_hit:
                            ab3_issues.append("echo_violation")
                    # Keep report readable: same reason may be emitted by both
                    # debug_meta quality gate and local checks.
                    if ab3_issues:
                        ab3_issues = list(dict.fromkeys(ab3_issues))

                    _lock = _operator_lock_type(math_expr)
                    if _lock in {"multiply", "divide", "rationalize_den_sqrt"} and _is_add_sub_only(_expr_out_ab3):
                        ab3_issues.append("operator_lock_violation")

                    # Pattern family acceptance (Radicals-only critical exemplars)
                    _pid = str(dm.get("selected_pattern_id") or "")
                    _in_norm = _normalized_echo_key(math_expr)
                    if _in_norm == _normalized_echo_key(r"(\sqrt{3}+2\sqrt{2}\quad)^2"):
                        _looks_p2d = bool(re.search(r"\)\^2$", _normalized_echo_key(_expr_out_ab3 or "")))
                        if not (_pid.startswith("p2d") or _pid == "p2d_perfect_square" or _looks_p2d):
                            ab3_issues.append("pattern_family_violation:p2d_required")
                    if _in_norm == _normalized_echo_key(r"(\sqrt{3}-2\sqrt{2})(\sqrt{3}+2\sqrt{2})"):
                        if not (_pid.startswith("p2e") or _pid == "p2e_diff_of_squares"):
                            ab3_issues.append("pattern_family_violation:p2e_required")
                    if _in_norm == _normalized_echo_key(r"\frac{1}{\sqrt{3}-\sqrt{2}}"):
                        if not (_pid.startswith("p5a") or _pid == "p5a_conjugate_int"):
                            ab3_issues.append("pattern_family_violation:p5a_required")

                ab2_ok = not ab2_issues
                ab3_ok = not ab3_issues
                if ab2_ok:
                    ab2_pass += 1
                else:
                    ab2_fail += 1
                if ab3_ok:
                    ab3_pass += 1
                else:
                    ab3_fail += 1
                if ab2_ok and not ab3_ok and ab3_drift_errs:
                    count_ab2_ok_ab3_drift += 1
                if not ab2_ok:
                    count_ab2_bad += 1

                issues = ab2_issues + ab3_issues

                dbg_line = _debug_meta_line(dm)
                mismatch_cell = ""
                if ab2_drift_reason or ab3_drift_reason:
                    mismatch_cell += "<b>Ab2</b>: " + html.escape(ab2_drift_reason or "—")
                    mismatch_cell += "<br><b>Ab3</b>: " + html.escape(ab3_drift_reason or "—")
                else:
                    mismatch_cell = "—"
                if dbg_line:
                    mismatch_cell += f"<br><small>{html.escape(dbg_line)}</small>"

                def _status_cell(ok: bool, errs: List[str]) -> str:
                    if ok:
                        return "✅ PASS"
                    return "❌ " + html.escape("; ".join(errs)[:400])

                status_icon = "✅" if (ab2_ok and ab3_ok) else "❌"
                overall_msg = []
                if not ab2_ok:
                    overall_msg.append(f"Ab2: {'; '.join(ab2_issues)}")
                if not ab3_ok:
                    overall_msg.append(f"Ab3: {'; '.join(ab3_issues)}")
                _style_html = (
                    f"input={html.escape(str(_input_rs))}<br>"
                    f"Ab2 out={html.escape(str(_ab2_out_rs))} preserved={html.escape(str(_ab2_sp))}<br>"
                    f"Ab3 out={html.escape(str(_ab3_out_rs))} preserved={html.escape(str(_ab3_sp))}"
                    if _input_rs is not None
                    else "—"
                )
                html_rows.append(f"""
                <tr>
                    <td>{idx}</td>
                    <td>${html.escape(math_expr)}$<br><small>classify ocr: {html.escape(ocr_text[:120])}{'…' if len(ocr_text) > 120 else ''}</small><br><small>skill: {html.escape(skill_id)}</small></td>
                    <td>{html.escape(ab2_problem_text) if ab2_problem_text else '<span style="color:red"><b>[無 Ab2 題幹]</b></span>'}</td>
                    <td>{_status_cell(ab2_ok, ab2_issues)}</td>
                    <td>{html.escape(ab3_problem_text) if ab3_problem_text else '<span style="color:red"><b>[無產出]</b></span>'}</td>
                    <td>{_status_cell(ab3_ok, ab3_issues)}</td>
                    <td>{html.escape(str(ans))}</td>
                    <td>{html.escape(expected_type)}</td>
                    <td><code>{html.escape(_fmt_sig(sig_out))}</code><br><small>Ab2 sig: {html.escape(_fmt_sig(ab2_sig) if isinstance(ab2_sig, dict) else '')}</small></td>
                    <td>{mismatch_cell}</td>
                    <td>{_style_html}</td>
                    <td>{status_icon} {html.escape(' | '.join(overall_msg))}</td>
                    <td>cls {classify_elapsed:.2f}s / gen {elapsed:.2f}s</td>
                </tr>
                """)

                if ab2_drift_errs or ab3_drift_errs:
                    drift_mismatches.append(
                        {
                            "idx": idx,
                            "input": math_expr,
                            "ab2_text": ab2_problem_text,
                            "ab3_text": ab3_problem_text,
                            "ab2_drift": bool(ab2_drift_errs),
                            "ab3_drift": bool(ab3_drift_errs),
                            "ab2_reason": ab2_drift_reason,
                            "ab3_reason": ab3_drift_reason,
                            "expected_type": expected_type,
                            "pattern_id": pid,
                            "debug": dbg_line,
                        }
                    )

                if ab2_ok and ab3_ok:
                    print(
                        f"  [PASS] (classify {classify_elapsed:.2f}s, generate {elapsed:.2f}s) "
                        f"Ab2/Ab3 皆通過 | Ab3 題幹: {ab3_problem_text[:80]}{'…' if len(ab3_problem_text) > 80 else ''}"
                    )
                    passed += 1
                else:
                    print(f"  [Ab2] {'PASS' if ab2_ok else 'FAIL'}{'' if ab2_ok else ': ' + '; '.join(ab2_issues)}")
                    print(f"  [Ab3] {'PASS' if ab3_ok else 'FAIL'}{'' if ab3_ok else ': ' + '; '.join(ab3_issues)}")
                    if not ab2_ok:
                        print(f"     Ab2 題幹: {ab2_problem_text[:200]!r}")
                    if not ab3_ok:
                        print(f"     Ab3 題幹: {ab3_problem_text[:200]!r}")
                    failed += 1
                    fail_details.append(
                        {
                            "idx": idx,
                            "input": math_expr,
                            "output_ab2": ab2_problem_text,
                            "output_ab3": ab3_problem_text,
                            "errors_ab2": ab2_issues,
                            "errors_ab3": ab3_issues,
                            "errors": issues,
                        }
                    )
            else:
                msg = f"generate_live HTTP {r.status_code}: {(r.text or '')[:300]}"
                print(f"  [CRASH] {msg}")
                crashed += 1
                html_rows.append(f"""
                <tr>
                    <td>{idx}</td>
                    <td>${html.escape(math_expr)}$<br><small>classify ocr: {html.escape(ocr_text[:120])}{'…' if len(ocr_text) > 120 else ''}</small><br><small>skill: {html.escape(skill_id)}</small></td>
                    <td>—</td>
                    <td>—</td>
                    <td><span style="color:red"><b>[HTTP 錯誤]</b></span></td>
                    <td>—</td>
                    <td></td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>❌ {html.escape(msg)}</td>
                    <td>cls {classify_elapsed:.2f}s</td>
                </tr>
                """)
                fail_details.append({"idx": idx, "input": math_expr, "output": "", "errors": [msg]})
        except Exception as e:
            print(f"  [CRASH] 連線錯誤: {str(e)}")
            crashed += 1
            html_rows.append(f"""
                <tr>
                    <td>{idx}</td>
                    <td>${html.escape(math_expr)}$<br><small>classify ocr: {html.escape(ocr_text[:120])}{'…' if len(ocr_text) > 120 else ''}</small><br><small>skill: {html.escape(skill_id)}</small></td>
                    <td>—</td>
                    <td>—</td>
                    <td><span style="color:red"><b>[連線例外]</b></span></td>
                    <td>—</td>
                    <td></td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>❌ {html.escape(str(e))}</td>
                    <td>cls {classify_elapsed:.2f}s</td>
                </tr>
            """)
            fail_details.append({"idx": idx, "input": math_expr, "output": "", "errors": [str(e)]})

    print("\n" + "=" * 80)
    print("[REPORT] 最終測試報表")
    print("-" * 80)
    print(f"  總測試數: {total}")
    print(f"  成功 (PASS, Ab2+Ab3 皆過): {passed}")
    print(f"  瑕疵 (FAIL): {failed}")
    print(f"  崩潰 (CRASH): {crashed}")
    print(f"  Ab2 通過: {ab2_pass} | Ab2 失敗: {ab2_fail}")
    print(f"  Ab3 通過: {ab3_pass} | Ab3 失敗: {ab3_fail}")
    print(f"  [診斷] Ab2 正常但 Ab3 題型漂移: {count_ab2_ok_ab3_drift} 題（傾向 healer/Ab3 路徑問題）")
    print(f"  [診斷] Ab2 已失敗（含 Ab2 missing/漂移）: {count_ab2_bad} 題（非僅 healer 造成）")
    if total:
        print(f"  整體成功率 (雙軌皆過): {passed / total * 100:.1f}%")
    print("=" * 80)

    if pattern_counts:
        print("\n[PATTERN] selected_pattern_id 分布（debug_meta，含 (none)）：")
        for k, v in sorted(pattern_counts.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {k!r}: {v}")
    print(f"\n[PATTERN] pattern_overwritten count (debug_meta): {pattern_overwritten_count}")
    if radical_items_count:
        print(
            f"[STYLE] FourOperations items={radical_items_count} "
            f"drift_ab2={style_drift_ab2} ({100.0 * style_drift_ab2 / radical_items_count:.1f}%) "
            f"drift_ab3={style_drift_ab3} ({100.0 * style_drift_ab3 / radical_items_count:.1f}%)"
        )
    if pattern_audit_first10:
        print("[PATTERN] first items: before/after universal assemble vs API selected_pattern_id:")
        for row in pattern_audit_first10:
            print(
                f"  [#{row['idx']}] before={row['before']!r} after={row['after']!r} "
                f"api_selected={row['api_selected']!r} overwritten={row['overwritten']!r} "
                f"reason={row['reason']!r}"
            )
    if style_audit_first10:
        print("[STYLE] first items: input_style / output_style / style_preserved (debug_meta):")
        for row in style_audit_first10:
            print(
                f"  [#{row['idx']}] in={row['input_style']!r} "
                f"Ab2 out={row['ab2_out']!r} preserved={row['ab2_preserved']!r} | "
                f"Ab3 out={row['ab3_out']!r} preserved={row['ab3_preserved']!r}"
            )
    if mirror_audit_first10:
        print(
            "[MIRROR] Radicals radical_complexity_mirror_* (debug_meta) + iso_isomorphic:"
        )
        for row in mirror_audit_first10:
            print(
                f"  [#{row['idx']}] mirror_iso={row['mirror_iso']!r} "
                f"mirror_diff={row['mirror_diff']!r} "
                f"iso_isomorphic={row['iso_isomorphic']!r}"
            )

    if drift_mismatches:
        print("\n[DRIFT] 運算骨架漂移（前 10 筆，Ab2/Ab3 分開標示）：")
        for row in drift_mismatches[:10]:
            print(
                f"  [#{row['idx']}] expected={row['expected_type']!r}\n"
                f"       Ab2 drift={row.get('ab2_drift')} reason={row.get('ab2_reason')!r}\n"
                f"       Ab3 drift={row.get('ab3_drift')} reason={row.get('ab3_reason')!r}\n"
                f"       in : {row['input']!r}\n"
                f"       Ab2: {row.get('ab2_text', '')!r}\n"
                f"       Ab3: {row.get('ab3_text', '')!r}\n"
                f"       {row.get('debug', '')}"
            )

    if fail_details:
        print("\n[DIAG] 瑕疵題目診斷清單：")
        for f in fail_details:
            if "errors_ab2" in f:
                print(
                    f"- [#{f['idx']}] 輸入: {f['input']} | "
                    f"Ab2: {f.get('errors_ab2')} | Ab3: {f.get('errors_ab3')}"
                )
            else:
                print(f"- [#{f['idx']}] 輸入: {f['input']} | 輸出: {f.get('output', '')} | 原因: {f['errors']}")

    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>MathProject 壓力測試渲染報表 (Ab2 + Ab3)</title>
    <script>
        MathJax = {{
            tex: {{ inlineMath: [['$', '$']] }}
        }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; vertical-align: top; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background: #fafafa; }}
    </style>
</head>
<body>
    <h2>根式四則運算 (Qwen3-VL-8B + Active Healer) 壓力測試 — Ab2 / Ab3 分軌</h2>
    <p>流程：每題先 <code>/api/classify</code>（text_data = 大題原文 + 小題算式），再以回傳的 <code>json_spec</code> + <code>ocr_text</code> 呼叫 <code>/api/generate_live</code>。</p>
    <p>總測試數: {total} | 雙軌皆過: {passed} | 失敗: {failed} | 崩潰: {crashed}</p>
    <p>Ab2 通過: {ab2_pass} | Ab2 失敗: {ab2_fail} | Ab3 通過: {ab3_pass} | Ab3 失敗: {ab3_fail}</p>
    <p>Ab2 正常但 Ab3 漂移: {count_ab2_ok_ab3_drift} 題 | Ab2 已失敗（含 missing）: {count_ab2_bad} 題</p>
    <p>pattern_overwritten (debug_meta) 次數: {pattern_overwritten_count}</p>
    <p>根式技能小題數: {radical_items_count} | style 漂移 Ab2: {style_drift_ab2} | Ab3: {style_drift_ab3}</p>
    <table>
        <tr><th>編號</th><th>課本小題 / classify</th><th>Ab2 生成題幹</th><th>Ab2 狀態</th>
        <th>Ab3 生成題幹</th><th>Ab3 狀態</th><th>生成答案 (Ab3)</th>
        <th>expected_type</th><th>output_signature</th><th>漂移摘要 (Ab2/Ab3)</th>
        <th>根式風格 (in / Ab2 out / Ab3 out)</th><th>整體狀態</th><th>耗時</th></tr>
        {''.join(html_rows)}
    </table>
</body>
</html>
"""
    report_path = os.path.join(os.path.dirname(__file__), "stress_test_report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"\n[HTML] 已產生視覺化報表：{report_path} (請用瀏覽器開啟以檢查 LaTeX 渲染)")


if __name__ == "__main__":
    main()
