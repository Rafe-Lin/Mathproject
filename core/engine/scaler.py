# -*- coding: utf-8 -*-
import os
import uuid
import random
import time
import sys
import importlib.util
import ast
from core.ai_wrapper import get_ai_client, call_ai_with_retry
from core.code_generator import auto_generate_skill_code
from config import Config

# 合法 pattern_id 清單（與 domain_functions.py / SKILL.md 對齊，防止假 ID 觸發強制萃取）
RADICAL_VALID_PATTERN_IDS = [
    'p0_simplify', 'p1_add_sub', 'p2a_mult_direct', 'p2b_mult_distrib',
    'p2c_mult_binomial', 'p2f_int_mult_rad', 'p2g_rad_mult_frac',
    'p2h_frac_mult_rad', 'p2d_perfect_square', 'p2e_diff_of_squares',
    'p3a_div_expr', 'p3c_div_direct', 'p3b_div_simple', 'p4_frac_mult',
    'p4b_frac_rad_div', 'p4c_nested_frac_chain', 'p4d_frac_rad_div_mixed', 'p5a_conjugate_int',
    'p5b_conjugate_rad', 'p6_combo', 'p7_mixed_rad_add',
    'p1b_add_sub_bracket', 'p1c_mixed_frac_rad_add_sub',
]

# 短別名 → 完整 ID（模糊匹配，減少 8B 模型壓力）
RADICAL_FUZZY_PREFIX_MAP = {
    'p0': 'p0_simplify', 'p1': 'p1_add_sub', 'p2a': 'p2a_mult_direct',
    'p2b': 'p2b_mult_distrib', 'p2c': 'p2c_mult_binomial', 'p2d': 'p2d_perfect_square',
    'p2e': 'p2e_diff_of_squares', 'p2f': 'p2f_int_mult_rad', 'p2g': 'p2g_rad_mult_frac',
    'p2h': 'p2h_frac_mult_rad', 'p3a': 'p3a_div_expr', 'p3b': 'p3b_div_simple',
    'p3c': 'p3c_div_direct', 'p4': 'p4_frac_mult', 'p4b': 'p4b_frac_rad_div',
    'p4c': 'p4c_nested_frac_chain', 'p4d': 'p4d_frac_rad_div_mixed', 'p5a': 'p5a_conjugate_int', 'p5b': 'p5b_conjugate_rad',
    'p6': 'p6_combo', 'p7': 'p7_mixed_rad_add',
    'p1b': 'p1b_add_sub_bracket', 'p1c': 'p1c_mixed_frac_rad_add_sub',
}


def _resolve_radical_pattern_id(matched: str, raw_text: str) -> str | None:
    """將模型輸出的 pattern_id（可能為短別名或幻覺）解析為合法 ID。"""
    if not matched:
        return None
    s = matched.strip()
    if s in RADICAL_VALID_PATTERN_IDS:
        return s
    if s in RADICAL_FUZZY_PREFIX_MAP:
        return RADICAL_FUZZY_PREFIX_MAP[s]
    # p3 或含 div/÷ 時預設為兩根式相除
    if (s.startswith("p3") or s == "p3") and ("div" in raw_text or "÷" in raw_text or "\\div" in raw_text):
        return "p3c_div_direct"
    # 前綴匹配：僅當唯一時採用
    candidates = [vid for vid in RADICAL_VALID_PATTERN_IDS if vid.startswith(s) or s.startswith(vid)]
    if len(candidates) == 1:
        return candidates[0]
    return None

