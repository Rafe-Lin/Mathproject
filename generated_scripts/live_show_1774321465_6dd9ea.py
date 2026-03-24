import re

def generate(level=1):
    _math_str_fb = locals().get('math_str', locals().get('last_math_str', ''))
    if not _math_str_fb:
        _t = [str(v) for k, v in locals().items() if re.match('^t\\\\d+$', k)]
        _math_str_fb = ''.join(_t) if _t else '0'
    question_text = locals().get('question_text', '')
    if not question_text or '$' not in str(question_text):
        question_text = f'化簡 ${_math_str_fb}$ 的值。'
    correct_answer = locals().get('correct_answer', '')
    if correct_answer:
        correct_answer = str(correct_answer).replace('-', '-').replace('-', '-').replace('1\\sqrt', '\\sqrt')

def check(user_answer, correct_answer):
    try:
        return {'correct': str(user_answer).strip() == str(correct_answer).strip(), 'result': '自動補全比對'}
    except:
        return {'correct': False, 'result': '錯誤'}