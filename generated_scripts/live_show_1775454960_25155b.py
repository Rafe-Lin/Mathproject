
# ==============================================================================
# [AUTO-INJECTED RESOURCE] IntegerOps
# ==============================================================================
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

def generate(level=1, **kwargs):
    v1 = IntegerOps.random_nonzero(1, 100)
    v2 = IntegerOps.random_nonzero(-12, -1)
    eval_str = f'{v1} - {v2}'
    math_str = f'{IntegerOps.fmt_num(v1)} - {IntegerOps.fmt_num(v2)}'
    ans = IntegerOps.safe_eval(eval_str)
    return (f'計算 ${math_str}$ 的值。', str(int(round(ans))))

def check(user_answer, correct_answer):
    try:
        user_val = int(user_answer.strip())
        return user_val == int(correct_answer)
    except:
        return False