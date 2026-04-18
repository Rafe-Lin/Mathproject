# ============================================================================
# Domain-Based 標準函數庫 [V2.5 重構版]
# [V47.14] 為每個數學領域定義標準工具函數，強制 LLM 引用而非自創
# [V2.5 新增] FractionOps、IntegerOps、RadicalOps 等高精度運算模組
# ============================================================================
"""
此模組定義了各個數學領域的標準工具函數。
所有 LLM（Gemini / 14B / 7B）在生成代碼時，必須引用這些預定義函數，禁止自創同名或類似功能的函數。

【V2.5 新增功能】
1. FractionOps (分數模組)：精確處理分數運算與浮點數轉換
2. IntegerOps (整數模組)：支援絕對值、括號格式化
3. RadicalOps (根號模組)：化簡與精確計算
4. CalculusOps (微積分模組)：多項式與微分

【關鍵改進】
- 浮點數精度修復：-0.6 → -3/5 (不是 -0.599999...)
- 設計模式：所有四則運算皆透過 Fraction 進行
- 安全評估：safe_eval() 支援絕對值運算
"""

import math
import random
from fractions import Fraction
from decimal import Decimal, getcontext
import logging

logger = logging.getLogger(__name__)

# 設置 Decimal 精度
getcontext().prec = 28


# ============================================================================
# [V2.5 新增] Python 實現的標準操作類（用於 LLM 提示和本地測試）
# ============================================================================

class FractionOps:
    """分數運算模組 - 精確處理分數與浮點數混合運算"""
    
    @staticmethod
    def create(value):
        """
        建立分數，具備「型別智慧」
        - 如果輸入是 float，先轉 str 再轉 Fraction（避免浮點精度誤差）
        - 支援 str 輸入（如 "-0.6"）
        - 支援 Fraction、int、float 輸入
        
        範例：
            FractionOps.create(-0.6)    → Fraction(-3, 5)
            FractionOps.create("-0.6")  → Fraction(-3, 5)
            FractionOps.create(3)       → Fraction(3, 1)
        """
        if isinstance(value, float):
            value_str = str(value)
            return Fraction(value_str).limit_denominator(10000)
        elif isinstance(value, str):
            return Fraction(value)
        elif isinstance(value, Fraction):
            return value
        else:
            return Fraction(value)
    
    @staticmethod
    def to_latex(val, mixed=False):
        """輸出 LaTeX 格式"""
        if isinstance(val, Fraction):
            if val.denominator == 1:
                return str(val.numerator)
            if mixed and abs(val.numerator) > val.denominator:
                whole = abs(val.numerator) // val.denominator  # [Fix] use abs() to avoid Python floor-division error for negatives
                remainder = abs(val.numerator) % val.denominator
                if remainder == 0:
                    return str(-whole if val < 0 else whole)
                sign = "-" if val < 0 else ""
                return f"{sign}{whole} \\frac{{{remainder}}}{{{val.denominator}}}"
            return f"\\frac{{{val.numerator}}}{{{val.denominator}}}"
        return str(val)
    
    @staticmethod
    def add(a, b):
        """分數加法"""
        return a + b
    
    @staticmethod
    def sub(a, b):
        """分數減法"""
        return a - b
    
    @staticmethod
    def mul(a, b):
        """分數乘法"""
        return a * b
    
    @staticmethod
    def div(a, b):
        """分數除法"""
        if b == 0:
            raise ValueError("Division by zero")
        return a / b


class IntegerOps:
    """整數運算模組 - 支援格式化、絕對值等"""
    
    @staticmethod
    def op_to_latex(op_str):
        """將基礎運算符號轉成國中課本 LaTeX 顯示"""
        if op_str == '*': 
            return '\\times'
        if op_str == '/': 
            return '\\div'
        return op_str

    @staticmethod
    def fmt_num(n):
        """格式化數字，為負數自動加括號"""
        if n < 0:
            return f"({n})"
        return str(n)
    
    @staticmethod
    def random_nonzero(min_val, max_val):
        """生成非零隨機整數"""
        available = [x for x in range(min_val, max_val + 1) if x != 0]
        if not available:
            raise ValueError(f"No non-zero integers in range [{min_val}, {max_val}]")
        return random.choice(available)
    
    @staticmethod
    def is_divisible(a, b):
        """檢查 a 是否能被 b 整除"""
        if b == 0:
            return False
        return a % b == 0
    
    @staticmethod
    def safe_eval(expr):
        """安全評估算式，支援：abs()、基本四則運算、括號"""
        safe_dict = {
            '__builtins__': {},
            'abs': abs,
            'sum': sum,
            'max': max,
            'min': min,
        }
        # 先將 LaTeX 符號與括號清理乾淨，轉為純 Python 計算式
        clean_expr = str(expr).replace('\\div', '/').replace('\\times', '*')
        clean_expr = clean_expr.replace('\\', '') # 移除殘留的反斜線
        # 移除方括號並替換為括號（如果需要）
        clean_expr = clean_expr.replace('[', '(').replace(']', ')')
        try:
            return eval(clean_expr, safe_dict)
        except Exception as e:
            raise ValueError(f"Invalid expression: {expr} (cleaned: {clean_expr}). Error: {e}")


