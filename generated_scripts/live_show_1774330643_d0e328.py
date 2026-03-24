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
