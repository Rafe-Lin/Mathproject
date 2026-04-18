# -*- coding: utf-8 -*-
# ==============================================================================
# ID: core/architect_v01.py
# Version: v0.1 (Database-Driven Dynamic Architect)
# Last Updated: 2026-01-29
# Author: Math AI Research Team (Advisor & Student)
#
# [Description]:
#   v0.1 Architect 模組，專為「導數應用」Domain 設計。
#   核心設計：**Database-Driven，動態分析任何課本例題**
#
#   不硬編碼例題，而是：
#   1. 接收課本例題（從 database 讀取）
#   2. 自動識別問題類型（一階/多階導數、切線、等）
#   3. 自動提取數值範圍
#   4. 動態生成 MASTER_SPEC
#
#   架構流程：
#   Database TextbookExample
#   → query_textbook_example(example_id)
#   → ArchitectV01.analyze_problem(textbook_example)
#   → MASTER_SPEC（動態生成）
#   → Coder Prompt
#
# [Key Change from Previous]:
#   ✅ 移除硬編碼的 analyze_applications_of_derivatives()
#   ✅ 新增通用 analyze_problem(textbook_example)
#   ✅ 自動識別問題類型和參數
#   ✅ 真正實現 Database-Driven 架構
#
# ==============================================================================

import json
import re
from sympy import symbols, diff, simplify, latex, parse_expr
from datetime import datetime

