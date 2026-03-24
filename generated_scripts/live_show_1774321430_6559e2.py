def check(user_answer, correct_answer):
    try:
        return {'correct': str(user_answer).strip() == str(correct_answer).strip(), 'result': '自動補全比對'}
    except:
        return {'correct': False, 'result': '錯誤'}

def generate(level=1, **kwargs):
    return {'question_text': 'Fallback due to missing generate() wrapper', 'correct_answer': '\\text{Failed}'}