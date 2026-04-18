# \三角函數\標準位置角與象限角
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「標準位置角與象限角」的題目。
    """
    if level == 1:
        angle = random.choice([45, 135, 225, 315])
        question_text = f"請問 {angle}° 是第幾象限角？ (請回答 一, 二, 三, 或 四)"
        if 0 < angle < 90: correct_answer = "一"
        elif 90 < angle < 180: correct_answer = "二"
        elif 180 < angle < 270: correct_answer = "三"
        else: correct_answer = "四"
    else: # level 2, 廣義角或觀念題
        q_type = random.choice(['large_angle', 'negative_angle', 'quadrantal'])
        if q_type == 'large_angle':
            angle = random.randint(400, 700)
            min_equiv_angle = angle % 360
            if 0 < min_equiv_angle < 90: quadrant = "一"
            elif 90 < min_equiv_angle < 180: quadrant = "二"
            elif 180 < min_equiv_angle < 270: quadrant = "三"
            else: quadrant = "四"
            question_text = f"請問 {angle}° 是第幾象限角？ (請回答 一, 二, 三, 或 四)"
            correct_answer = quadrant
        else: # q_type == 'quadrantal'
            angle = random.choice([90, 180, 270, 360])
            question_text = f"請問 {angle}° 是不是象限角？ (是/否)"
            correct_answer = "是"
            
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='case_insensitive')