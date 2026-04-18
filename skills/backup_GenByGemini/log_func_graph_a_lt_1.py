# \函數\對數函數圖形 (0<a<1)
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「對數函數圖形 (0<a<1)」的觀念題。
    """
    a_den = random.randint(2, 5)
    question_text = (
        f"請在計算紙上畫出對數函數 y = log_(1/{a_den})(x) 的圖形。\n"
        f"提示：圖形通過 (1,0)，且為嚴格遞減函數。\n"
        "完成後請點擊「AI 檢查」。"
    )
    return {"question_text": question_text, "answer": None, "correct_answer": "graph"}

def check(user_answer, correct_answer):
    # This is a conceptual graph question, so any answer is accepted and a standard explanation is given.
    result_text = "觀念正確！當 0<a<1 時，對數函數圖形是遞減的。"
    return {"correct": True, "result": result_text, "next_question": True}