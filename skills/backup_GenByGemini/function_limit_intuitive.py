# \極限\函數極限 (直觀)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「函數極限 (直觀)」的觀念題。
    """
    a = random.randint(1, 5)
    l = random.randint(1, 10)
    question_text = (
        f"若函數 f(x) 的圖形在 x={a} 附近，無論從左邊或右邊靠近，其 y 值都非常趨近於 {l}，"
        f"請問 lim (x→{a}) f(x) 的值是多少？\n\n"
        f"A) {a}\nB) {l}\nC) 不存在"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')