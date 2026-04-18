# \統計\莖葉圖
import random
from .utils import check_answer

def generate(level=1):
    """
    生成一道「莖葉圖」的題目。
    """
    # 構造數據
    stems = [6, 7, 7, 8, 8, 8, 9]
    leaves = [random.randint(0,9) for _ in range(len(stems))]
    data = sorted([s*10 + l for s, l in zip(stems, leaves)])
    
    plot_str = "莖 | 葉\n"
    plot_str += "---|---\n"
    plot_str += "6 | " + " ".join(map(str, sorted([d%10 for d in data if 60<=d<70]))) + "\n"
    plot_str += "7 | " + " ".join(map(str, sorted([d%10 for d in data if 70<=d<80]))) + "\n"
    plot_str += "8 | " + " ".join(map(str, sorted([d%10 for d in data if 80<=d<90]))) + "\n"
    plot_str += "9 | " + " ".join(map(str, sorted([d%10 for d in data if 90<=d<100])))
    
    if level == 1:
        question_text = f"某組學生的體重(公斤)莖葉圖如下：\n{plot_str}\n請問體重最重的學生是幾公斤？"
        correct_answer = str(max(data))
    else: # level 2
        question_text = f"某組學生的體重(公斤)莖葉圖如下：\n{plot_str}\n請問這組數據的中位數是多少公斤？"
        median = data[len(data) // 2]
        correct_answer = str(median)
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    return check_answer(user_answer, correct_answer, check_type='numeric')