class AdaptiveScaler:
    """
    AdaptiveScaler 負責根據技能與難度生成題目。
    採用 JIT (Just-in-Time) 模式：根據需求動態生成並執行出題腳本。
    """
    def __init__(self, model_role='generator'):
        self.model_role = model_role
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def _get_skill_path(self, skill_name):
        return os.path.join(self.project_root, "agent_skills", skill_name)

    def _get_skill_vision_input(self, skill_name: str) -> bool:
        """讀取 skill.json["vision_input"]；不存在則回傳 False。"""
        manifest = os.path.join(self._get_skill_path(skill_name), "skill.json")
        if os.path.isfile(manifest):
            try:
                import json as _json
                with open(manifest, encoding="utf-8") as fh:
                    return bool(_json.load(fh).get("vision_input", False))
            except Exception:
                pass
        return False

    def _call_ai_vision(self, prompt: str, image_base64: str, model_config: dict) -> tuple:
        """多模態 AI 呼叫（Qwen3-VL）。
        目前所有 skill 的 vision_input=false，此方法為未來擴充預留。
        Returns: (raw_code, _, _, thinking_text)
        """
        from core.code_generator import _call_ai
        # 當 skill.json vision_input=true 且有 image 時呼叫；暫時 fallback 到純文字
        if image_base64:
            try:
                import requests, base64, json as _json
                from config import Config
                url = model_config.get("base_url", "http://127.0.0.1:11434") + "/api/chat"
                payload = {
                    "model": model_config.get("model", "qwen3-vl:8b-instruct-q4_k_m"),
                    "messages": [{"role": "user", "content": [
                        {"type": "text",  "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                    ]}],
                    "stream": False,
                    "options": {"num_predict": model_config.get("max_tokens", 4096)},
                }
                resp = requests.post(url, json=payload, timeout=120)
                resp.raise_for_status()
                content = resp.json().get("message", {}).get("content", "")
                return content, None, None, ""
            except Exception as e:
                print(f"[WARN] _call_ai_vision failed ({e}), fallback to text-only")
        return _call_ai(prompt, model_config=model_config)

    def _load_skill_prompt(self, skill_path: str, mode: str = "LIVESHOW") -> str | None:
        """優先讀取 mode-specific prompt 檔（prompt_liveshow.md / prompt_benchmark.md）。
        若不存在則回傳 None，呼叫端 fallback 到 SKILL.md 切割邏輯。
        """
        mode_file = os.path.join(skill_path, f"prompt_{mode.lower()}.md")
        if os.path.isfile(mode_file):
            with open(mode_file, encoding="utf-8") as fh:
                raw = fh.read()
            return "\n".join(line.replace('\r', '') for line in raw.splitlines())
        return None

    def _is_radical_simplifiable(self, n):
        """檢查一個數字是否可以從根號中化簡（即包含大於1的平方數因數）"""
        n = int(n)
        if n <= 1:
            return False
        i = 2
        while i * i <= n:
            if n % (i * i) == 0:
                return True
            i += 1
        return False

    def _analyze_radical_style(self, latex_string):
        """分析輸入的 LaTeX 字串，判斷其根式風格"""
        import re
        # 從 \sqrt{...} 中提取所有數字
        # [Fix] 支援 \sqrt (單反斜線) 與 \\sqrt (雙反斜線) 兩種情況，避免因轉義導致漏抓
        radicands = [int(n) for n in re.findall(r'\\{1,2}sqrt\{(\d+)\}', latex_string)]
        if not radicands:
            return 'simplified'  # 如果沒有根號，預設為最簡風格

        # 只要有一個根式可以化簡，就整體視為「需化簡」風格
        if any(self._is_radical_simplifiable(r) for r in radicands):
            return 'simplifiable'
        else:
            return 'simplified'

    def generate_problem(self, skill_name, level=2):
        """
        生成指定技能與難度的題目。
        Args:
            skill_name: 技能名稱 (例如 jh_數學2上_FourOperationsOfRadicals)
            level: 1 (Easy), 2 (Normal), 3 (Hard)
        Returns:
            dict: 包含題目的字典
        """
        skill_path = self._get_skill_path(skill_name)
        skill_md_path = os.path.join(skill_path, "SKILL.md")
        
        if not os.path.exists(skill_md_path):
            raise FileNotFoundError(f"找不到技能定義: {skill_md_path}")

        difficulty_names = {1: "EASY (簡單)", 2: "NORMAL (標準)", 3: "HARD (進階/挑戰)"}
        print(f"[INFO] 正在為 {skill_name} 生成 {difficulty_names.get(level)} 等級的題目代碼...")
        
        # 使用 auto_generate_skill_code
        # 它會回傳一個結果路徑或狀態
        try:
            # 這裡我們利用 ablation_id=2 (Regex Healed)
            # auto_generate_skill_code 會將檔案寫入 agent_tools/reports/...
            # 我們需要抓到它是哪一個檔案
            from core.code_utils.file_utils import ensure_dir
            
            # [Optimization] 這裡我們直接傳入 level 參數作為 kwargs，
            # 但目前的 auto_generate_skill_code 可能不會直接把 level 傳給 AI。
            # 沒關係，SKILL.md 裡面的 generate(level) 會處理。
            
            # 執行生成
            # 注意：auto_generate_skill_code 會回傳生成的 code 字串 (在 V50.0 版本中是有回傳的嗎？)
            # 讓我們檢查一下 auto_generate_skill_code 的定義。
            # 根據 outline，它回傳的可能是成果路徑。
            
            # 這裡我們做一個簡化：直接呼叫後，從回傳或生成的路徑讀取。
            # 但為了效率，我們可以直接從 generate_skill_code 邏輯中提取。
            
            # 其實，我們可以更直接一點：因為我們要的是「執行」，
            # 我們可以直接呼叫 auto_generate_skill_code，然後它會存檔。
            # 然後我們再去載入那個檔。
            
            # [修正] 其實在 V50.0 版本的 code_generator 中，
            # auto_generate_skill_code 的實作會把檔案存在特定的 report 目錄下。
            
            # 為了測試，我們先假設它能運作。
            # 如果要更精準，我應該檢查 auto_generate_skill_code 的回傳值。
            
            # [Hack] 這裡我改用更底層的 _build_prompt + _call_ai + _basic_cleanup 
            # 這樣可以直接拿到 code 字串。
            
            from core.code_generator import _build_prompt, _call_ai, _basic_cleanup, _advanced_healer, _inject_domain_libs
            
            # 1. 構建 Prompt
            # 這裡我們讀取 SKILL.md 並與骨架結合
            # 簡化起見，我們借用 code_generator 的內部邏輯
            
            # 讀取 SKILL.md
            with open(skill_md_path, "r", encoding="utf-8") as f:
                skill_spec = f.read()
            
            # 呼叫 AI (這裡我們跳過 DB logging，直接拿 code)
            prompt = f"{skill_spec}\n\n【特別要求】請生成難度為 {difficulty_names.get(level)} 的題目內容。"
            
            # [Fix] 使用 Qwen3-8B 作為預設發案模型
            from config import Config
            model_config = Config.CODER_PRESETS.get('qwen3.5-9b') or Config.CODER_PRESETS.get('qwen3-8b')
            raw_code, _, _, _ = _call_ai(prompt, model_config=model_config)
            
            # 2. 清理與修復
            # [Fix] _basic_cleanup 回傳的是 (code, fixes_count)
            clean_code, _ = _basic_cleanup(raw_code)
            
            # [Fix] 預設使用 ablation_id=3 (AST Healed) 以獲得最高成功率
            healed_code, *healer_stats = _advanced_healer(clean_code, ablation_id=3, skill_id=skill_name)
            
            def _ensure_generate_block(code_text, fallback_source):
                import re
                code_out = code_text or ""
                if re.search(r"^\s*def\s+generate\s*\(", code_out, flags=re.MULTILINE):
                    return code_out
                src = fallback_source or ""
                m = re.search(r"^\s*def\s+generate\s*\(", src, flags=re.MULTILINE)
                if m:
                    recovered = src[m.start():].strip()
                    if recovered:
                        if code_out and not code_out.endswith("\n"):
                            code_out += "\n"
                        code_out += "\n\n" + recovered if code_out else recovered
                return code_out

            # 3. 注入 Libs
            # [Fix] _inject_domain_libs 回傳的是 (code, injected_list)
            final_code, _ = _inject_domain_libs(healed_code)
            final_code = _ensure_generate_block(final_code, clean_code)
            try:
                ast.parse(final_code)
            except SyntaxError:
                final_code, _ = _inject_domain_libs(clean_code)
                final_code = _ensure_generate_block(final_code, clean_code)
            if (not re.search(r"^\s*def\s+generate\s*\(", final_code, flags=re.MULTILINE)) and re.search(r"^\s*def\s+generate\s*\(", clean_code, flags=re.MULTILINE):
                final_code = clean_code
            if not re.search(r"^\s*def\s+generate\s*\(", final_code, flags=re.MULTILINE):
                final_code = self._build_emergency_generate_code("計算 1+1 的值。")
            
            return self._execute_code(final_code, level)

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"代碼生成或執行失敗: {e}")

    def generate_custom_problems(self, skill_name, input_text, count=5, model_id='qwen3.5-9b', ablation_mode=False):
        """
        根據輸入例題，完全模仿題型生成 count 題。
        ablation_mode: 若為 True (Ab1 模式)，跳過 SKILL.md 讀取與 Healer 修復，使用原生 Prompt。
        """
        # 1. 根據您的正確清單進行資源定位 (Domain Mapping)
        domain_config = {
            "OfIntegers": "IntegerOps",
            "OfNumbers": "FractionOps",
            "OfPolynomial": "PolynomialOps",
            "OfRadicals": "RadicalOps"
        }
        
        target_ops = "IntegerOps" # 預設
        for key, val in domain_config.items():
            if key in skill_name:
                target_ops = val
                break
                
        try:
            from core.code_generator import _call_ai, _basic_cleanup, _advanced_healer, _inject_domain_libs
            
            if ablation_mode:
                print(f"[WARN] [Ab1] 載入 {skill_name} Baseline Prompt。")
                skill_path = self._get_skill_path(skill_name)
                ab1_prompt_path = os.path.join(skill_path, "experiments", "ab1_bare_prompt.md")
                if os.path.exists(ab1_prompt_path):
                    with open(ab1_prompt_path, "r", encoding="utf-8") as f:
                        ab1_template = f.read()
                    import re
                    # 使用正則替換【參考例題】區塊，把題目換成我們提供的 input_text
                    prompt = re.sub(
                        r"【參考例題】.*?【程式要求】", 
                        lambda _m: f"【參考例題】\n{input_text}\n\n【程式要求】", 
                        ab1_template, 
                        flags=re.DOTALL
                    )
                else:
                    prompt = f"請寫一個 generate(level=1) 函式，參考：\n{input_text}\n直接輸出代碼。"
                active_ablation_id = 1
            else:
                print(f"[INFO] [Ab3] 鎖定 {skill_name} 基因庫...")
                skill_path = self._get_skill_path(skill_name)
                skill_md_path = os.path.join(skill_path, "SKILL.md")
                if not os.path.exists(skill_md_path):
                    raise FileNotFoundError(f"找不到技能定義: {skill_md_path}")

                # ── Phase 3-B: mode-aware prompt loading ──────────────────────
                liveshow_prompt = self._load_skill_prompt(skill_path, "LIVESHOW")
                # ──────────────────────────────────────────────────────────────

                with open(skill_md_path, "r", encoding="utf-8") as f:
                    raw_text = f.read()
                    # 徹底消除 Windows CRLF 導致的 f-string 游標回車覆寫問題
                    full_skill_spec = "\n".join([line.replace('\r', '') for line in raw_text.splitlines()])

                # 使用明確的切斷錨點，截取基礎規則與 LIVESHOW 區段
                skill_spec_distilled = full_skill_spec.split("=== SKILL_END_PROMPT ===")[0].strip()
                if "OfRadicals" in skill_name:
                    try:
                        from core.routes.live_show import compact_radical_skill_for_liveshow
                        skill_spec_distilled = compact_radical_skill_for_liveshow(skill_spec_distilled)
                    except ImportError:
                        pass

                import re
                benchmark_match = re.search(r'\[\[MODE:BENCHMARK\]\]([\s\S]*?)\[\[END_MODE:BENCHMARK\]\]', full_skill_spec)
                benchmark_content = benchmark_match.group(1).strip() if benchmark_match else ""

                if liveshow_prompt:
                    # ── [架構規範] 組合 SKILL.md base + prompt_liveshow.md delta ──
                    assembled_liveshow = f"{skill_spec_distilled}\n=== SKILL_END_PROMPT ===\n\n{liveshow_prompt}"
                    input_text_safe = self._sanitize_input_dna(input_text)
                    try:
                        from core.routes.live_show import apply_strict_mirroring
                        assembled_liveshow = apply_strict_mirroring(assembled_liveshow, input_text_safe)
                    except ImportError:
                        pass

                    # Fetch api_stubs for Ab2 interception (same as fallback path)
                    from core.prompts.domain_function_library import get_required_domains, get_domain_helpers_code
                    required_domains = get_required_domains(skill_name)
                    api_stubs = get_domain_helpers_code(required_domains, stub_mode=True)

                    # [新增] 根據輸入例題分析根式風格，動態生成 Prompt 指令
                    radical_style_prompt = ""
                    if "OfRadicals" in skill_name:
                        style = self._analyze_radical_style(input_text_safe)
                        if style == 'simplifiable':
                            radical_style_prompt = "\n【根式風格】: 例題包含需化簡的根式 (如 √8)，你生成的題目也必須包含需化簡的根式。"
                        else:  # 'simplified'
                            radical_style_prompt = "\n【根式風格】: 例題的根式皆為最簡根式 (如 √2)，你生成的題目也必須只使用最簡根式。"
                            # [Auto-Fix] 若為最簡風格，強制替換 Scaffolding 中的 simplifiable 列表，避免 AI 照抄舊列表
                            import re
                            assembled_liveshow = re.sub(
                                r"(\s*)simplifiable\s*=\s*\[.*?\]",
                                r"\1simplifiable = [2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22, 23, 26, 29, 30, 31, 33, 34, 35, 37, 38, 39, 41, 42]",
                                assembled_liveshow,
                                flags=re.DOTALL  # [Fix] 確保即使列表跨行也能正確替換
                            )

                    if "OfRadicals" in skill_name:
                        prompt = f"""{assembled_liveshow}
{radical_style_prompt}
【動態目標題型參考】
{input_text_safe}
"""
                    else:
                        prompt = f"""{assembled_liveshow}
{radical_style_prompt}
【動態目標題型參考】
{input_text_safe}

【硬性一致性約束（必須遵守）】
1. 嚴格鏡像目標題型結構，不得新增題型中不存在的運算符號。
2. 必須使用對應 Domain API（例如 IntegerOps / FractionOps / PolynomialOps / RadicalOps）。
   (API 原始碼已從 Prompt 移除以節省 Token，AI 需依賴 SKILL.md 的範例與規則來學習使用。)
3. 題目中的乘號與除號必須使用 \\times 與 \\div。
4. 程式碼輸出格式請嚴格遵守你所選的路徑（路徑 A 僅需 3 行變數宣告，路徑 B 才需完整 generate 函式）。
5. 不要輸出 JSON、不要輸出 markdown 解釋、更不要在 Python 區塊外寫任何廢話（如 "生成的代碼如下"）。
6. 允許將數字隨機化，但必須完全保持原題的運算結構與項數。
7. 必須保留原題的運算骨架：項數、括號層級、絕對值位置、正負號配置與運算符集合需一致。
8. 禁止新增原題沒有的運算（例如原題沒有絕對值時，不得自行加入 | |）。
9. `question_text` 必須是對原題算式的標準化 LaTeX 呈現，不得改題意。
"""
                else:
                    # ── Fallback：舊邏輯（SKILL.md 切割 + BENCHMARK section）──
                    input_text_safe = self._sanitize_input_dna(input_text)
                    try:
                        from core.routes.live_show import apply_strict_mirroring
                        skill_spec_distilled = apply_strict_mirroring(skill_spec_distilled, input_text_safe)
                    except ImportError:
                        pass

                    from core.prompts.domain_function_library import get_required_domains, get_domain_helpers_code
                    required_domains = get_required_domains(skill_name)
                    api_stubs = get_domain_helpers_code(required_domains, stub_mode=True)

                    # [新增] 根據輸入例題分析根式風格，動態生成 Prompt 指令
                    radical_style_prompt = ""
                    if "OfRadicals" in skill_name:
                        style = self._analyze_radical_style(input_text_safe)
                        if style == 'simplifiable':
                            radical_style_prompt = "\n【根式風格】: 例題包含需化簡的根式 (如 √8)，你生成的題目也必須包含需化簡的根式。"
                        else:  # 'simplified'
                            radical_style_prompt = "\n【根式風格】: 例題的根式皆為最簡根式 (如 √2)，你生成的題目也必須只使用最簡根式。"

                    prompt = f"""# Math-Master 核心開發任務

【1. 數學基因 (From SKILL.md)】
{skill_spec_distilled}

【2. 實作規範與模板 (From BENCHMARK)】
{benchmark_content}
{radical_style_prompt}
【3. 動態目標題型參考】
{input_text_safe}

【最高實作準則】
1. 嚴格鏡像目標題型結構，不得新增題型中不存在的運算符號。
2. 必須使用對應 Domain API（例如 IntegerOps / FractionOps / PolynomialOps / RadicalOps）。
   (API 原始碼已從 Prompt 移除以節省 Token，AI 需依賴 SKILL.md 的範例與規則來學習使用。)
3. 題目中的乘號與除號必須使用 \\times 與 \\div。
4. 程式碼輸出格式請嚴格遵守你所選的路徑（路徑 A 僅需 3 行變數宣告，路徑 B 才需完整 generate 函式）。
5. 不要輸出 JSON、不要輸出 markdown 解釋、更不要在 Python 區塊外寫任何廢話（如 "生成的代碼如下"）。

【硬性一致性約束（必須遵守）】
6. 允許將數字隨機化，但必須完全保持原題的運算結構與項數。
7. 必須保留原題的運算骨架：項數、括號層級、絕對值位置、正負號配置與運算符集合需一致。
8. 禁止新增原題沒有的運算（例如原題沒有絕對值時，不得自行加入 | |）。
9. `question_text` 必須是對原題算式的標準化 LaTeX 呈現，不得改題意。
"""
                active_ablation_id = 3
            
            from config import Config
            model_config = Config.CODER_PRESETS.get(model_id) or Config.CODER_PRESETS.get('qwen3.5-9b') or Config.CODER_PRESETS.get('qwen3-8b')
            
            start_ai = time.time()
            # ── Phase 4-A: vision_input routing ────────────────────────────
            use_vision = (not ablation_mode) and self._get_skill_vision_input(skill_name)
            # ───────────────────────────────────────────────────────────────
            if not ablation_mode:
                print("========================================")
                print("[INFO] [Ab3] 單階段 Qwen 直出代碼...")
                print("========================================")
                print("=== [DEBUG] 發送給 Qwen 的 PROMPT 內容 ===")
                print(prompt)
                print("========================================")
                if use_vision:
                    raw_code, _, _, thinking_text = self._call_ai_vision(prompt, "", model_config)
                else:
                    raw_code, _, _, thinking_text = _call_ai(prompt, model_config=model_config)
            else:
                print("=== [DEBUG] 發送給 LLM (Native) 的 PROMPT 內容 ===")
                print(prompt)
                print("========================================")
                raw_code, _, _, thinking_text = _call_ai(prompt, model_config=model_config)
            ai_inference_time_sec = time.time() - start_ai
            
            # 🚨 教授的「思維搶救」：如果正文是空的，但思考區有東西，就拿思考區來救災！
            if not raw_code.strip() and thinking_text.strip():
                print("[SYSTEM] 偵測到正文為空，啟動『思維區內容搶救』...")
                raw_code = thinking_text 
            
            # 🚨 關鍵偵錯點 1：印出「絕對原始」的回應
            print("=== [DEBUG] RAW LLM OUTPUT ===")
            print(repr(raw_code))
            print("==============================")
            
            import re

            # [ROOT FIX] Apply Radical Scaffold BEFORE Ab2/Ab3 split
            # This must run before cleaned_text / ab2_code_to_execute are derived.
            if "FourOperationsOfRadicals" in (skill_name or ""):
                from core.prompt_architect import RADICAL_V4_SCAFFOLD_PREFIX, RADICAL_V4_SCAFFOLD_SUFFIX
                _rr = str(raw_code or "")

                # [LOOP BREAKER] 重複迴圈時強制改為預設 Path A，避免崩潰
                if len(_rr) > 1000 and _rr.count('pattern_id') > 5:
                    _style = self._analyze_radical_style(input_text) if 'input_text' in locals() else 'mixed'
                    _decisions = f'    pattern_id = "p1_add_sub"\n    difficulty = "mid"\n    term_count = 2\n    radical_style = "{_style}"\n'
                    raw_code = RADICAL_V4_SCAFFOLD_PREFIX + _decisions + RADICAL_V4_SCAFFOLD_SUFFIX
                    print("[INFO] [LOOP_BREAKER/scaler] Repetition loop detected. Forcing Path A (p1_add_sub).")
                else:
                    # [SMART INTERCEPTOR V4] Alias-aware: 僅當 AI 輸出很短（且沒寫 def generate）時才啟動強制萃取
                    _pid_m = re.search(r'pattern_id\s*=\s*["\']([^"\']+)["\']', _rr)
                    _raw_pid = _pid_m.group(1).strip() if _pid_m else None

                    alias_map = {
                        "p0": "p0_simplify", "p1": "p1_add_sub", "p2a": "p2a_mult_direct",
                        "p2b": "p2b_mult_distrib", "p2c": "p2c_mult_binomial", "p2d": "p2d_perfect_square",
                        "p2e": "p2e_diff_of_squares", "p2f": "p2f_int_mult_rad", "p2g": "p2g_rad_mult_frac",
                        "p2h": "p2h_frac_mult_rad", "p3a": "p3a_div_expr", "p3b": "p3b_div_simple",
                        "p3c": "p3c_div_direct", "p4": "p4_frac_mult", "p4b": "p4b_frac_rad_div",
                        "p4c": "p4c_nested_frac_chain", "p4d": "p4d_frac_rad_div_mixed", "p5a": "p5a_conjugate_int", "p5b": "p5b_conjugate_rad",
                        "p6": "p6_combo", "p7": "p7_mixed_rad_add", "p1b": "p1b_add_sub_bracket", "p1c": "p1c_mixed_frac_rad_add_sub"
                    }
                    if _raw_pid:
                        _raw_pid_clean = _raw_pid.split()[0].replace('±', '').replace('÷', '').strip()
                        _pid = alias_map.get(_raw_pid_clean, _raw_pid_clean)
                    else:
                        _pid = None

                    valid_ids = set(alias_map.values())

                    if _pid in valid_ids and len(_rr.strip()) < 300 and "def generate" not in _rr:
                        _diff_m = re.search(r'difficulty\s*=\s*["\'](easy|mid|hard)["\']', _rr)
                        _tc_m = re.search(r'term_count\s*=\s*(\d+|None)', _rr)
                        _diff = _diff_m.group(1).strip() if _diff_m else "mid"
                        _tc = _tc_m.group(1).strip() if _tc_m else "None"
                        _style = self._analyze_radical_style(input_text) if 'input_text' in locals() else 'mixed'
                        _decisions = f'    pattern_id = "{_pid}"\n    difficulty = "{_diff}"\n    term_count = {_tc}\n    radical_style = "{_style}"\n'
                        raw_code = RADICAL_V4_SCAFFOLD_PREFIX + _decisions + RADICAL_V4_SCAFFOLD_SUFFIX
                        print(f"[INFO] [ROOT_ASSEMBLER/scaler] Valid Pattern Detected (Resolved): {_pid}. Forcing Scaffold.")
                    else:
                        if "df." in _rr and "DomainFunctionHelper" not in _rr:
                            raw_code = "import sympy as sp\nfrom core.domain_functions import DomainFunctionHelper\ndf = DomainFunctionHelper()\n\n" + _rr
                            print("[INFO] [ROOT_ASSEMBLER/scaler] Path B Detected (Complex Logic). Skipping force-extraction.")

            # 2. 處理 <think> 標籤
            if '<think>' in raw_code:
                cleaned_text = re.sub(r'<think>.*?</think>', '', raw_code, flags=re.DOTALL).strip()
            else:
                cleaned_text = raw_code.strip()
                
            # 3. 提取 Markdown 中的 Python 區塊（強化版：避免誤抓到殘缺片段）
            def _score_code_candidate(text):
                src = (text or "").strip()
                score = 0
                if "def generate(" in src:
                    score += 120
                if "def check(" in src:
                    score += 60
                if src.startswith("return "):
                    score -= 140
                if "```" in src:
                    score -= 20
                score += min(len(src), 4000) // 40
                return score

            py_blocks = re.findall(r'```python\s*(.*?)\s*```', cleaned_text, re.DOTALL | re.IGNORECASE)
            generic_blocks = re.findall(r'```\s*(.*?)\s*```', cleaned_text, re.DOTALL)
            candidates = [b.strip() for b in py_blocks if b.strip()]
            candidates.extend([b.strip() for b in generic_blocks if b.strip() and b.strip() not in candidates])

            if candidates:
                final_code_to_healer = max(candidates, key=_score_code_candidate).strip()
            else:
                final_code_to_healer = cleaned_text.strip()

            ab1_code_to_execute = (raw_code or "").strip()
            ab1_code_to_execute = ab1_code_to_execute.replace("\r\n", "\n")
            if ab1_code_to_execute.lower().startswith("```python"):
                ab1_code_to_execute = ab1_code_to_execute[len("```python"):].lstrip("\n")
            elif ab1_code_to_execute.startswith("```"):
                ab1_code_to_execute = ab1_code_to_execute[len("```"):].lstrip("\n")
            if ab1_code_to_execute.endswith("```"):
                ab1_code_to_execute = ab1_code_to_execute[:-3].rstrip()

            ab2_code_to_execute = cleaned_text.strip()
            ab2_code_to_execute = re.sub(r'^\s*```python\s*', '', ab2_code_to_execute, flags=re.IGNORECASE)
            ab2_code_to_execute = re.sub(r'^\s*```\s*', '', ab2_code_to_execute)
            ab2_code_to_execute = re.sub(r'\s*```\s*$', '', ab2_code_to_execute)

            # fallback: 如果抽出的區塊不含 generate，但全文有，則從全文第一個 generate 開始截取
            if "def generate(" not in final_code_to_healer and "def generate(" in cleaned_text:
                gen_idx = cleaned_text.find("def generate(")
                if gen_idx >= 0:
                    final_code_to_healer = cleaned_text[gen_idx:].strip()

            # 清理殘留 markdown fence
            final_code_to_healer = re.sub(r'^\s*```python\s*', '', final_code_to_healer, flags=re.IGNORECASE)
            final_code_to_healer = re.sub(r'^\s*```\s*', '', final_code_to_healer)
            final_code_to_healer = re.sub(r'\s*```\s*$', '', final_code_to_healer)

            # [UNIVERSAL ORCHESTRATOR FIX] Ensure Radical code is assembled before Healer
            if "FourOperationsOfRadicals" in (skill_name or ""):
                from core.prompt_architect import RADICAL_V4_SCAFFOLD_PREFIX, RADICAL_V4_SCAFFOLD_SUFFIX
                raw_code_temp = str(final_code_to_healer or "")

                if len(raw_code_temp) > 1000 and raw_code_temp.count('pattern_id') > 5:
                    _style = self._analyze_radical_style(input_text) if 'input_text' in locals() else 'mixed'
                    decisions = f'    pattern_id = "p0_simplify"\n    difficulty = "easy"\n    term_count = None\n    radical_style = "{_style}"\n'
                    final_code_to_healer = RADICAL_V4_SCAFFOLD_PREFIX + decisions + RADICAL_V4_SCAFFOLD_SUFFIX
                    print("[INFO] [LOOP_BREAKER/scaler] Repetition loop detected. Forcing Path A (p0_simplify).")
                else:
                    # [SMART INTERCEPTOR V4] Alias-aware: 僅當輸出很短且沒寫 def generate 時才強制萃取
                    pid_match = re.search(r'pattern_id\s*=\s*["\']([^"\']+)["\']', raw_code_temp)
                    _raw_pid = pid_match.group(1).strip() if pid_match else None

                    alias_map = {
                        "p0": "p0_simplify", "p1": "p1_add_sub", "p2a": "p2a_mult_direct",
                        "p2b": "p2b_mult_distrib", "p2c": "p2c_mult_binomial", "p2d": "p2d_perfect_square",
                        "p2e": "p2e_diff_of_squares", "p2f": "p2f_int_mult_rad", "p2g": "p2g_rad_mult_frac",
                        "p2h": "p2h_frac_mult_rad", "p3a": "p3a_div_expr", "p3b": "p3b_div_simple",
                        "p3c": "p3c_div_direct", "p4": "p4_frac_mult", "p4b": "p4b_frac_rad_div",
                        "p4c": "p4c_nested_frac_chain", "p4d": "p4d_frac_rad_div_mixed", "p5a": "p5a_conjugate_int", "p5b": "p5b_conjugate_rad",
                        "p6": "p6_combo", "p7": "p7_mixed_rad_add", "p1b": "p1b_add_sub_bracket", "p1c": "p1c_mixed_frac_rad_add_sub"
                    }
                    if _raw_pid:
                        _raw_pid_clean = _raw_pid.split()[0].replace('±', '').replace('÷', '').strip()
                        pid = alias_map.get(_raw_pid_clean, _raw_pid_clean)
                    else:
                        pid = None

                    valid_ids = set(alias_map.values())

                    if pid in valid_ids and len(raw_code_temp.strip()) < 300 and "def generate" not in raw_code_temp:
                        diff_match = re.search(r'difficulty\s*=\s*["\'](easy|mid|hard)["\']', raw_code_temp)
                        tc_match = re.search(r'term_count\s*=\s*(\d+|None)', raw_code_temp)
                        diff = diff_match.group(1).strip() if diff_match else "mid"
                        tc = tc_match.group(1).strip() if tc_match else "None"
                        _style = self._analyze_radical_style(input_text) if 'input_text' in locals() else 'mixed'
                        decisions = f'    pattern_id = "{pid}"\n    difficulty = "{diff}"\n    term_count = {tc}\n    radical_style = "{_style}"\n'
                        final_code_to_healer = RADICAL_V4_SCAFFOLD_PREFIX + decisions + RADICAL_V4_SCAFFOLD_SUFFIX
                        print(f"[INFO] [UNIVERSAL_ASSEMBLER/scaler] Valid Pattern Detected (Resolved): {pid}. Forcing Scaffold.")
                    else:
                        if "df." in raw_code_temp and "DomainFunctionHelper" not in raw_code_temp:
                            final_code_to_healer = "import sympy as sp\nfrom core.domain_functions import DomainFunctionHelper\ndf = DomainFunctionHelper()\n\n" + raw_code_temp
                            print("[INFO] [UNIVERSAL_ASSEMBLER/scaler] Path B Detected (Complex Logic). Skipping force-extraction.")

            # 🚨 關鍵偵錯點 2：檢查送給 Healer 的內容是否為空
            if not ablation_mode:
                print(f"=== [DEBUG] SENDING TO HEALER (Length: {len(final_code_to_healer)}) ===")
                print(final_code_to_healer)
                print("=====================================================================")
                
                if not final_code_to_healer:
                    print("[FATAL ERROR] 傳給 Healer 的字串是空的！API 萃取邏輯有 Bug！")

            # [CIRCUIT BREAKER]
            _final_str = str(final_code_to_healer or "")
            # 檢查是否為系統組裝的 Scaffold (路徑 A VIP 豁免)
            is_scaffold = "df.get_safe_vars_for_pattern" in _final_str

            # 只有在非 Scaffold (即 AI 自行撰寫的路徑 B) 的情況下，才檢查是否瘋狂跳針
            if not is_scaffold and (_final_str.count('pattern_id') > 3 or len(_final_str) > 2000):
                print("[ERROR] [scaler] Circuit Breaker Triggered: Model Repetition Detected in Path B!")
                final_code_to_healer = self._build_emergency_generate_code("計算 $\\sqrt{2} \\times \\sqrt{3}$ 的值。")

            clean_code = final_code_to_healer
            
            if ablation_mode:
                # [完全跳過 Healer] Ab1 實驗精神：只做基礎字串清理，保留 AI 生成的所有原生邏輯錯誤/套件缺失
                final_code = ab1_code_to_execute
                healed_code = ab1_code_to_execute
                regex_fixes = 0
                ast_fixes = 0
                class DummyASTStats:
                    pass
                dummy_stats = DummyASTStats()
                dummy_stats.logs = []
                healer_stats = [dummy_stats]
                print("[WARN] [Ab1 模式] 已繞過 _advanced_healer 與 _inject_domain_libs。")
                ab2_result = None
            else:
                # --- [NEW] Ab2 Interception (Scaffold Prompt, No Healer) ---
                ab2_result = {}
                ab2_save_dir = "generated_scripts"
                if not os.path.exists(ab2_save_dir):
                    os.makedirs(ab2_save_dir, exist_ok=True)
                ab2_filename = f"scaler_{int(time.time())}_{uuid.uuid4().hex[:6]}_ab2.py"
                ab2_file_path = os.path.join(ab2_save_dir, ab2_filename)
                with open(ab2_file_path, "w", encoding="utf-8") as _fb:
                    _fb.write(ab2_code_to_execute)
                
                try:
                    cpu_start_ab2 = time.time()
                    ab2_exe_res = self._execute_code(ab2_code_to_execute, level=1)
                    try:
                        from scripts.evaluate_mcri import evaluate_math_hygiene
                        if "question_text" in ab2_exe_res:
                            h_score, _ = evaluate_math_hygiene(ab2_exe_res["question_text"])
                            ab2_exe_res["_mcri_hygiene_score"] = h_score
                    except:
                        pass
                    ab2_result = ab2_exe_res
                    ab2_result["cpu_execution_time_sec"] = time.time() - cpu_start_ab2
                except Exception as e:
                    ab2_result = {"error": f"執行錯誤: {e}", "cpu_execution_time_sec": time.time() - cpu_start_ab2}
                
                ab2_result["file_path"] = ab2_file_path
                ab2_result["ai_inference_time_sec"] = ai_inference_time_sec
                ab2_result["raw_code"] = ab2_code_to_execute    # scaffold code, markdown-fence stripped only
                
                # [NEW] Prepend api_stubs to Ab2's final code so the UI sees the injected functions
                _api_stubs_prefix = api_stubs if 'api_stubs' in dir() else ""
                ab2_result["final_code"] = _api_stubs_prefix + "\n\n" + ab2_code_to_execute  # no Healer applied for Ab2
                # --- /Ab2 Interception ---
                
                def _ensure_generate_block(code_text, fallback_source):
                    import re
                    code_out = code_text or ""
                    if re.search(r"^\s*def\s+generate\s*\(", code_out, flags=re.MULTILINE):
                        return code_out
                    src = fallback_source or ""
                    m = re.search(r"^\s*def\s+generate\s*\(", src, flags=re.MULTILINE)
                    if m:
                        recovered = src[m.start():].strip()
                        if recovered:
                            if code_out and not code_out.endswith("\n"):
                                code_out += "\n"
                            code_out += "\n\n" + recovered if code_out else recovered
                    return code_out

                # [執行完整 Healer + 函式庫注入]
                healed_code, *healer_stats = _advanced_healer(clean_code, ablation_id=active_ablation_id, skill_id=skill_name)
                # [Bug 16 Fix] If AST healer exited early, bare eval() may remain.
                # Replace before injection so MCRI static analysis sees safe_eval().
                healed_code = re.sub(r'\beval\s*\(', 'safe_eval(', healed_code)
                # [Bug 16 Fix — source] Strip extra args (globals/locals dicts) from
                # safe_eval() calls using AST so expressions with parens are handled safely.
                # The polyfill also accepts *args as a runtime safety net, but this ensures
                # clean code reaches downstream MCRI analysis.
                try:
                    import ast as _ast, astunparse as _astunparse

                    class _StripSafeEvalArgs(_ast.NodeTransformer):
                        def visit_Call(self, node):
                            self.generic_visit(node)
                            if (isinstance(node.func, _ast.Name)
                                    and node.func.id == 'safe_eval'
                                    and len(node.args) > 1):
                                node.args = [node.args[0]]
                                node.keywords = []
                            return node

                    _tree = _ast.parse(healed_code)
                    _tree = _StripSafeEvalArgs().visit(_tree)
                    _ast.fix_missing_locations(_tree)
                    healed_code = astunparse.unparse(_tree).strip()
                except Exception:
                    pass  # AST strip is best-effort; polyfill handles runtime

                # [核心優化]：在代碼中注入可見的修復痕跡
                healed_code = self._inject_healer_tags(healed_code, raw_code, target_ops)
                
                final_code, _ = _inject_domain_libs(healed_code)
                final_code = _ensure_generate_block(final_code, clean_code)
                try:
                    ast.parse(final_code)
                except SyntaxError:
                    final_code, _ = _inject_domain_libs(clean_code)
                    final_code = _ensure_generate_block(final_code, clean_code)
                if (not re.search(r"^\s*def\s+generate\s*\(", final_code, flags=re.MULTILINE)) and re.search(r"^\s*def\s+generate\s*\(", clean_code, flags=re.MULTILINE):
                    final_code = clean_code
                if not re.search(r"^\s*def\s+generate\s*\(", final_code, flags=re.MULTILINE):
                    print("[AB3-SAFETY] final_code missing generate(); switching to emergency template.")
                    final_code = self._build_emergency_generate_code(input_text)
                regex_fixes = healer_stats[0] if len(healer_stats) > 0 else 0
                ast_fixes = healer_stats[1] if len(healer_stats) > 1 else 0
            
            print("\n=== DEBUG: GENERATED CODE ===")
            print(final_code)
            print("=============================\n")
            
            # [修正] 這裡直接使用頂層 os
            save_dir = "generated_scripts"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
                
            unique_filename = f"live_show_{int(time.time())}_{uuid.uuid4().hex[:6]}.py"
            file_path = os.path.join(save_dir, unique_filename)
            
            with open(file_path, "w", encoding="utf-8") as _fb:
                _fb.write(final_code)
            
            # MCRI Report - Code Robustness
            robustness_grade = "UNKNOWN"
            robustness_reason = ""
            try:
                from scripts.evaluate_mcri import analyze_code_robustness, evaluate_math_hygiene
                robustness_grade, robustness_reason = analyze_code_robustness(healed_code)
            except ImportError:
                pass
            
            # 拿到 final_code 後，執行 count 次
            start_cpu = time.time()
            results = []
            for i in range(count):
                try:
                    res = self._execute_code(final_code, level=1) # pass dummy level 1
                    
                    # 計算 MCRI Math Hygiene
                    if "question_text" in res:
                        try:
                            h_score, h_notes = evaluate_math_hygiene(res["question_text"])
                            res["_mcri_hygiene_score"] = h_score
                            res["_mcri_hygiene_notes"] = h_notes
                        except:
                            pass
                            
                    results.append(res)
                except Exception as e:
                    results.append({"error": f"執行第 {i+1} 題時發生錯誤: {e}"})
            cpu_execution_time_sec = time.time() - start_cpu
            
            debug_meta = {
                "prompt": prompt,
                "raw_text": ab1_code_to_execute if ablation_mode else raw_code,
                "raw_code": ab1_code_to_execute if ablation_mode else raw_code,
                "thinking": thinking_text,
                "final_code": final_code,
                "file_path": file_path,
                "architect_model": (model_config or {}).get("model", Config.CODER_PRESETS.get(Config.DEFAULT_CODER_PRESET, {}).get('model', 'qwen3.5:9b')),
                "healer_trace": {
                    "regex_fixes": regex_fixes,
                    "ast_fixes": ast_fixes
                },
                "mcri_report": {
                    "robustness_grade": robustness_grade,
                    "robustness_reason": robustness_reason
                },
                "bare_prompt": prompt if ablation_mode else "",
                "scaffold_prompt": prompt if not ablation_mode else "",
                "architect_raw_spec": "",
                "gemini_raw_spec": "",
                "healer_logs": getattr(healer_stats[2], "logs", []) if len(healer_stats) > 2 and hasattr(healer_stats[2], "logs") else [],
                "performance": {
                    "ai_inference_time_sec": round(ai_inference_time_sec, 2),
                    "cpu_execution_time_sec": round(cpu_execution_time_sec, 4)
                }
            }
            return {
                "problems": results,
                "ab2_result": ab2_result if not ablation_mode else None,
                "debug_meta": debug_meta
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"代碼生成或執行失敗: {e}")

    def _sanitize_input_dna(self, text):
        import re
        
        # 0. 處理 LaTeX 轉義，確保送給 AI 的字串不會因為 Python 解析遇到 \d, \t 而報錯
        text = text.replace(r'\div', r'\\div').replace(r'\times', r'\\times').replace(r'\sqrt', r'\\sqrt')
        
        # 1. 處理平方：將 x^2 轉為 x^{2} (LaTeX 標準)
        text = re.sub(r'(\w)\^(\d+)', r'\1^{\2}', text)
        
        # 2. 偵測數學片段並封裝：
        # 簡單邏輯：如果整段話沒有 $，但看起來像數學題，就試著處理
        if "$" not in text:
            # 這裡我們針對您提供的範例進行特製化處理
            # 尋找從括號開始到括號結束的片段
            text = re.sub(r'(\(.*\).*)', r'$\1$', text)
        
        # 3. [V51.1 防禦] 過濾掉真實換行，避免 LLM 產生帶有真實換行的單引號字串 (導致 SyntaxError)
        text = text.replace('\n', ' ').replace('\r', '')
        
        return text

    def _build_emergency_generate_code(self, source_text):
        raw_text = str(source_text or "計算 1+1 的值。")
        if "【題型同構硬性約束】" in raw_text:
            raw_text = raw_text.split("【題型同構硬性約束】", 1)[0].strip()
        if not raw_text:
            raw_text = "計算 1+1 的值。"
        safe_text = repr(raw_text)
        return f'''def generate(level=1, **kwargs):
    question_text = {safe_text}
    try:
        from core.code_utils.live_show_math_utils import _recompute_correct_answer_from_question
        ans = _recompute_correct_answer_from_question(question_text) or "0"
    except Exception:
        ans = "0"
    if "計算" not in question_text:
        question_text = f"計算 ${{question_text}}$ 的值。"
    return {{
        "question_text": question_text,
        "correct_answer": str(ans),
        "mode": 1
    }}

def check(user_answer, correct_answer):
    ok = str(user_answer).strip() == str(correct_answer).strip()
    return {{"correct": ok, "result": "正確" if ok else "錯誤"}}
'''

    def _inject_healer_tags(self, code, raw_code, ops_name):
        """ 在代碼中標註修復痕跡 """
        annotated_lines = []
        for line in code.split('\n'):
            new_line = line
            # AST Fix標註: 參數處理
            if "def generate(level=1" in line and "def generate():" in raw_code:
                new_line += "  # [AST Fix: 自動補齊必全參數]"
            # AST Fix標註: 防護
            elif "question_text =" in line and "question_text" not in raw_code[:300] and "question_text = " not in raw_code[:300]:
                new_line += "  # [AST Fix: 安全初始化防護]"
            # Regex Fix 標註
            elif f"{ops_name}.format_latex(" in line and ".format(" in raw_code:
                new_line += f"  # [Regex Fix: 修正 {ops_name} API]"
            
            annotated_lines.append(new_line)
        return '\n'.join(annotated_lines)

    def _execute_code(self, code, level):
        """
        動態執行 Python 代碼並獲取結果。
        """
        # [V2.5 Unification] 優先從標準函式庫匯入
        try:
            from core.prompts.domain_function_library import (
                RadicalOps, IntegerOps, FractionOps, PolynomialOps, CalculusOps
            )
        except ImportError:
            # Fallback 到舊有的 Scaffold Libs
            try:
                from core.scaffold.domain_libs import RadicalOps, IntegerOps, FractionOps
            except ImportError:
                RadicalOps = IntegerOps = FractionOps = None
            PolynomialOps = CalculusOps = None
        
        Fraction = importlib.import_module("fractions").Fraction
        
        # [Fallback Polyfill] 為了壓制 AI 發瘋硬要呼叫 safe_eval 的幻覺，並且處理 LaTeX 語法
        # *_ignored_args accepts extra positional args (e.g. globals/locals dict) that
        # Python's built-in eval() takes; generated code may call eval(expr, {...}) with 2 args.
        def _safe_eval_polyfill(expr, *_ignored_args, **_ignored_kwargs):
            try:
                import re
                from fractions import Fraction
                
                class MyFrac:
                    def __init__(self, n): self.n = n
                    def __call__(self, d): return Fraction(self.n, d)

                s = str(expr)
                # 替換常見的全形或人類可讀符號，並清除 LaTeX (如 \left, \right)
                s = s.replace('×', '*').replace('÷', '/').replace('＋', '+').replace('－', '-')
                s = s.replace('\\times', '*').replace('\\div', '/').replace('\\cdot', '*')
                s = s.replace('\\left', '').replace('\\right', '')
                
                # 將 \frac{a}{b} 或 \frac(a)(b) 轉為 Fraction 進行精準有理數計算
                s = s.replace('\\{', '(').replace('\\}', ')').replace('{', '(').replace('}', ')')
                s = s.replace('\\frac', 'MyFrac')
                
                # 放棄危險正則表達式，直接 eval
                # [Fix] 加入 sqrt 與 math 支援，防止緊急代碼執行時報錯
                return eval(s, {"__builtins__": {}}, {"Fraction": Fraction, "abs": abs, "MyFrac": MyFrac, "sqrt": math.sqrt, "math": math})
            except Exception as e:
                raise Exception(f"safe_eval 計算失敗 ({expr}): 轉換後為 '{s}', 錯誤: {e}")

        import sympy as sp
        from core.domain_functions import DomainFunctionHelper
        df_instance = DomainFunctionHelper()

        exec_globals = {
            "random": importlib.import_module("random"),
            "math": importlib.import_module("math"),
            "sp": sp,
            "sympy": sp,
            "Fraction": Fraction,
            "safe_eval": _safe_eval_polyfill,
            "eval": _safe_eval_polyfill,
            "RadicalOps": RadicalOps,
            "DomainFunctionHelper": DomainFunctionHelper,
            "df": df_instance,  # 閉環關鍵：預載實例
            "question_text": "題目生成失敗",
            "correct_answer": "0"
        }
        
        try:
            import tempfile
            
            # 1. 強制寫入硬碟，避開記憶體快取
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                tmp_path = f.name
            
            # 2. 強制重載模組 (Importlib Reload)
            spec = importlib.util.spec_from_file_location("dynamic_module", tmp_path)
            foo = importlib.util.module_from_spec(spec)
            
            # 將防呆變數與函式庫注入至模組的命名空間
            foo.__dict__.update(exec_globals)
            
            # 強制從硬碟執行載入
            spec.loader.exec_module(foo)
            
            gen_func = getattr(foo, "generate", None)
            if not gen_func:
                raise Exception("生成的代碼中找不到 generate 函式")
                
            # [動態參數檢查]
            import inspect
            sig = inspect.signature(gen_func)
            
            # 如果 AI 產出的函式不吃參數，我們就直接呼叫
            if not sig.parameters:
                result = gen_func()
            else:
                result = gen_func(level=level)
                
            # [Patch] Post-process question_text to fix common AI LaTeX hallucinations (e.g., sqrt(x) -> \sqrt{x})
            if isinstance(result, dict) and "question_text" in result:
                q = result["question_text"]
                if "sqrt(" in q:
                    import re
                    # Replace 'sqrt(inner)' with '\sqrt{inner}'
                    q = re.sub(r'sqrt\s*\(([^)]+)\)', r'\\sqrt{\1}', q)
                    result["question_text"] = q

            return result
        except Exception as e:
            print(f"[ERROR] 執行生成的程式碼時出錯: {e}")
            raise e

    def generate_batch(self, skill_name, input_text, n=100, batch_size=5, ablation_mode=False):
        """
        新增批量模式 (直接用 Python 迴圈高速產出 100 題)
        """
        print(f"[INFO] 正在為 {skill_name} 生產 {n} 題 (單次 AI 呼叫 + Python 高速迴圈)...")
        # 直接呼叫一次 custom_problems，要求他回傳 n 題，這也是在本地 Python 環境中跑 n 次 generate()
        batches = self.generate_custom_problems(skill_name, input_text, count=n, model_id=Config.DEFAULT_CODER_PRESET, ablation_mode=ablation_mode)
        return batches

if __name__ == "__main__":
    # 簡單測試
    scaler = AdaptiveScaler()
    skill = "jh_數學2上_FourArithmeticOperationsOfPolynomial"
    for lv in [1, 2, 3]:
        print(f"\n--- 測試難度 {lv} ---")
        try:
            res = scaler.generate_problem(skill, level=lv)
            print(f"Q: {res.get('question_text')}")
            print(f"A: {res.get('correct_answer')}")
        except Exception as e:
            print(f"錯誤: {e}")