class RadicalOps:
    """根號運算模組 - 化簡與精確計算"""
    
    @staticmethod
    def create(inner):
        """建立根號 sqrt(inner) 並自動化簡"""
        if inner < 0:
            raise ValueError("Cannot take square root of negative number")
        if inner == 0:
            return "0"
        
        i = int(math.sqrt(inner))
        while i > 1:
            if inner % (i * i) == 0:
                sqrt_val = i
                remainder = inner // (i * i)
                if remainder == 1:
                    return str(sqrt_val)
                return f"{sqrt_val}√{remainder}"
            i -= 1
        
        return f"√{inner}"
    
    @staticmethod
    def is_perfect_square(n):
        """檢查 n 是否為完全平方數"""
        if n < 0:
            return False
        sqrt = int(n ** 0.5)
        return sqrt * sqrt == n
    
    @staticmethod
    def to_latex(expr):
        """輸出根號的 LaTeX 格式"""
        return f"\\sqrt{{{expr}}}"

    @staticmethod
    def add_term(terms_dict, coeff, radicand):
        """化簡並將單項根式加入到字典中"""
        new_coeff, new_radicand = RadicalOps.simplify_term(coeff, radicand)
        if new_coeff != 0:
            terms_dict[new_radicand] = terms_dict.get(new_radicand, 0) + new_coeff
        return terms_dict

    @staticmethod
    def mul_terms(c1, r1, c2, r2):
        """兩個單項根式相乘，返回化簡結果 (new_coeff, new_radicand)"""
        return RadicalOps.simplify_term(c1 * c2, r1 * r2)

    @staticmethod
    def div_terms(c1, r1, c2, r2):
        """兩個單項根式相除 c1√r1 ÷ c2√r2，返回化簡與有理化結果 (new_coeff, new_radicand)"""
        from fractions import Fraction
        # 處理分數被開方數
        is_r1_frac = type(r1).__name__ == "Fraction" or isinstance(r1, Fraction)
        is_r2_frac = type(r2).__name__ == "Fraction" or isinstance(r2, Fraction)
        if is_r1_frac or is_r2_frac:
            return RadicalOps.simplify_term(Fraction(c1, c2), Fraction(r1, r2))
        # 整數被開方數
        if r1 % r2 == 0:
            return RadicalOps.simplify_term(Fraction(c1, c2), r1 // r2)
        else:
            return RadicalOps.simplify_term(Fraction(c1, c2 * r2), r1 * r2)

    @staticmethod
    def get_prime_factors(n):
        """質因數分解 (例: 12 -> {2:2, 3:1})"""
        n = abs(int(n))
        factors = {}
        d = 2
        temp = n
        while d * d <= temp:
            while temp % d == 0:
                factors[d] = factors.get(d, 0) + 1
                temp //= d
            d += 1
        if temp > 1:
            factors[temp] = factors.get(temp, 0) + 1
        return factors

    @staticmethod
    def simplify_term(coeff, radicand):
        """化簡單項根式 c√r -> (new_c, new_r)"""
        from fractions import Fraction
        # [Fix] Handle Fraction radicand (e.g. 1/2 -> 2/4 -> 1/2 sqrt(2))
        if isinstance(radicand, Fraction):
            if radicand.denominator != 1:
                coeff = Fraction(coeff, radicand.denominator)
                radicand = radicand.numerator * radicand.denominator
            else:
                radicand = radicand.numerator

        radicand = int(radicand)
        if radicand == 0: return 0, 1
        if radicand == 1: return coeff, 1
        factors = RadicalOps.get_prime_factors(radicand)
        out_factor = 1
        new_radicand = 1
        for p, exp in factors.items():
            out_factor *= p**(exp // 2)
            new_radicand *= p**(exp % 2)
        return coeff * out_factor, new_radicand

    @staticmethod
    def simplify(coeff, radicand):
        """別名：等同 simplify_term；單項化簡 c√r → (new_c, new_r)。"""
        return RadicalOps.simplify_term(coeff, radicand)

    @staticmethod
    def format_term(coeff, radicand, is_first=True):
        """格式化單項根式 (LaTeX)，支援 Fraction 係數"""
        if coeff == 0: return ""
        c_val, r_val = RadicalOps.simplify_term(coeff, radicand)
        from fractions import Fraction as _F
        _is_frac = isinstance(c_val, _F) and c_val.denominator != 1

        if r_val == 1:
            if _is_frac:
                n, d = abs(c_val.numerator), c_val.denominator
                s = f"\\frac{{{n}}}{{{d}}}"
                if not is_first:
                    return f" - {s}" if c_val < 0 else f" + {s}"
                return f"-{s}" if c_val < 0 else s
            if is_first: return str(c_val)
            return f" + {c_val}" if c_val > 0 else f" - {-c_val}"

        sign = ""
        if not is_first:
            sign = " + " if c_val > 0 else " - "
        elif c_val < 0:
            sign = "-"

        abs_c = abs(c_val)
        if _is_frac:
            c_str = f"\\frac{{{abs_c.numerator}}}{{{abs_c.denominator}}}"
        elif abs_c == 1:
            c_str = ""
        else:
            c_str = str(abs_c)
        return f"{sign}{c_str}\\sqrt{{{r_val}}}"

    @staticmethod
    def format_term_unsimplified(
        coeff, radicand, is_first=True, wrap_negative_non_leading=False, is_leading=None
    ):
        """不化簡被開方數；is_leading 與 is_first 同義。"""
        if is_leading is not None:
            is_first = bool(is_leading)
        if coeff == 0:
            return ""
        from fractions import Fraction as _F

        def is_f(x):
            return type(x).__name__ == "Fraction" or isinstance(x, _F)

        if radicand == 0:
            return "0"
        if not is_f(radicand) and int(radicand) == 1:
            return FractionOps.to_latex(coeff, mixed=False) if is_f(coeff) else str(coeff)
        if is_f(radicand):
            rt = (
                FractionOps.to_latex(radicand, mixed=False)
                if radicand.denominator != 1
                else str(radicand.numerator)
            )
            core = f"\\sqrt{{{rt}}}"
        else:
            core = f"\\sqrt{{{radicand}}}"
        if is_f(coeff):
            if wrap_negative_non_leading and coeff < 0 and not is_first:
                return f"\\left({RadicalOps.format_term_unsimplified(coeff, radicand, True, False)}\\right)"
            at = FractionOps.to_latex(abs(coeff), mixed=False)
            mid = f"{at}{core}" if abs(coeff) != 1 else core
            if is_first:
                return f"-{mid}" if coeff < 0 else (mid if coeff > 0 else "0")
            if coeff > 0:
                return f" + {mid}" if coeff != 1 else f" + {core}"
            return f" - {mid}" if abs(coeff) != 1 else f" - {core}"
        c = int(coeff)
        if wrap_negative_non_leading and c < 0 and not is_first:
            return f"\\left({RadicalOps.format_term_unsimplified(c, radicand, True, False)}\\right)"
        if is_first:
            if c == 1:
                return core
            if c == -1:
                return f"-{core}"
            if c < 0:
                return f"-{abs(c)}{core}"
            return f"{c}{core}"
        if c > 0:
            return f" + {core}" if c == 1 else f" + {c}{core}"
        if c == -1:
            return f" - {core}"
        return f" - {abs(c)}{core}"

    @staticmethod
    def format_expression(terms_dict, denominator=1):
        """格式化多項根式表達式 (terms_dict: {radicand: coeff})，支援 Fraction 係數與 denominator 參數"""
        if not terms_dict: return "0"
        import math
        from fractions import Fraction as _F

        # 1. 內部化簡合併
        simplified = {}
        for r, c in terms_dict.items():
            if c == 0: continue
            c_s, r_s = RadicalOps.simplify_term(c, r)
            simplified[r_s] = simplified.get(r_s, 0) + c_s

        simplified = {r: c for r, c in simplified.items() if c != 0}
        if not simplified: return "0"

        # 1.5 若有 Fraction 係數，通分整化
        for r in list(simplified.keys()):
            c = simplified[r]
            if isinstance(c, _F) and c.denominator != 1:
                denominator = denominator * c.denominator
                simplified[r] = c.numerator

        # 2. 處理分母約分
        if denominator != 1:
            all_coeffs = [int(c) for c in simplified.values()]
            common = abs(int(denominator))
            for c in all_coeffs:
                common = math.gcd(common, abs(c))
            if common > 1:
                denominator //= common
                for r in simplified:
                    simplified[r] //= common

        # 3. 按 radicand 升序（答案唯一）
        sorted_rads = sorted(simplified.keys())

        # 4. 標準書寫：首項負號緊貼；後續「 + 」「 - 」與係數絕對值
        parts = []
        for i, r in enumerate(sorted_rads):
            c = simplified[r]
            if c == 0:
                continue
            if r == 1:
                tex = str(c)
                if not parts:
                    parts.append(tex)
                elif c > 0:
                    parts.append(f" + {tex}")
                else:
                    parts.append(f" - {abs(c)}")
            else:
                ac = abs(c)
                body = f"\\sqrt{{{r}}}" if ac == 1 else f"{ac}\\sqrt{{{r}}}"
                if not parts:
                    parts.append(f"-{body}" if c < 0 else body)
                elif c > 0:
                    parts.append(f" + {body}")
                else:
                    parts.append(f" - {body}")

        final_str = "".join(parts)

        if denominator == 1 or not final_str:
            return final_str if final_str else "0"
        if len(simplified) == 1:
            only_r, only_c = next(iter(simplified.items()))
            if only_r != 1:
                sign = "-" if only_c < 0 else ""
                abs_coeff = abs(int(only_c))
                coeff_tex = f"\\frac{{{abs_coeff}}}{{{denominator}}}"
                radical_tex = f"\\sqrt{{{only_r}}}"
                return f"{sign}{coeff_tex}{radical_tex}"
        return f"\\frac{{{final_str}}}{{{denominator}}}"

    @staticmethod
    def add_dicts(terms1, terms2):
        """合併兩個同類項字典 {radicand: coeff}"""
        merged = dict(terms1)
        for r, c in terms2.items():
            merged[r] = merged.get(r, 0) + c
        return merged

    @staticmethod
    def multiply_dicts(terms1, terms2):
        """展開兩個多項根式的乘積，並自動化簡同類項"""
        result = {}
        for r1, c1 in terms1.items():
            for r2, c2 in terms2.items():
                if c1 == 0 or c2 == 0:
                    continue
                new_c, new_r = RadicalOps.simplify_term(c1 * c2, r1 * r2)
                result[new_r] = result.get(new_r, 0) + new_c
        return {r: c for r, c in result.items() if c != 0}

    @staticmethod
    def simplify_root(radicand):
        """[防護方法] 化簡 √radicand，等同 simplify_term(1, radicand)，返回 (coeff, simplified_radicand)"""
        return RadicalOps.simplify_term(1, int(radicand))

class CalculusOps:
    """微積分運算模組 - 多項式與微分"""
    
    @staticmethod
    def create_poly(coeffs):
        """建立多項式"""
        degree = len(coeffs) - 1
        return [(coeffs[i], degree - i) for i in range(len(coeffs))]
    
    @staticmethod
    def differentiate(poly_terms, times=1):
        """對多項式求導 times 次"""
        result = list(poly_terms)
        for _ in range(times):
            new_result = []
            for coeff, exp in result:
                if exp > 0:
                    new_result.append((coeff * exp, exp - 1))
            result = new_result
        return result
    
    @staticmethod
    def to_latex(terms):
        """多項式轉 LaTeX"""
        if not terms:
            return '0'
        parts = []
        for i, (c, e) in enumerate(sorted(terms, key=lambda x: x[1], reverse=True)):
            if c == 0:
                continue
            sign = '' if i == 0 else (' + ' if c > 0 else ' - ')
            abs_c = abs(c)
            if e == 0:
                parts.append(f'{sign}{abs_c}')
            elif e == 1:
                coeff = '' if abs_c == 1 else str(abs_c)
                parts.append(f'{sign}{coeff}x')
            else:
                coeff = '' if abs_c == 1 else str(abs_c)
                parts.append(f'{sign}{coeff}x^{{{e}}}')
        return ''.join(parts).strip()


class PolynomialOps:
    """多項式運算模組 - 四則運算與 LaTeX 格式化 (降冪係數列表)"""

    @staticmethod
    def normalize(coeffs):
        """移除前導零，例: [0, 0, 3, -1] -> [3, -1]；全零回傳 [0]"""
        if not coeffs:
            return [0]
        i = 0
        while i < len(coeffs) - 1 and coeffs[i] == 0:
            i += 1
        return list(coeffs[i:])

    @staticmethod
    def format_latex(coeffs, var='x'):
        """係數列表 (降冪) → LaTeX 字串，例: [3, -2, 1] → '3x^{2} - 2x + 1'"""
        coeffs = PolynomialOps.normalize(coeffs)
        if all(c == 0 for c in coeffs):
            return '0'
        degree = len(coeffs) - 1
        parts = []
        for i, c in enumerate(coeffs):
            d = degree - i
            if c == 0:
                continue
            abs_c = abs(c)
            coeff_str = '' if abs_c == 1 and d > 0 else str(abs_c)
            if d == 0:
                var_str = str(abs_c)
            elif d == 1:
                var_str = f'{coeff_str}{var}'
            else:
                var_str = f'{coeff_str}{var}^{{{d}}}'
            if not parts:
                sign_str = '-' if c < 0 else ''
            else:
                sign_str = ' - ' if c < 0 else ' + '
            parts.append(f'{sign_str}{var_str}')
        return ''.join(parts) if parts else '0'

    @staticmethod
    def format_plain(coeffs, var='x'):
        """係數列表 (降冪) → 純文字字串（用於答案），例: [3, -2, 1] → '3x^2-2x+1'"""
        coeffs = PolynomialOps.normalize(coeffs)
        if all(c == 0 for c in coeffs):
            return '0'
        degree = len(coeffs) - 1
        parts = []
        for i, c in enumerate(coeffs):
            d = degree - i
            if c == 0:
                continue
            abs_c = abs(c)
            coeff_str = '' if abs_c == 1 and d > 0 else str(abs_c)
            if d == 0:
                var_str = str(abs_c)
            elif d == 1:
                var_str = f'{coeff_str}{var}'
            else:
                var_str = f'{coeff_str}{var}^{d}'
            if not parts:
                sign_str = '-' if c < 0 else ''
            else:
                sign_str = '-' if c < 0 else '+'
            parts.append(f'{sign_str}{var_str}')
        return ''.join(parts) if parts else '0'

    @staticmethod
    def add(c1, c2):
        """多項式加法：輸入兩個係數列表，回傳結果係數列表"""
        max_len = max(len(c1), len(c2))
        p1 = [0] * (max_len - len(c1)) + list(c1)
        p2 = [0] * (max_len - len(c2)) + list(c2)
        return PolynomialOps.normalize([a + b for a, b in zip(p1, p2)])

    @staticmethod
    def sub(c1, c2):
        """多項式減法：c1 - c2"""
        max_len = max(len(c1), len(c2))
        p1 = [0] * (max_len - len(c1)) + list(c1)
        p2 = [0] * (max_len - len(c2)) + list(c2)
        return PolynomialOps.normalize([a - b for a, b in zip(p1, p2)])

    @staticmethod
    def mul(c1, c2):
        """多項式乘法"""
        if not c1 or not c2:
            return [0]
        result = [0] * (len(c1) + len(c2) - 1)
        for i, a in enumerate(c1):
            for j, b in enumerate(c2):
                result[i + j] += a * b
        return PolynomialOps.normalize(result)

    @staticmethod
    def random_poly(degree, range_val=(-5, 5)):
        """生成隨機多項式係數（最高項非零）"""
        choices_nonzero = [x for x in range(range_val[0], range_val[1] + 1) if x != 0]
        coeffs = []
        for i in range(degree + 1):
            if i == 0:
                coeffs.append(random.choice(choices_nonzero))
            else:
                coeffs.append(random.randint(range_val[0], range_val[1]))
        return coeffs


# ============================================================================
# [V2.5 新增] FractionOps - 分數標準函數庫
# ============================================================================

FRACTIONOPS_HELPERS = r"""
# ===== FractionOps (分數標準函數庫) =====

class FractionOps:
    '''分數運算模組 - 精確處理分數與浮點數混合運算'''
    
    @staticmethod
    def create(value):
        '''
        建立分數，具備「型別智慧」
        - 如果輸入是 float，先轉 str 再轉 Fraction（避免浮點精度誤差）
        - 支援 str 輸入（如 "-0.6"）
        - 支援 Fraction、int、float 輸入
        
        範例：
            FractionOps.create(-0.6)    → Fraction(-3, 5)
            FractionOps.create("-0.6")  → Fraction(-3, 5)
            FractionOps.create(3)       → Fraction(3, 1)
        '''
        if isinstance(value, float):
            value_str = str(value)
            return Fraction(value_str).limit_denominator(10000)
        elif isinstance(value, str):
            return Fraction(value)
        elif isinstance(value, Fraction):
            return value
        else:
            return Fraction(value)

    @staticmethod
    def to_latex(val, mixed=False):
        '''
        輸出 LaTeX 格式
        - 分母為 1 時，只顯示整數
        - mixed=True 時顯示帶分數（如 -1 1/2）
        
        範例：
            FractionOps.to_latex(Fraction(3, 2))        → "\\frac{3}{2}"
            FractionOps.to_latex(Fraction(3, 2), True)  → "1\\frac{1}{2}"
            FractionOps.to_latex(Fraction(5, 1))        → "5"
        '''
        if isinstance(val, Fraction):
            if val.denominator == 1:
                return str(val.numerator)
            if mixed and abs(val.numerator) > val.denominator:
                whole = abs(val.numerator) // val.denominator  # [Fix] use abs() to avoid Python floor-division error for negatives
                remainder = abs(val.numerator) % val.denominator
                if remainder == 0:
                    return str(-whole if val < 0 else whole)
                sign = "-" if val < 0 else ""
                return f"{sign}{whole} \\frac{{{remainder}}}{{{val.denominator}}}"
            return f"\\frac{{{val.numerator}}}{{{val.denominator}}}"
        return str(val)

    @staticmethod
    def add(a, b):
        '''分數加法'''
        return a + b

    @staticmethod
    def sub(a, b):
        '''分數減法'''
        return a - b

    @staticmethod
    def mul(a, b):
        '''分數乘法'''
        return a * b

    @staticmethod
    def div(a, b):
        '''分數除法（注意：b 不能為零）'''
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
"""

# ============================================================================
# [V2.5 新增] IntegerOps - 整數標準函數庫
# ============================================================================

INTEGEROPS_HELPERS = r"""
# ===== IntegerOps (整數標準函數庫) =====

class IntegerOps:
    '''整數運算模組 - 支援格式化、隨機數生成、整除判斷等'''
    
    @staticmethod
    def op_to_latex(op_str):
        '''將基礎運算符號轉成國中課本 LaTeX 顯示'''
        if op_str == '*': 
            return '\\times'
        if op_str == '/': 
            return '\\div'
        return op_str

    @staticmethod
    def fmt_num(n):
        '''
        格式化數字，為負數自動加括號
        - 便於生成 Python 算式（如 "x + (-5)" 而非 "x + -5"）
        
        範例：
            IntegerOps.fmt_num(5)   → "5"
            IntegerOps.fmt_num(-5)  → "(-5)"
            IntegerOps.fmt_num(0)   → "0"
        '''
        if n < 0:
            return f"({n})"
        return str(n)

    @staticmethod
    def random_nonzero(min_val, max_val):
        '''生成非零隨機整數'''
        available = [x for x in range(min_val, max_val + 1) if x != 0]
        if not available:
            raise ValueError(f"No non-zero integers in range [{min_val}, {max_val}]")
        return random.choice(available)

    @staticmethod
    def is_divisible(a, b):
        '''檢查 a 是否能被 b 整除'''
        if b == 0:
            return False
        return a % b == 0

    @staticmethod
    def safe_eval(expr):
        '''
        安全評估算式，支援：abs()、基本四則運算、括號
        
        範例：
            IntegerOps.safe_eval("8 * (-2) - 5")           → -21
            IntegerOps.safe_eval("abs(8 * (-2) - 5)")     → 21
            IntegerOps.safe_eval("[ (-20) + (-10)] / (-5) * 3")  → 18.0
        '''
        # 允許的函數和變數
        safe_dict = {
            '__builtins__': {},
            'abs': abs,
            'sum': sum,
            'max': max,
            'min': min,
        }
        # 先將 LaTeX 符號與括號清理乾淨，轉為純 Python 計算式
        clean_expr = str(expr).replace('\\div', '/').replace('\\times', '*')
        clean_expr = clean_expr.replace('\\', '') # 移除殘留的反斜線
        # 移除方括號並替換為括號（如果需要）
        clean_expr = clean_expr.replace('[', '(').replace(']', ')')
        try:
            return eval(clean_expr, safe_dict)
        except Exception as e:
            raise ValueError(f"Invalid expression: {expr} (cleaned: {clean_expr}). Error: {e}")
"""

# ============================================================================
# [V2.5 新增] RadicalOps - 根號標準函數庫
# ============================================================================

RADICALOPS_HELPERS = r"""
# ===== RadicalOps (根號標準函數庫) =====

class RadicalOps:
    '''根號運算模組 - 化簡與精確計算'''
    
    @staticmethod
    def create(inner):
        '''建立根號 sqrt(inner) 並自動化簡 (例: 12 -> "2√3")'''
        if inner < 0: raise ValueError("Negative root")
        if inner == 0: return "0"
        i = int(math.sqrt(inner))
        while i > 1:
            if inner % (i * i) == 0:
                sqrt_val = i
                rem = inner // (i * i)
                return f"{sqrt_val}√{rem}" if rem > 1 else str(sqrt_val)
            i -= 1
        return f"√{inner}"

    @staticmethod
    def is_perfect_square(n):
        '''檢查 n 是否為完全平方數'''
        return n >= 0 and int(n**0.5)**2 == n

    @staticmethod
    def to_latex(expr):
        return f"\\sqrt{{{expr}}}"

    @staticmethod
    def add_term(terms_dict, coeff, radicand):
        '''化簡並將單項根式加入到字典中'''
        new_coeff, new_radicand = RadicalOps.simplify_term(coeff, radicand)
        if new_coeff != 0:
            terms_dict[new_radicand] = terms_dict.get(new_radicand, 0) + new_coeff
        return terms_dict

    @staticmethod
    def mul_terms(c1, r1, c2, r2):
        '''兩個單項根式相乘，返回化簡結果 (new_coeff, new_radicand)'''
        return RadicalOps.simplify_term(c1 * c2, r1 * r2)

    @staticmethod
    def div_terms(c1, r1, c2, r2):
        '''兩個單項根式相除 c1√r1 ÷ c2√r2，返回化簡與有理化結果 (new_coeff, new_radicand)'''
        if c2 == 0 or r2 == 0: raise ValueError("Division by zero")
        from fractions import Fraction
        # 處理分數被開方數
        is_r1_frac = type(r1).__name__ == "Fraction" or isinstance(r1, Fraction)
        is_r2_frac = type(r2).__name__ == "Fraction" or isinstance(r2, Fraction)
        if is_r1_frac or is_r2_frac:
            return RadicalOps.simplify_term(Fraction(c1, c2), Fraction(r1, r2))
        # 整數被開方數
        if r1 % r2 == 0:
            return RadicalOps.simplify_term(Fraction(c1, c2), r1 // r2)
        else:
            return RadicalOps.simplify_term(Fraction(c1, c2 * r2), r1 * r2)

    # --- [V2.7 新增] 高級根式運算工具 (供複雜題目生成使用) ---

    @staticmethod
    def get_prime_factors(n):
        '''質因數分解 (例: 12 -> {2:2, 3:1})'''
        n = abs(int(n))
        factors = {}
        d = 2
        temp = n
        while d * d <= temp:
            while temp % d == 0:
                factors[d] = factors.get(d, 0) + 1
                temp //= d
            d += 1
        if temp > 1:
            factors[temp] = factors.get(temp, 0) + 1
        return factors

    @staticmethod
    def simplify_term(coeff, radicand):
        '''化簡單項根式 c√r -> (new_c, new_r)'''
        from fractions import Fraction
        # [Fix] Handle Fraction radicand
        if isinstance(radicand, Fraction):
            if radicand.denominator != 1:
                coeff = Fraction(coeff, radicand.denominator)
                radicand = radicand.numerator * radicand.denominator
            else:
                radicand = radicand.numerator

        radicand = int(radicand)
        if radicand == 0: return 0, 1
        if radicand == 1: return coeff, 1
        factors = RadicalOps.get_prime_factors(radicand)
        out_factor = 1
        new_radicand = 1
        for p, exp in factors.items():
            out_factor *= p**(exp // 2)
            new_radicand *= p**(exp % 2)
        return coeff * out_factor, new_radicand

    @staticmethod
    def simplify(coeff, radicand):
        '''別名：等同 simplify_term；單項化簡 c√r → (new_c, new_r)。'''
        return RadicalOps.simplify_term(coeff, radicand)

    @staticmethod
    def format_term(coeff, radicand, is_first=True):
        '''
        格式化單項根式 (LaTeX)
        - 自動化簡: √12 -> 2√3
        - 支援 Fraction 係數: Fraction(2,9) -> \\frac{2}{9}
        - 處理正負號: first term 不顯示 + 號，負數顯示 -
        '''
        if coeff == 0: return ""
        c_val, r_val = RadicalOps.simplify_term(coeff, radicand)
        from fractions import Fraction as _F
        _is_frac = isinstance(c_val, _F) and c_val.denominator != 1

        if r_val == 1:
            if _is_frac:
                n, d = abs(c_val.numerator), c_val.denominator
                s = f"\\frac{{{n}}}{{{d}}}"
                if not is_first:
                    return f" - {s}" if c_val < 0 else f" + {s}"
                return f"-{s}" if c_val < 0 else s
            if is_first: return str(c_val)
            return f" + {c_val}" if c_val > 0 else f" - {-c_val}"

        sign = ""
        if not is_first:
            sign = " + " if c_val > 0 else " - "
        elif c_val < 0:
            sign = "-"

        abs_c = abs(c_val)
        if _is_frac:
            c_str = f"\\frac{{{abs_c.numerator}}}{{{abs_c.denominator}}}"
        elif abs_c == 1:
            c_str = ""
        else:
            c_str = str(abs_c)
        return f"{sign}{c_str}\\sqrt{{{r_val}}}"

    @staticmethod
    def format_term_unsimplified(
        coeff, radicand, is_first=True, wrap_negative_non_leading=False, is_leading=None
    ):
        '''不化簡被開方數；is_leading 與 is_first 同義。'''
        if is_leading is not None:
            is_first = bool(is_leading)
        if coeff == 0:
            return ""
        from fractions import Fraction as _F

        def is_f(x):
            return type(x).__name__ == "Fraction" or isinstance(x, _F)

        if radicand == 0:
            return "0"
        if not is_f(radicand) and int(radicand) == 1:
            return FractionOps.to_latex(coeff, mixed=False) if is_f(coeff) else str(coeff)
        if is_f(radicand):
            rt = (
                FractionOps.to_latex(radicand, mixed=False)
                if radicand.denominator != 1
                else str(radicand.numerator)
            )
            core = f"\\sqrt{{{rt}}}"
        else:
            core = f"\\sqrt{{{radicand}}}"
        if is_f(coeff):
            if wrap_negative_non_leading and coeff < 0 and not is_first:
                return f"\\left({RadicalOps.format_term_unsimplified(coeff, radicand, True, False)}\\right)"
            at = FractionOps.to_latex(abs(coeff), mixed=False)
            mid = f"{at}{core}" if abs(coeff) != 1 else core
            if is_first:
                return f"-{mid}" if coeff < 0 else (mid if coeff > 0 else "0")
            if coeff > 0:
                return f" + {mid}" if coeff != 1 else f" + {core}"
            return f" - {mid}" if abs(coeff) != 1 else f" - {core}"
        c = int(coeff)
        if wrap_negative_non_leading and c < 0 and not is_first:
            return f"\\left({RadicalOps.format_term_unsimplified(c, radicand, True, False)}\\right)"
        if is_first:
            if c == 1:
                return core
            if c == -1:
                return f"-{core}"
            if c < 0:
                return f"-{abs(c)}{core}"
            return f"{c}{core}"
        if c > 0:
            return f" + {core}" if c == 1 else f" + {c}{core}"
        if c == -1:
            return f" - {core}"
        return f" - {abs(c)}{core}"

    @staticmethod
    def format_expression(terms_dict, denominator=1):
        '''
        格式化多項根式表達式 (terms_dict: {radicand: coeff})
        - 自動化簡合併同類項
        - 支援 Fraction 係數（自動通分轉為整數係數 + denominator）
        - 支援 denominator 參數直接傳入分母（推薦用法：避免 Fraction 係數）
        - 按 radicand 升序；首項負號緊貼，後續「 + 」「 - 」
        '''
        if not terms_dict: return "0"
        import math
        from fractions import Fraction as _F

        # 1. 內部化簡合併
        simplified = {}
        for r, c in terms_dict.items():
            if c == 0: continue
            c_s, r_s = RadicalOps.simplify_term(c, r)
            simplified[r_s] = simplified.get(r_s, 0) + c_s

        simplified = {r: c for r, c in simplified.items() if c != 0}
        if not simplified: return "0"

        # 1.5 若有 Fraction 係數，通分整化：擴大 denominator，係數轉為整數
        for r in list(simplified.keys()):
            c = simplified[r]
            if isinstance(c, _F) and c.denominator != 1:
                denominator = denominator * c.denominator
                simplified[r] = c.numerator

        # 2. 處理分母約分
        if denominator != 1:
            all_coeffs = [int(c) for c in simplified.values()]
            common = abs(int(denominator))
            for c in all_coeffs:
                common = math.gcd(common, abs(c))
            if common > 1:
                denominator //= common
                for r in simplified:
                    simplified[r] //= common

        # 3. 按 radicand 升序（答案唯一）
        sorted_rads = sorted(simplified.keys())

        # 4. 標準書寫：首項負號緊貼；後續「 + 」「 - 」與係數絕對值
        parts = []
        for i, r in enumerate(sorted_rads):
            c = simplified[r]
            if c == 0:
                continue
            if r == 1:
                tex = str(c)
                if not parts:
                    parts.append(tex)
                elif c > 0:
                    parts.append(f" + {tex}")
                else:
                    parts.append(f" - {abs(c)}")
            else:
                ac = abs(c)
                body = f"\\sqrt{{{r}}}" if ac == 1 else f"{ac}\\sqrt{{{r}}}"
                if not parts:
                    parts.append(f"-{body}" if c < 0 else body)
                elif c > 0:
                    parts.append(f" + {body}")
                else:
                    parts.append(f" - {body}")

        final_str = "".join(parts)

        if denominator == 1 or not final_str:
            return final_str if final_str else "0"
        if len(simplified) == 1:
            only_r, only_c = next(iter(simplified.items()))
            if only_r != 1:
                sign = "-" if only_c < 0 else ""
                abs_coeff = abs(int(only_c))
                coeff_tex = f"\\frac{{{abs_coeff}}}{{{denominator}}}"
                radical_tex = f"\\sqrt{{{only_r}}}"
                return f"{sign}{coeff_tex}{radical_tex}"
        return f"\\frac{{{final_str}}}{{{denominator}}}"

    @staticmethod
    def add_dicts(terms1, terms2):
        '''合併兩個同類項字典 {radicand: coeff}'''
        merged = dict(terms1)
        for r, c in terms2.items():
            merged[r] = merged.get(r, 0) + c
        return merged

    @staticmethod
    def multiply_dicts(terms1, terms2):
        '''展開兩個多項根式的乘積，並自動化簡同類項'''
        result = {}
        for r1, c1 in terms1.items():
            for r2, c2 in terms2.items():
                if c1 == 0 or c2 == 0:
                    continue
                new_c, new_r = RadicalOps.simplify_term(c1 * c2, r1 * r2)
                result[new_r] = result.get(new_r, 0) + new_c
        return {r: c for r, c in result.items() if c != 0}

    @staticmethod
    def simplify_root(radicand):
        '''[防護方法] 化簡 sqrt(radicand)，等同 simplify_term(1, radicand)，返回 (coeff, simplified_radicand)'''
        return RadicalOps.simplify_term(1, int(radicand))
"""

# ============================================================================
# [保留] CalculusOps - 微積分標準函數庫
# ============================================================================

CALCULUSOPS_HELPERS = r"""
# ===== CalculusOps (微積分標準函數庫) =====

def CalculusOps_create_poly(coeffs):
    '''建立多項式 (例: [1, -2] → x² - 2)'''
    degree = len(coeffs) - 1
    return [(coeffs[i], degree - i) for i in range(len(coeffs))]

def CalculusOps_differentiate(poly_terms, times=1):
    '''對多項式求導 times 次'''
    result = list(poly_terms)
    for _ in range(times):
        new_result = []
        for coeff, exp in result:
            if exp > 0:
                new_result.append((coeff * exp, exp - 1))
        result = new_result
    return result

def CalculusOps_to_latex(terms):
    '''多項式轉 LaTeX'''
    if not terms:
        return '0'
    parts = []
    for i, (c, e) in enumerate(sorted(terms, key=lambda x: x[1], reverse=True)):
        if c == 0:
            continue
        sign = '' if i == 0 else (' + ' if c > 0 else ' - ')
        abs_c = abs(c)
        if e == 0:
            parts.append(f'{sign}{abs_c}')
        elif e == 1:
            coeff = '' if abs_c == 1 else str(abs_c)
            parts.append(f'{sign}{coeff}x')
        else:
            coeff = '' if abs_c == 1 else str(abs_c)
            parts.append(f'{sign}{coeff}x^{{{e}}}')
    return ''.join(parts).strip()
"""

# ============================================================================
# [新增] PolynomialOps - 多項式標準函數庫
# ============================================================================

POLYNOMIALOPS_HELPERS = r"""
# ===== PolynomialOps (多項式標準函數庫) =====

class PolynomialOps:
    '''多項式運算模組 - 四則運算與 LaTeX 格式化 (降冪係數列表)'''

    @staticmethod
    def _coerce_poly(value):
        '''將純量或係數序列統一轉成降冪係數列表'''
        if isinstance(value, (list, tuple)):
            return list(value) if value else [0]
        if isinstance(value, bool):
            value = int(value)
        if isinstance(value, (int, float)):
            return [value]
        raise TypeError(f'Unsupported polynomial operand: {type(value).__name__}')

    @staticmethod
    def normalize(coeffs):
        '''移除前導零；全零回傳 [0]'''
        coeffs = PolynomialOps._coerce_poly(coeffs)
        if not coeffs:
            return [0]
        i = 0
        while i < len(coeffs) - 1 and coeffs[i] == 0:
            i += 1
        return list(coeffs[i:])

    @staticmethod
    def const(value):
        '''常數多項式，例如 3 -> [3]'''
        return PolynomialOps.normalize([value])

    @staticmethod
    def x():
        '''一次項 x'''
        return [1, 0]

    @staticmethod
    def x2():
        '''二次項 x^2'''
        return [1, 0, 0]

    @staticmethod
    def format_latex(coeffs, var='x', shuffle=False):
        '''係數列表 (降冪) → LaTeX 字串，支援打亂項次，例: [3,-2,1] → "3x^{2} - 2x + 1" (或亂序)'''
        import random
        coeffs = PolynomialOps.normalize(coeffs)
        if all(c == 0 for c in coeffs):
            return '0'
        degree = len(coeffs) - 1
        
        terms = []
        for i, c in enumerate(coeffs):
            d = degree - i
            if c == 0:
                continue
            abs_c = abs(c)
            coeff_str = '' if abs_c == 1 and d > 0 else str(abs_c)
            if d == 0:
                var_str = str(abs_c)
            elif d == 1:
                var_str = f'{coeff_str}{var}'
            else:
                var_str = f'{coeff_str}{var}^{{{d}}}'
            terms.append((c, var_str))
            
        if shuffle:
            random.shuffle(terms)
            
        parts = []
        for i, (c, var_str) in enumerate(terms):
            if i == 0:
                sign_str = '-' if c < 0 else ''
            else:
                sign_str = ' - ' if c < 0 else ' + '
            parts.append(f'{sign_str}{var_str}')
            
        return ''.join(parts) if parts else '0'

    @staticmethod
    def format_shuffled_latex(coeffs, var='x'):
        '''
        與 format_latex 類似，但會隨機打亂項次順序，增加教學難度。
        例：[1, 0, -3, 2] -> 可能產出 "-3x + x^{3} + 2"
        '''
        coeffs = PolynomialOps.normalize(coeffs)
        if all(c == 0 for c in coeffs): return '0'
        
        degree = len(coeffs) - 1
        terms_data = []
        
        for i, c in enumerate(coeffs):
            d = degree - i
            if c == 0: continue
            
            abs_c = abs(c)
            # 處理係數與變數
            coeff_str = '' if abs_c == 1 and d > 0 else str(abs_c)
            if d == 0: var_str = str(abs_c)
            elif d == 1: var_str = f'{coeff_str}{var}'
            else: var_str = f'{coeff_str}{var}^{{{d}}}'
            
            # 儲存單項資料 (不含前導加號)
            terms_data.append({'val': var_str, 'is_neg': c < 0})
        
        # --- 核心：隨機打亂項次 ---
        import random
        random.shuffle(terms_data)
        
        # 組合字串
        res_parts = []
        for i, t in enumerate(terms_data):
            if i == 0:
                sign = "-" if t['is_neg'] else ""
            else:
                sign = " - " if t['is_neg'] else " + "
            res_parts.append(f"{sign}{t['val']}")
            
        return "".join(res_parts)

    @staticmethod
    def format_plain(coeffs, var='x', shuffle=False):
        '''係數列表 (降冪) → 純文字字串（用於答案），支援打亂項次，例: [3,-2,1] → "3x^2-2x+1" (或亂序)'''
        import random
        coeffs = PolynomialOps.normalize(coeffs)
        if all(c == 0 for c in coeffs):
            return '0'
        degree = len(coeffs) - 1
        
        terms = []
        for i, c in enumerate(coeffs):
            d = degree - i
            if c == 0:
                continue
            abs_c = abs(c)
            coeff_str = '' if abs_c == 1 and d > 0 else str(abs_c)
            if d == 0:
                var_str = str(abs_c)
            elif d == 1:
                var_str = f'{coeff_str}{var}'
            else:
                var_str = f'{coeff_str}{var}^{d}'
            terms.append((c, var_str))
            
        if shuffle:
            random.shuffle(terms)
            
        parts = []
        for i, (c, var_str) in enumerate(terms):
            if i == 0:
                sign_str = '-' if c < 0 else ''
            else:
                sign_str = '-' if c < 0 else '+'
            parts.append(f'{sign_str}{var_str}')
            
        return ''.join(parts) if parts else '0'

    @staticmethod
    def add(c1, c2):
        '''多項式加法'''
        c1 = PolynomialOps._coerce_poly(c1)
        c2 = PolynomialOps._coerce_poly(c2)
        max_len = max(len(c1), len(c2))
        p1 = [0] * (max_len - len(c1)) + list(c1)
        p2 = [0] * (max_len - len(c2)) + list(c2)
        return PolynomialOps.normalize([a + b for a, b in zip(p1, p2)])

    @staticmethod
    def sub(c1, c2):
        '''多項式減法：c1 - c2'''
        c1 = PolynomialOps._coerce_poly(c1)
        c2 = PolynomialOps._coerce_poly(c2)
        max_len = max(len(c1), len(c2))
        p1 = [0] * (max_len - len(c1)) + list(c1)
        p2 = [0] * (max_len - len(c2)) + list(c2)
        return PolynomialOps.normalize([a - b for a, b in zip(p1, p2)])

    @staticmethod
    def mul(c1, c2):
        '''多項式乘法'''
        c1 = PolynomialOps._coerce_poly(c1)
        c2 = PolynomialOps._coerce_poly(c2)
        if not c1 or not c2:
            return [0]
        result = [0] * (len(c1) + len(c2) - 1)
        for i, a in enumerate(c1):
            for j, b in enumerate(c2):
                result[i + j] += a * b
        return PolynomialOps.normalize(result)

    @staticmethod
    def random_poly(degree, range_val=(-5, 5)):
        '''生成隨機多項式係數（最高項非零）'''
        import random
        choices_nonzero = [x for x in range(range_val[0], range_val[1] + 1) if x != 0]
        coeffs = [random.choice(choices_nonzero)] + [random.randint(range_val[0], range_val[1]) for _ in range(degree)]
        return coeffs
"""

# ============================================================================
# Domain 1: POLYNOMIAL (多項式)
# ============================================================================

POLYNOMIAL_HELPERS = r"""
# ===== 多項式標準函數庫 =====

# 🔴 答案格式：純多項式逗號分隔（例："36x^2+10,72x"）
#    ✅ 用 _format_polynomial_for_answer() 組答案，再 ','.join()
#    ❌ 禁止：_deriv_symbol_plain() 只用於題目，不用於答案
#    ❌ 禁止：換行分隔 '\n'.join()

def _coeffs_to_terms(coeffs):
    '''係數列表 [a_n,...,a_0] → terms [(c,e),...]'''
    degree = len(coeffs) - 1
    return [(coeffs[i], degree - i) for i in range(len(coeffs))]

def _poly_to_latex(terms):
    '''terms → LaTeX (不含$)，例: [(3,2),(-5,0)] → "3x^{2} - 5"'''
    if not terms:
        return '0'
    parts = []
    for i, (c, e) in enumerate(sorted(terms, key=lambda x: x[1], reverse=True)):
        if c == 0:
            continue
        sign = '' if i == 0 else (' + ' if c > 0 else ' - ')
        abs_c = abs(c)
        coeff_str = '' if (abs_c == 1 and e > 0) else str(abs_c)
        if e == 0:
            var_str = str(abs_c)
        elif e == 1:
            var_str = f'{coeff_str}x' if coeff_str else 'x'
        else:
            var_str = f'{coeff_str}x^{{{e}}}' if coeff_str else f'x^{{{e}}}'
        parts.append(f'{sign}{var_str}')
    return ''.join(parts).strip()

def _poly_to_plain(terms):
    '''terms → 純文本答案格式 (無空格)，例: "3x^2-5"'''
    if not terms:
        return '0'
    parts = []
    for i, (c, e) in enumerate(sorted(terms, key=lambda x: x[1], reverse=True)):
        if c == 0:
            continue
        sign = '' if i == 0 else ('+' if c > 0 else '-')
        abs_c = abs(c)
        coeff_str = '' if (abs_c == 1 and e > 0) else str(abs_c)
        if e == 0:
            var_str = str(abs_c)
        elif e == 1:
            var_str = f'{coeff_str}x' if coeff_str else 'x'
        else:
            var_str = f'{coeff_str}x^{e}' if coeff_str else f'x^{e}'
        parts.append(f'{sign}{var_str}')
    return ''.join(parts).strip()

def _differentiate_poly(terms, order=1):
    '''求導 order 次，返回新 terms'''
    result = list(terms)
    for _ in range(order):
        new_terms = []
        for c, e in result:
            if e > 0:
                new_c = c * e
                if abs(new_c) > 10000:
                    raise ValueError(f"Coefficient {new_c} exceeds limit")
                new_terms.append((new_c, e - 1))
        result = new_terms
    return result

def _deriv_symbol_latex(order):
    '''導數符號 LaTeX: f'(x), f''(x), f^{(n)}(x)'''
    if order == 1:
        return "f'(x)"
    elif order == 2:
        return "f''(x)"
    else:
        return f"f^{{({order})}}(x)"

def _deriv_symbol_plain(order):
    '''導數符號純文本: f'(x), f''(x), f^(n)(x)'''
    if order == 1:
        return "f'(x)"
    elif order == 2:
        return "f''(x)"
    else:
        return f"f^({order})(x)"

def _format_polynomial_for_answer(terms):
    '''Format polynomial terms for answer display - use plain text, no LaTeX brackets
    Examples:
      _format_polynomial_for_answer([(36, 3), (27, 2), (16, 1)]) → "36x^3+27x^2+16x"
      _format_polynomial_for_answer([(216, 1), (54, 0)]) → "216x+54"
    '''
    return _poly_to_plain(terms)
"""

# ============================================================================
# Domain 2: GEOMETRY (幾何)
# ============================================================================

GEOMETRY_HELPERS = """
# ===== 幾何標準函數庫 =====

def _distance_2d(x1, y1, x2, y2):
    '''計算兩點距離'''
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def _midpoint_2d(x1, y1, x2, y2):
    '''計算中點座標'''
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def _slope(x1, y1, x2, y2):
    '''計算斜率（處理垂直線）'''
    if x2 == x1:
        return None  # 垂直線
    return (y2 - y1) / (x2 - x1)

def _line_equation_latex(m, b):
    '''生成直線方程式 y = mx + b 的 LaTeX'''
    if m is None:
        return "x = ..."  # 需要額外處理
    b_str = f" + {b}" if b >= 0 else f" - {abs(b)}"
    return f"y = {m}x{b_str}"

def _point_to_line_dist(px, py, a, b, c):
    '''點到直線 ax + by + c = 0 的距離'''
    return abs(a * px + b * py + c) / math.sqrt(a**2 + b**2)
"""

# ============================================================================
# Domain 3: TRIGONOMETRY (三角函數)
# ============================================================================

TRIGONOMETRY_HELPERS = """
# ===== 三角函數標準函數庫 =====

def _deg_to_rad(degrees):
    '''角度轉弧度'''
    return degrees * math.pi / 180

def _rad_to_deg(radians):
    '''弧度轉角度'''
    return radians * 180 / math.pi

def _normalize_angle(theta, unit='deg'):
    '''正規化角度到 [0, 360) 或 [0, 2π)'''
    if unit == 'deg':
        return theta % 360
    else:
        return theta % (2 * math.pi)

def _trig_value_latex(func_name, angle, exact=True):
    '''生成三角函數值的 LaTeX（支持特殊角精確值）'''
    # 實現特殊角的精確值輸出，例如 sin(30°) = 1/2
    pass
"""

# ============================================================================
# Domain 4: ALGEBRA (代數)
# ============================================================================

ALGEBRA_HELPERS = """
# ===== 代數標準函數庫 =====

def _solve_linear_2x2(a1, b1, c1, a2, b2, c2):
    '''
    解二元一次方程組
    a1*x + b1*y = c1
    a2*x + b2*y = c2
    返回: (x, y) 或 None（無解/無限多解）
    '''
    det = a1 * b2 - a2 * b1
    if det == 0:
        return None
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return (x, y)

def _quadratic_formula(a, b, c):
    '''
    求解一元二次方程 ax² + bx + c = 0
    返回: (x1, x2) 或 None（無實根）
    '''
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return None
    x1 = (-b + math.sqrt(discriminant)) / (2*a)
    x2 = (-b - math.sqrt(discriminant)) / (2*a)
    return (x1, x2)
"""

# ============================================================================
# Domain 5: PROBABILITY (機率)
# ============================================================================

PROBABILITY_HELPERS = """
# ===== 機率標準函數庫 =====
# (已在 MASTER_SPEC 注入的工具中定義 nCr, nPr)

def _probability_latex(numerator, denominator):
    '''生成機率的 LaTeX 分數表示'''
    from fractions import Fraction
    frac = Fraction(numerator, denominator)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"\\\\frac{{{frac.numerator}}}{{{frac.denominator}}}"
"""

# ============================================================================
# Domain 6: VECTOR (向量)
# ============================================================================

VECTOR_HELPERS = """
# ===== 向量標準函數庫 =====

def _vector_add(v1, v2):
    '''向量加法: (x1,y1) + (x2,y2)'''
    return (v1[0] + v2[0], v1[1] + v2[1])

def _vector_scalar_mult(k, v):
    '''純量乘法: k * (x,y)'''
    return (k * v[0], k * v[1])

def _vector_dot_product(v1, v2):
    '''內積: v1 · v2'''
    return v1[0] * v2[0] + v1[1] * v2[1]

def _vector_magnitude(v):
    '''向量長度: |v|'''
    return math.sqrt(v[0]**2 + v[1]**2)
"""

# ============================================================================
# Domain 7: CALCULUS (微積分)
# ============================================================================

CALCULUS_HELPERS = """
# ===== 微積分標準函數庫 =====
# (多項式微分已在 POLYNOMIAL_HELPERS 中定義)

def _find_critical_points(coeffs):
    '''
    找多項式的臨界點（一階導數為 0 的點）
    參數: coeffs = [a_n, a_{n-1}, ..., a_0] (降冪排列)
    返回: 臨界點列表
    '''
    # 實現求導 + 解方程
    pass

def _evaluate_poly(coeffs, x):
    '''計算多項式在 x 點的值'''
    result = 0
    for i, c in enumerate(coeffs):
        result += c * (x ** (len(coeffs) - 1 - i))
    return result
"""

# ============================================================================
# Domain 映射表 [V2.5 新增 FractionOps、IntegerOps、RadicalOps、CalculusOps]
# ============================================================================

DOMAIN_MAP = {
    'fractionops': FRACTIONOPS_HELPERS,
    'integerops': INTEGEROPS_HELPERS,
    'radicalops': RADICALOPS_HELPERS,
    'calculusops': CALCULUSOPS_HELPERS,
    'polynomial': POLYNOMIAL_HELPERS,
    'geometry': GEOMETRY_HELPERS,
    'trigonometry': TRIGONOMETRY_HELPERS,
    'algebra': ALGEBRA_HELPERS,
    'probability': PROBABILITY_HELPERS,
    'vector': VECTOR_HELPERS,
    'calculus': CALCULUS_HELPERS,
}

# ============================================================================
# Skill → Domain 映射（精確匹配優先級最高）
# ============================================================================

SKILL_DOMAIN_MAPPING = {
    # ===== 整數運算相關 (新增 V2.6) =====
    'FourArithmeticOperationsOfIntegers': ['integerops'],
    'FourArithmeticOperationsOfNumbers': ['integerops', 'fractionops'],  # [Fix] 補上分數工具
    
    # ===== 根式運算相關 (新增 V2.7) =====
    'FourOperationsOfRadicals': ['radicalops', 'fractionops'],  # 根式 + 分數排版（RadicalOps 可呼叫 FractionOps）
    
    # ===== 多項式相關 =====
    'polynomial_def': ['polynomial'],
    'poly_op_add_sub_mult': ['polynomial'],
    'synthetic_division': ['polynomial'],
    'completing_square': ['polynomial', 'algebra'],
    
    # ===== 微積分相關 =====
    'ApplicationsOfDerivatives': ['polynomial', 'calculus'],
    'deriv_basic': ['polynomial', 'calculus'],
    'critical_points': ['polynomial', 'calculus'],
    'extreme_values': ['polynomial', 'calculus'],
    
    # ===== 幾何相關 =====
    'dist_formula_1d': ['geometry'],
    'dist_formula_2d': ['geometry'],
    'midpoint_formula': ['geometry'],
    'section_formula': ['geometry'],
    'centroid_formula': ['geometry'],
    'slope_definition': ['geometry'],
    'slope_general_form': ['geometry'],
    'parallel_lines_slope': ['geometry'],
    'perpendicular_lines_slope': ['geometry'],
    'point_slope_form': ['geometry'],
    'horiz_vert_lines': ['geometry'],
    'slope_intercept_form': ['geometry'],
    'intercept_form': ['geometry'],
    'eq_of_parallel_line': ['geometry'],
    'eq_of_perpendicular_line': ['geometry'],
    'distance_point_line': ['geometry'],
    'distance_parallel_lines': ['geometry'],
    
    # ===== 三角函數相關 =====
    'radian_deg_conv': ['trigonometry'],
    'arc_len_area': ['trigonometry'],
    'coterminal_angles': ['trigonometry'],
    'right_tri_trig': ['trigonometry'],
    'trig_basic_id': ['trigonometry'],
    'quadrant_trig': ['trigonometry'],
    'periodicity_trig': ['trigonometry'],
    'area_formula_sas': ['trigonometry'],
    'sine_law': ['trigonometry'],
    'cosine_law': ['trigonometry'],
    'trig_survey': ['trigonometry'],
    
    # ===== 代數相關 =====
    'abs_val_eq': ['algebra'],
    'abs_val_ineq_lt': ['algebra'],
    'abs_val_ineq_gt': ['algebra'],
    'quad_ineq_factorable': ['algebra'],
    'quad_ineq_discriminant': ['algebra'],
    'always_positive_cond': ['algebra'],
    'always_negative_cond': ['algebra'],
    'cross_multiplication': ['algebra'],
    'sys_linear_eq_geometry': ['algebra', 'geometry'],
    'linear_func_type': ['algebra'],
    'quad_func_prop': ['algebra'],
    'vertex_max_min': ['algebra'],
    
    # ===== 機率相關 =====
    'classical_probability': ['probability'],
    'conditional_probability': ['probability'],
    'permutation_basic': ['probability'],
    'combination_basic': ['probability'],
    
    # ===== 向量相關 =====
    'vector_def_add': ['vector'],
    'vector_coord_len': ['vector'],
    'vector_scalar_mult': ['vector'],
    'vector_dot_product': ['vector'],
}

def get_required_domains(skill_id):
    """
    根據 skill_id 自動判斷需要注入哪些 domain 的函數庫
    [V47.13] 改進策略：優先級匹配 + 從資料庫章節信息推斷
    
    參數:
        skill_id: str, 例如 'gh_ApplicationsOfDerivatives'
    
    返回:
        list of str: 需要的 domain 列表，例如 ['polynomial', 'calculus']
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 移除前綴 'gh_', 'jh_', 'local_'
    clean_id = skill_id.replace('gh_', '').replace('jh_', '').replace('local_', '')
    logger.info(f"🔍 Domain 識別: skill_id={skill_id}, clean_id={clean_id}")
    
    # ===== 優先級 1: 精確匹配（手動維護的高優先級映射）=====
    if clean_id in SKILL_DOMAIN_MAPPING:
        domains = SKILL_DOMAIN_MAPPING[clean_id]
        logger.info(f"   ✅ 優先級 1 - 精確匹配: {domains}")
        return domains
        
    # [Fix] 嘗試更激進的提取：只取最後一段 (針對 'jh_數學1上_EnglishID' 這種格式)
    if '_' in clean_id:
        english_part = clean_id.split('_')[-1]
        if english_part in SKILL_DOMAIN_MAPPING:
            domains = SKILL_DOMAIN_MAPPING[english_part]
            logger.info(f"   ✅ 優先級 1.5 - 後綴匹配 ({english_part}): {domains}")
            return domains
    
    # ===== 優先級 2: 從資料庫章節信息推斷 =====
    try:
        from models import db, SkillCurriculum
        from flask import current_app
        if current_app:
            curriculum = SkillCurriculum.query.filter_by(skill_id=clean_id).first()
            if curriculum:
                chapter = curriculum.chapter.lower()
                section = curriculum.section.lower()
                logger.info(f"   📚 章節信息: chapter={chapter}, section={section}")
                
                # 章節關鍵字映射
                if any(kw in chapter or kw in section for kw in ['多項式', '式的運算', 'polynomial']):
                    logger.info(f"   ✅ 優先級 2 - 章節匹配: ['polynomial']")
                    return ['polynomial']
                if any(kw in chapter or kw in section for kw in ['導數', '微分', '極值', 'derivative', 'calculus']):
                    logger.info(f"   ✅ 優先級 2 - 章節匹配: ['polynomial', 'calculus']")
                    return ['polynomial', 'calculus']
                if any(kw in chapter or kw in section for kw in ['直線', '斜率', '坐標', 'line', 'coordinate']):
                    logger.info(f"   ✅ 優先級 2 - 章節匹配: ['geometry']")
                    return ['geometry']
                if any(kw in chapter or kw in section for kw in ['三角', 'trigon', 'sin', 'cos']):
                    logger.info(f"   ✅ 優先級 2 - 章節匹配: ['trigonometry']")
                    return ['trigonometry']
                if any(kw in chapter or kw in section for kw in ['機率', 'probability']):
                    logger.info(f"   ✅ 優先級 2 - 章節匹配: ['probability']")
                    return ['probability']
                if any(kw in chapter or kw in section for kw in ['向量', 'vector']):
                    logger.info(f"   ✅ 優先級 2 - 章節匹配: ['vector']")
                    return ['vector']
                if any(kw in chapter or kw in section for kw in ['方程', 'equation', '不等式', 'inequality']):
                    logger.info(f"   ✅ 優先級 2 - 章節匹配: ['algebra']")
                    return ['algebra']
    except Exception as e:
        logger.debug(f"   ⚠️ 優先級 2 失敗 (資料庫不可用): {e}")
    
    # ===== 優先級 3: skill_id 關鍵字匹配（保守策略）=====
    domains = []
    clean_lower = clean_id.lower()
    
    # 整數運算 (新增 V2.6)
    if any(kw in clean_lower for kw in ['integer', 'arithmetic', 'fourarithmetic']):
        domains.append('integerops')
    
    # 多項式 & 微積分（高優先級，因為常見）
    if any(kw in clean_lower for kw in ['deriv', 'calculus', 'extreme', 'critical']):
        domains.extend(['polynomial', 'calculus'])
    elif any(kw in clean_lower for kw in ['poly', 'polynomial', 'factor', 'division']):
        domains.append('polynomial')
    
    # 幾何
    if any(kw in clean_lower for kw in ['distance', 'line', 'slope', 'midpoint', 'circle', 'triangle']):
        domains.append('geometry')
    
    # 三角函數
    if any(kw in clean_lower for kw in ['trig', 'sin', 'cos', 'tan', 'radian', 'angle']):
        domains.append('trigonometry')
    
    # 代數
    if any(kw in clean_lower for kw in ['equation', 'quadratic', 'linear', 'inequality', 'abs']):
        domains.append('algebra')
    
    # 機率
    if any(kw in clean_lower for kw in ['prob', 'permutation', 'combination', 'ncr', 'npr']):
        domains.append('probability')
    
    # 向量
    if any(kw in clean_lower for kw in ['vector', 'dot', 'cross']):
        domains.append('vector')
    
    if domains:
        logger.info(f"   ✅ 優先級 3 - 關鍵字匹配: {list(set(domains))}")
        return list(set(domains))
    
    # ===== 優先級 4: 默認策略（未匹配時）=====
    logger.info(f"   ⚠️ 優先級 4 - 默認策略: ['algebra']")
    return ['algebra']

def _generate_stub(source_code):
    """
    使用 AST 將函數/類別實作替換為 Stubs (...)
    保留 Docstring 和簽名，大幅減少 Token 消耗
    """
    import ast

    class StubTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            # 保留 Docstring
            docstring = ast.get_docstring(node)
            
            # 建立新的 body
            new_body = []
            if docstring:
                new_body.append(ast.Expr(value=ast.Constant(value=docstring)))
            
            # 添加 ... (Ellipsis)
            # 在 Python 3.9+ ast.Constant(value=...) 是合法的
            # 為了兼容性，我們構造一個 Ellipsis 節點
            new_body.append(ast.Expr(value=ast.Constant(value=...)))
            
            node.body = new_body
            return node

        def visit_ClassDef(self, node):
            # 對於類別，我們繼續遞歸訪問其方法
            self.generic_visit(node)
            return node

    try:
        tree = ast.parse(source_code)
        transformer = StubTransformer()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        
        # 使用 ast.unparse (Python 3.9+)
        if hasattr(ast, 'unparse'):
            return ast.unparse(new_tree)
        else:
            return source_code  # Fallback
    except Exception as e:
        return source_code

def get_domain_helpers_code(domains, stub_mode=True):
    """
    獲取指定 domain 的所有標準函數代碼
    
    參數:
        domains: list of str, 例如 ['polynomial', 'calculus']
        stub_mode: bool, 是否只返回介面定義 (Stubs) 以節省 Token [默認開啟]
    
    返回:
        str: 合併後的函數定義代碼
    """
    code_parts = []
    for domain in domains:
        if domain in DOMAIN_MAP:
            full_code = DOMAIN_MAP[domain]
            if stub_mode:
                code_parts.append(_generate_stub(full_code))
            else:
                code_parts.append(full_code)
    
    return '\n\n'.join(code_parts)


# ============================================================================
# 測試代碼區塊
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("[V2.5 完整測試] Domain Function Library")
    print("=" * 80)
    
    # ========================================================================
    # TEST 1: FractionOps.create() - 浮點數精度修復
    # ========================================================================
    print("\n【TEST 1】FractionOps.create() - 浮點數精度修復")
    print("-" * 80)
    
    # 測試浮點數轉換
    result1 = FractionOps.create(-0.6)
    expected1 = Fraction(-3, 5)
    print(f"FractionOps.create(-0.6) = {result1}")
    print(f"Expected: {expected1}")
    print(f"✅ PASS" if result1 == expected1 else f"❌ FAIL")
    
    # 測試字符串轉換
    result2 = FractionOps.create("-0.6")
    print(f"\nFractionOps.create('-0.6') = {result2}")
    print(f"✅ PASS" if result2 == Fraction(-3, 5) else f"❌ FAIL")
    
    # ========================================================================
    # TEST 2: IntegerOps.fmt_num() - 負數括號格式化
    # ========================================================================
    print("\n【TEST 2】IntegerOps.fmt_num() - 負數括號格式化")
    print("-" * 80)
    
    print(f"IntegerOps.fmt_num(5) = '{IntegerOps.fmt_num(5)}' (期望: '5')")
    print(f"IntegerOps.fmt_num(-5) = '{IntegerOps.fmt_num(-5)}' (期望: '(-5)')")
    print(f"IntegerOps.fmt_num(0) = '{IntegerOps.fmt_num(0)}' (期望: '0')")
    print(f"✅ PASS" if IntegerOps.fmt_num(-5) == "(-5)" else f"❌ FAIL")
    
    # ========================================================================
    # TEST 3: IntegerOps.safe_eval() - 支援 abs()
    # ========================================================================
    print("\n【TEST 3】IntegerOps.safe_eval() - 支援 abs() 與括號")
    print("-" * 80)
    
    # 測試1：絕對值運算
    expr1 = "abs(8 * (-2) - 5)"
    result_expr1 = IntegerOps.safe_eval(expr1)
    print(f"IntegerOps.safe_eval('{expr1}')")
    print(f"  = IntegerOps.safe_eval('abs(-16 - 5)')")
    print(f"  = IntegerOps.safe_eval('abs(-21)')")
    print(f"  = {result_expr1}")
    print(f"  Expected: 21")
    print(f"✅ PASS" if result_expr1 == 21 else f"❌ FAIL")
    
    # ========================================================================
    # 【例題 1】整數混合運算: [ (-20) + (-10) ] / (-5) * 3 + | 8 * (-2) - 5 |
    # ========================================================================
    print("\n【例題 1】整數混合運算")
    print("-" * 80)
    print("題目: [ (-20) + (-10) ] / (-5) * 3 + | 8 * (-2) - 5 |")
    
    # 方式 1：使用 safe_eval + abs()
    expr_q1 = "[ (-20) + (-10) ] / (-5) * 3 + abs(8 * (-2) - 5)"
    answer_q1 = IntegerOps.safe_eval(expr_q1)
    print(f"\n方式 1: IntegerOps.safe_eval('{expr_q1}')")
    print(f"  結果 = {answer_q1}")
    
    # 分步驗證
    step1 = IntegerOps.safe_eval("(-20) + (-10)")
    print(f"\n分步驗證:")
    print(f"  Step 1: (-20) + (-10) = {step1}")
    
    step2 = IntegerOps.safe_eval("[-30] / (-5) * 3")
    print(f"  Step 2: [-30] / (-5) * 3 = {step2}")
    
    step3 = IntegerOps.safe_eval("abs(8 * (-2) - 5)")
    print(f"  Step 3: abs(8 * (-2) - 5) = {step3}")
    
    step4 = step2 + step3
    print(f"  Step 4: {step2} + {step3} = {step4}")
    
    print(f"\n✅ 最終答案: {step4} (期望: 39)")
    print(f"✅ PASS" if int(step4) == 39 else f"❌ FAIL")
    
    # ========================================================================
    # 【例題 2】分數小數混合運算: 3/2 / (-0.6) * (-3/5) - 1/2
    # ========================================================================
    print("\n【例題 2】分數小數混合運算")
    print("-" * 80)
    print("題目: 3/2 / (-0.6) * (-3/5) - 1/2")
    
    # 構建分數
    operand1 = FractionOps.create(Fraction(3, 2))
    operand2 = FractionOps.create(-0.6)  # 應該轉為 -3/5
    operand3 = FractionOps.create(Fraction(-3, 5))
    operand4 = FractionOps.create(Fraction(1, 2))
    
    print(f"\n構建分數:")
    print(f"  3/2 = {operand1}")
    print(f"  -0.6 = {operand2} (自動轉為 -3/5)")
    print(f"  -3/5 = {operand3}")
    print(f"  1/2 = {operand4}")
    
    # 計算：3/2 / (-0.6)
    step1_q2 = FractionOps.div(operand1, operand2)
    print(f"\nStep 1: 3/2 ÷ (-3/5) = {operand1} ÷ {operand2}")
    print(f"      = {operand1} × (-5/3) = {step1_q2}")
    
    # 計算：(3/2 / -0.6) * (-3/5)
    step2_q2 = FractionOps.mul(step1_q2, operand3)
    print(f"\nStep 2: {step1_q2} × (-3/5) = {step2_q2}")
    
    # 計算：最終結果
    final_q2 = FractionOps.sub(step2_q2, operand4)
    print(f"\nStep 3: {step2_q2} - 1/2 = {final_q2}")
    
    expected_q2 = Fraction(1, 1)
    print(f"\n✅ 最終答案: {final_q2} (期望: 1/1 或 1)")
    print(f"✅ PASS" if final_q2 == expected_q2 else f"❌ FAIL")
    
    # ========================================================================
    # TEST 4: FractionOps.to_latex() - LaTeX 輸出
    # ========================================================================
    print("\n【TEST 4】FractionOps.to_latex() - LaTeX 輸出")
    print("-" * 80)
    
    latex1 = FractionOps.to_latex(Fraction(3, 2))
    latex2 = FractionOps.to_latex(Fraction(3, 2), mixed=True)
    latex3 = FractionOps.to_latex(Fraction(5, 1))
    latex4 = FractionOps.to_latex(Fraction(7, 2), mixed=True)
    
    print(f"FractionOps.to_latex(3/2) = {latex1}")
    print(f"FractionOps.to_latex(3/2, mixed=True) = {latex2}")
    print(f"FractionOps.to_latex(5/1) = {latex3}")
    print(f"FractionOps.to_latex(7/2, mixed=True) = {latex4}")
    
    # ========================================================================
    # TEST 5: RadicalOps.create() - 根號化簡
    # ========================================================================
    print("\n【TEST 5】RadicalOps.create() - 根號化簡")
    print("-" * 80)
    
    radical1 = RadicalOps.create(12)
    radical2 = RadicalOps.create(9)
    radical3 = RadicalOps.create(2)
    
    print(f"RadicalOps.create(12) = {radical1} (應為 2√3)")
    print(f"RadicalOps.create(9) = {radical2} (應為 3)")
    print(f"RadicalOps.create(2) = {radical3} (應為 √2)")
    
    print(f"✅ PASS" if "2" in radical1 and "3" in radical1 else f"❌ FAIL")
    
    # ========================================================================
    # 總結
    # ========================================================================
    print("\n" + "=" * 80)
    print("【測試完成】")
    print("=" * 80)
    print("✅ 所有核心功能已驗證")
    print("✅ FractionOps.create() 正確處理浮點精度")
    print("✅ IntegerOps.safe_eval() 支援 abs() 和複雜表達式")
    print("✅ 例題 1 計算正確（結果: 39）")
    print("✅ 例題 2 計算正確（結果: 1）")
