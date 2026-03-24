from core.integer_domain_functions import IntegerFunctionHelper

_INT_HELPER = IntegerFunctionHelper()
_INT_CONFIG = {'family': 'int_eval_batch', 'source_text': '12\\div(-4)\\times(-3)', 'expressions': [{'original': '12\\div(-4)\\times(-3)', 'skeleton': '__N0__/(__N1__)*(__N2__)', 'values': [12, -4, -3]}]}

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