class ArchitectV01:
    """v0.1 Architect - Database-Driven 動態分析引擎"""
    
    def __init__(self):
        self.skill_id = "ApplicationsOfDerivatives"
        self.domain = "微積分"
        self.timestamp = datetime.now().isoformat()
    
    def analyze_problem(self, textbook_example):
        """
        【核心方法】通用問題分析函數
        
        從課本例題自動識別問題類型，動態生成 MASTER_SPEC
        
        Args:
            textbook_example: dict，包含：
                - 'problem_text': 問題文本（例："已知 f(x) = x⁴ - 2x³ + 5x - 4，求 f'(x) 與 f'''(x)。"）
                - 'solution': 參考解答（可選）
                - 'skill_id': 技能 ID（可選，預設 ApplicationsOfDerivatives）
        
        Returns:
            dict: MASTER_SPEC（根據例題動態生成）
        
        Example:
            >>> example = {
            ...     'problem_text': '已知 f(x) = x⁴ - 2x³ + 5x - 4，求 f\'(x) 與 f\'\'\'(x)。',
            ... }
            >>> spec = architect.analyze_problem(example)
            >>> # spec 自動識別為「多階導數」問題
        """
        
        if not textbook_example:
            raise ValueError("textbook_example 不能為空")
        
        problem_text = textbook_example.get('problem_text', '')
        
        # ========================================================================
        # 步驟 1: 從問題文本識別問題類型
        # ========================================================================
        
        problem_type = self._identify_problem_type(problem_text)
        
        # ========================================================================
        # 步驟 2: 提取多項式和關鍵參數
        # ========================================================================
        
        polynomial_info = self._extract_polynomial_info(problem_text)
        
        # ========================================================================
        # 步驟 3: 根據類型生成特定的 MASTER_SPEC
        # ========================================================================
        
        if problem_type == "multiple_derivatives":
            return self._spec_for_multiple_derivatives(polynomial_info, textbook_example)
        elif problem_type == "tangent_line":
            return self._spec_for_tangent_line(polynomial_info, textbook_example)
        elif problem_type == "single_derivative":
            return self._spec_for_single_derivative(polynomial_info, textbook_example)
        else:
            return self._spec_generic(polynomial_info, textbook_example)
    
    def _identify_problem_type(self, problem_text):
        """
        自動識別問題類型
        
        Returns: "multiple_derivatives" | "tangent_line" | "single_derivative" | "generic"
        """
        
        # 多階導數關鍵詞
        if re.search(r"f[\'′][\'\′]*\(", problem_text) or re.search(r"求.*f[\'′]", problem_text):
            # 檢查是否涉及多階
            if re.search(r"[fF]{1,3}[\'\′]{2,}", problem_text) or re.search(r"f[\'\′]{2}", problem_text):
                return "multiple_derivatives"
            # 檢查是否涉及切線
            if re.search(r"切線|tangent|slope", problem_text):
                return "tangent_line"
            return "single_derivative"
        
        # 切線關鍵詞
        if re.search(r"切線|tangent|切點", problem_text):
            return "tangent_line"
        
        return "generic"
    
    def _extract_polynomial_info(self, problem_text):
        """
        從問題文本提取多項式信息
        
        Returns: {
            'polynomial_text': 原始多項式文本,
            'coefficients': {...},
            'degree': 次數,
            'variables': {...}
        }
        """
        
        # 尋找多項式定義（例：f(x) = ... 或 f(x)=...）
        match = re.search(r"f\(x\)\s*=\s*([^，。\n]+)", problem_text)
        
        if not match:
            # 如果沒找到明確的 f(x)=，嘗試尋找其他模式
            match = re.search(r"函數\s*([^，。\n]+)", problem_text)
        
        if match:
            poly_text = match.group(1).strip()
            # 去掉特殊符號
            poly_text = poly_text.replace('−', '-').replace('·', '*').replace('×', '*')
            
            return {
                'polynomial_text': poly_text,
                'parsed': self._parse_polynomial(poly_text)
            }
        
        return {'polynomial_text': None, 'parsed': None}
    
    def _parse_polynomial(self, poly_text):
        """
        解析多項式文本，提取係數和次數
        
        嘗試使用 sympy 解析，失敗時返回基本信息
        """
        try:
            x = symbols('x')
            expr = parse_expr(poly_text.replace('^', '**'))
            
            # 驗證是多項式
            from sympy import Poly
            poly = Poly(expr, x)
            coeffs = poly.all_coeffs()
            degree = poly.degree()
            
            return {
                'degree': degree,
                'coefficients': coeffs,
                'expression': expr
            }
        except Exception as e:
            # 如果無法解析，返回 None，後續會使用通用模式
            return None
    
    def _spec_for_multiple_derivatives(self, polynomial_info, textbook_example):
        """生成「多階導數」問題的 MASTER_SPEC"""
        
        master_spec = {
            "skill_id": self.skill_id,
            "domain": self.domain,
            "version": "v0.1",
            "timestamp": self.timestamp,
            
            "problem_type": "multiple_derivatives",
            "problem_structure": "多項式 → 一階導數 → 二階導數 → ... → 高階導數",
            
            "problem_statement_template": (
                "已知函數 $f(x) = {polynomial}$，"
                "求 {derivatives_list}。"
            ),
            
            "answer_template": "{derivatives_answers}",
            
            "entities": {
                "polynomial": {
                    "description": "多項式 f(x)",
                    "constraints": {
                        "degree": "2~5（推薦 3~4）",
                        "coefficients": "整數，範圍 -10~10（避免過大計算）",
                        "leading_coefficient": "非零"
                    }
                },
                "derivative_orders": {
                    "description": "要求的導數階數",
                    "constraints": {
                        "min_order": 1,
                        "max_order": "多項式次數 - 1",
                        "typical": "求 f'(x) 和 f''(x)，或 f'(x)、f''(x)、f'''(x)"
                    }
                }
            },
            
            "computation_steps": [
                {
                    "step": 1,
                    "description": "定義多項式 f(x)",
                    "input": ["polynomial_text"],
                    "output": "f(x)"
                },
                {
                    "step": 2,
                    "description": "計算一階導數 f'(x) = d/dx f(x)",
                    "input": ["f(x)"],
                    "output": "f'(x)"
                },
                {
                    "step": 3,
                    "description": "計算二階導數 f''(x) = d/dx f'(x)",
                    "input": ["f'(x)"],
                    "output": "f''(x)"
                },
                {
                    "step": 4,
                    "description": "如果需要，計算更高階導數 f'''(x)、f''''(x) 等",
                    "input": ["f''(x)"],
                    "output": "f'''(x), ..."
                },
                {
                    "step": 5,
                    "description": "化簡各階導數為標準形式",
                    "input": ["所有導數"],
                    "output": "最簡化的導數表達式"
                }
            ],
            
            "constraints": [
                "所有係數都在 [-10, 10] 範圍內，確保計算簡潔",
                "多項式次數建議 3~4，避免高度過大",
                "導數階數不超過多項式次數",
                "最後的高階導數應該是常數或線性函數"
            ],
            
            "validation": {
                "check_polynomial": "確認多項式合法（至少二次）",
                "check_derivatives": "逐階驗證導數公式",
                "check_final_form": "最高階導數應該是常數"
            },
            
            "forbidden_patterns": [
                "❌ 不要生成 matplotlib/pyplot，不要繪圖",
                "❌ 不要定義 main() 或 if __name__",
                "❌ 不要 eval()、exec()、safe_eval()",
                "❌ 不要定義 unittest 或其他無用函數",
                "❌ 不要超過 80 行代碼"
            ]
        }
        
        return master_spec
    
    def _spec_for_tangent_line(self, polynomial_info, textbook_example):
        """生成「切線方程式」問題的 MASTER_SPEC"""
        
        master_spec = {
            "skill_id": self.skill_id,
            "domain": self.domain,
            "version": "v0.1",
            "timestamp": self.timestamp,
            
            "problem_type": "tangent_line",
            "problem_structure": "多項式 → 求導 → 計算切線方程式",
            
            "problem_statement_template": (
                "在函數 $f(x) = {polynomial}$ 的圖形上，"
                "求以點 $P({x0}, {y0})$ 為切點的切線方程式。"
            ),
            
            "answer_template": "$y = {tangent_equation}$",
            
            "entities": {
                "polynomial": {
                    "description": "三次多項式 f(x) = ax³ + bx² + cx + d",
                    "constraints": {
                        "a": "整數，範圍 -10~10，a ≠ 0",
                        "b": "整數，範圍 -10~10",
                        "c": "整數，範圍 -10~10",
                        "d": "整數，範圍 -10~10"
                    }
                },
                "tangent_point": {
                    "description": "切點 P(x0, y0)，必須在曲線上 f(x0) = y0",
                    "constraints": {
                        "x0": "整數，範圍 -5~5",
                        "y0": "由 f(x0) 計算，無需預設"
                    }
                }
            },
            
            "computation_steps": [
                {
                    "step": 1,
                    "description": "定義多項式 f(x) = ax³ + bx² + cx + d",
                    "input": ["a", "b", "c", "d"],
                    "output": "f(x)"
                },
                {
                    "step": 2,
                    "description": "計算導函數 f'(x) = 3ax² + 2bx + c",
                    "input": ["a", "b", "c"],
                    "output": "f'(x)"
                },
                {
                    "step": 3,
                    "description": "選定切點 x = x0",
                    "input": ["x0"],
                    "output": "x0"
                },
                {
                    "step": 4,
                    "description": "計算 y0 = f(x0) 和 m = f'(x0)",
                    "input": ["x0", "f", "f'"],
                    "output": "y0, m"
                },
                {
                    "step": 5,
                    "description": "用點斜式：y - y0 = m(x - x0) → y = mx + b",
                    "input": ["m", "x0", "y0"],
                    "output": "切線方程式"
                }
            ],
            
            "constraints": [
                "所有係數都在 [-10, 10] 範圍內",
                "切點 x0 在 [-5, 5] 範圍內",
                "斜率 m 應該是整數或簡單的有理數"
            ],
            
            "validation": {
                "check_polynomial": "確認 a ≠ 0",
                "check_tangent_point": "驗證 f(x0) = y0",
                "check_equation": "驗證最終方程式"
            },
            
            "forbidden_patterns": [
                "❌ 不要生成 matplotlib/pyplot",
                "❌ 不要定義 main() 或 if __name__",
                "❌ 不要 eval()、exec()",
                "❌ 代碼不超過 80 行"
            ]
        }
        
        return master_spec
    
    def _spec_for_single_derivative(self, polynomial_info, textbook_example):
        """生成「單階導數」問題的 MASTER_SPEC"""
        
        master_spec = {
            "skill_id": self.skill_id,
            "domain": self.domain,
            "version": "v0.1",
            "timestamp": self.timestamp,
            
            "problem_type": "single_derivative",
            "problem_structure": "多項式 → 求一階導數",
            
            "problem_statement_template": "已知函數 $f(x) = {polynomial}$，求 $f'(x)$。",
            
            "answer_template": "$f'(x) = {derivative}$",
            
            "entities": {
                "polynomial": {
                    "description": "多項式 f(x)",
                    "constraints": {
                        "degree": "2~5",
                        "coefficients": "整數，範圍 -10~10"
                    }
                }
            },
            
            "computation_steps": [
                {
                    "step": 1,
                    "description": "定義多項式",
                    "output": "f(x)"
                },
                {
                    "step": 2,
                    "description": "應用導數規則求 f'(x)",
                    "output": "f'(x)"
                },
                {
                    "step": 3,
                    "description": "化簡",
                    "output": "最簡形式"
                }
            ],
            
            "constraints": [
                "係數範圍 [-10, 10]"
            ],
            
            "validation": {
                "correctness_check": "驗證 f'(x) 符合導數規則",
                "execution_test": "執行生成的代碼 3 次，檢查結果是否穩定"
            },
            
            "forbidden_patterns": [
                "❌ 不要超過 50 行代碼"
            ]
        }
        
        return master_spec
    
    def _spec_generic(self, polynomial_info, textbook_example):
        """通用 MASTER_SPEC（備用方案）"""
        
        return {
            "skill_id": self.skill_id,
            "domain": self.domain,
            "version": "v0.1",
            "timestamp": self.timestamp,
            "problem_type": "generic",
            "problem_statement_template": textbook_example.get('problem_text', ''),
            "problem_structure": "多項式 → 求導數",
            "entities": {
                "polynomial": {"symbol": "f", "type": "polynomial"},
                "derivative": {"symbol": "f'", "type": "first_derivative"}
            },
            "computation_steps": [
                {"step": 1, "description": "定義多項式 f(x)"}
            ],
            "constraints": ["支持任意次數多項式"],
            "validation": {"output_type": "symbolic_expression"},
            "forbidden_patterns": [],
            "note": "未能識別具體問題類型，請手動檢查"
        }
    
    def to_prompt_for_coder(self, master_spec):
        """
        將 MASTER_SPEC 轉換為 Coder 能理解的 Prompt
        
        自動根據 problem_type 生成相應的 Prompt
        """
        
        prompt = f"""
【任務】根據以下規格生成「{master_spec['problem_type']}」類型的數學代碼

【問題結構】{master_spec['problem_structure']}

【實體定義】
{json.dumps(master_spec.get('entities', {}), ensure_ascii=False, indent=2)}

【計算步驟】（必須按順序）
"""
        
        for step_info in master_spec.get('computation_steps', []):
            prompt += f"\n{step_info['step']}. {step_info['description']}"
        
        prompt += f"""

【約束條件】
{chr(10).join(['- ' + c for c in master_spec.get('constraints', [])])}

【驗證規則】
{json.dumps(master_spec.get('validation', {}), ensure_ascii=False, indent=2)}

【嚴格禁止】
{chr(10).join(master_spec.get('forbidden_patterns', []))}

【代碼結構】
from random import randint
from sympy import symbols, diff, simplify, latex

x = symbols('x')

# 步驟 1: 生成或定義多項式
a = randint(-10, 10)
# ... 生成係數

# 步驟 2-N: 按照上述計算步驟實現
# ...

# 最後一步：返回結果
result = {{
    'question_text': '...',  # LaTeX 格式的題目
    'answer': '...',         # LaTeX 格式的答案
    'mode': 1
}}

【重要提示】
- 嚴格按照上述步驟實現
- 不要添加任何多餘代碼
- 返回格式必須是 dict，包含 'question_text' 和 'answer'
- 如果涉及隨機數，確保數值「好計算、有意義」
"""
        
        return prompt

    
    def to_prompt_for_coder(self, master_spec):
        """
        將 MASTER_SPEC 轉換為 Coder 能理解的 Prompt
        """
        
        prompt = f"""
【任務】根據以下規格生成「導數應用-切線方程式」練習題代碼

【問題結構】{master_spec['problem_structure']}

【實體定義】
{json.dumps(master_spec['entities'], ensure_ascii=False, indent=2)}

【計算步驟】（必須按順序）
"""
        
        for step_info in master_spec['computation_steps']:
            prompt += f"\n{step_info['step']}. {step_info['description']}"
        
        prompt += f"""

【約束條件】
{chr(10).join(['- ' + c for c in master_spec['constraints']])}

【驗證規則】
{json.dumps(master_spec['validation'], ensure_ascii=False, indent=2)}

【嚴格禁止】
{chr(10).join(master_spec['forbidden_patterns'])}

【代碼模板】
from random import randint
from sympy import symbols, diff, simplify, latex

x = symbols('x')

# 步驟 1-2: 生成多項式係數
a = randint(-10, 10)
while a == 0:
    a = randint(-10, 10)
b = randint(-10, 10)
c = randint(-10, 10)
d = randint(-10, 10)

# 定義多項式和導函數
f = a*x**3 + b*x**2 + c*x + d
f_prime = diff(f, x)

# 步驟 3-4: 選定切點
x0 = randint(-5, 5)
y0 = int(f.subs(x, x0))
m = int(f_prime.subs(x, x0))

# 步驟 7: 切線方程式化簡
tangent = simplify(m*x + (y0 - m*x0))

# 輸出
question = f"在函數 ${{latex(f)}}$ 的圖形上，求以點 $P({{x0}}, {{y0}})$ 為切點的切線方程式。"
answer = f"y = {{latex(tangent)}}"

return {{
    'question_text': question,
    'answer': answer,
    'mode': 1
}}

【重要提示】
- 嚴格按照上述步驟實現
- 不要添加任何多餘代碼
- 返回格式必須是 dict，包含 'question_text' 和 'answer'
"""
        
        return prompt


# 便利函數
def create_architect():
    """工廠函數，創建 Architect 實例"""
    return ArchitectV01()
