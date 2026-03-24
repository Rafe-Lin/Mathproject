class RadicalOps:
    """根號運算模組 - 化簡與精確計算"""

    @staticmethod
    def create(inner):
        """建立根號 sqrt(inner) 並自動化簡 (例: 12 -> "2√3")"""
        ...

    @staticmethod
    def is_perfect_square(n):
        """檢查 n 是否為完全平方數"""
        ...

    @staticmethod
    def to_latex(expr):
        ...

    @staticmethod
    def add_term(terms_dict, coeff, radicand):
        """化簡並將單項根式加入到字典中"""
        ...

    @staticmethod
    def mul_terms(c1, r1, c2, r2):
        """兩個單項根式相乘，返回化簡結果 (new_coeff, new_radicand)"""
        ...

    @staticmethod
    def div_terms(c1, r1, c2, r2):
        """兩個單項根式相除 c1√r1 ÷ c2√r2，返回化簡與有理化結果 (new_coeff, new_radicand)"""
        ...

    @staticmethod
    def get_prime_factors(n):
        """質因數分解 (例: 12 -> {2:2, 3:1})"""
        ...

    @staticmethod
    def simplify_term(coeff, radicand):
        """化簡單項根式 c√r -> (new_c, new_r)"""
        ...

    @staticmethod
    def simplify(coeff, radicand):
        """別名：等同 simplify_term；單項化簡 c√r → (new_c, new_r)。"""
        ...

    @staticmethod
    def format_term(coeff, radicand, is_first=True):
        """格式化單項根式 (LaTeX)
- 自動化簡: √12 -> 2√3
- 支援 Fraction 係數: Fraction(2,9) -> \\frac{2}{9}
- 處理正負號: first term 不顯示 + 號，負數顯示 -"""
        ...

    @staticmethod
    def format_term_unsimplified(coeff, radicand, is_first=True, wrap_negative_non_leading=False, is_leading=None):
        """不化簡被開方數；is_leading 與 is_first 同義。"""
        ...

    @staticmethod
    def format_expression(terms_dict, denominator=1):
        """格式化多項根式表達式 (terms_dict: {radicand: coeff})
- 自動化簡合併同類項
- 支援 Fraction 係數（自動通分轉為整數係數 + denominator）
- 支援 denominator 參數直接傳入分母（推薦用法：避免 Fraction 係數）
- 按 radicand 升序；首項負號緊貼，後續「 + 」「 - 」"""
        ...

    @staticmethod
    def add_dicts(terms1, terms2):
        """合併兩個同類項字典 {radicand: coeff}"""
        ...

    @staticmethod
    def multiply_dicts(terms1, terms2):
        """展開兩個多項根式的乘積，並自動化簡同類項"""
        ...

    @staticmethod
    def simplify_root(radicand):
        """[防護方法] 化簡 sqrt(radicand)，等同 simplify_term(1, radicand)，返回 (coeff, simplified_radicand)"""
        ...

class FractionOps:
    """分數運算模組 - 精確處理分數與浮點數混合運算"""

    @staticmethod
    def create(value):
        """建立分數，具備「型別智慧」
- 如果輸入是 float，先轉 str 再轉 Fraction（避免浮點精度誤差）
- 支援 str 輸入（如 "-0.6"）
- 支援 Fraction、int、float 輸入

範例：
    FractionOps.create(-0.6)    → Fraction(-3, 5)
    FractionOps.create("-0.6")  → Fraction(-3, 5)
    FractionOps.create(3)       → Fraction(3, 1)"""
        ...

    @staticmethod
    def to_latex(val, mixed=False):
        '''輸出 LaTeX 格式
- 分母為 1 時，只顯示整數
- mixed=True 時顯示帶分數（如 -1 1/2）

範例：
    FractionOps.to_latex(Fraction(3, 2))        → "\\frac{3}{2}"
    FractionOps.to_latex(Fraction(3, 2), True)  → "1\\frac{1}{2}"
    FractionOps.to_latex(Fraction(5, 1))        → "5"'''
        ...

    @staticmethod
    def add(a, b):
        """分數加法"""
        ...

    @staticmethod
    def sub(a, b):
        """分數減法"""
        ...

    @staticmethod
    def mul(a, b):
        """分數乘法"""
        ...

    @staticmethod
    def div(a, b):
        """分數除法（注意：b 不能為零）"""
        ...

import random

_EXPR_TEMPLATE = '(-__N0__)\\times__N1__\\sqrt{__N2__}'
_RANGES = [(1, 4), (2, 5), (4, 7)]
_PROMPT_WORD = '化簡'

def _render_expr():
    expr = _EXPR_TEMPLATE
    for i, (lo, hi) in enumerate(_RANGES):
        val = random.randint(lo, hi)
        expr = expr.replace(f'__N{i}__', str(val))
    return expr

def generate(level=1, **kwargs):
    expr = _render_expr()
    return {'question_text': _PROMPT_WORD + ' $' + expr + '$。', 'correct_answer': '', 'mode': 1}

def check(user_answer, correct_answer):
    try:
        if str(user_answer).strip() == str(correct_answer).strip():
            return {'correct': True, 'result': '正確'}
        if abs(float(user_answer) - float(correct_answer)) < 1e-6:
            return {'correct': True, 'result': '正確'}
    except Exception:
        pass
    return {'correct': False, 'result': '錯誤'}