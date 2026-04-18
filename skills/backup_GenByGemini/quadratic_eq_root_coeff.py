# \複數\根與係數 (含虛根)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「根與係數 (含虛根)」的題目。
    """
    # 構造虛根
    root1 = complex(random.randint(1, 5), random.randint(1, 5))
    root2 = root1.conjugate()
    
    # ax²+bx+c=0, a=1
    # α+β = -b/a => b = -(α+β)
    # αβ = c/a => c = αβ
    b = -(root1 + root2).real
    c = (root1 * root2).real
    
    question_text = f"已知方程式 x² + {int(b)}x + {int(c)} = 0 的一根為 {root1}，請問另一根為何？(格式: a+bi)"
    correct_answer = f"{int(root2.real)}{'+' if root2.imag >= 0 else ''}{int(root2.imag)}i".replace("+-","-")
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user_answer = user_answer.replace(" ", "")
    return check_answer(user_answer, correct_answer)