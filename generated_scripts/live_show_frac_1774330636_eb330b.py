from core.fraction_domain_functions import FractionFunctionHelper

_FRAC_HELPER = FractionFunctionHelper()
_FRAC_CONFIG = {'family': 'frac_eval_common_factor', 'source_text': '3\\frac{9}{11}\\times(-57)-1\\frac{9}{11}\\times(-57)', 'expr': '3 9/11*(-57)-1 9/11*(-57)', 'common_factor_pattern': {'shared_side': 'right', 'left': '3\\frac{9}{11}', 'right': '1\\frac{9}{11}', 'factor': '(-57)', 'op': '-'}}

def generate(level=1, **kwargs):
    runtime_config = _FRAC_HELPER.build_runtime_config(_FRAC_CONFIG, level=level, **kwargs)
    return _FRAC_HELPER.generate_from_config(runtime_config)

def check(user_answer, correct_answer):
    return _FRAC_HELPER.check_answer(_FRAC_CONFIG, user_answer, correct_answer)
