from core.integer_domain_functions import IntegerFunctionHelper

_INT_HELPER = IntegerFunctionHelper()
_INT_CONFIG = {'family': 'int_eval_batch', 'source_text': '(-60)\\div[(-7)\\times2-1]', 'expressions': [{'original': '(-60)\\div[(-7)\\times2-1]', 'skeleton': '(__N0__)/((__N1__)*__N2__-__N3__)', 'values': [-60, -7, 2, 1]}]}

def generate(level=1, **kwargs):
    return _INT_HELPER.generate_from_config(_INT_CONFIG)

def check(user_answer, correct_answer):
    u = str(user_answer or "").strip().replace(" ", "")
    c = str(correct_answer or "").strip().replace(" ", "")
    if u == c:
        return {"correct": True, "result": "正確"}
    try:
        if float(u) == float(c):
            return {"correct": True, "result": "正確"}
    except Exception:
        pass
    return {"correct": False, "result": "錯誤"}
