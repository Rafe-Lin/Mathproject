# \三角函數\弧長公式
import random

def generate(level=1):
    """
    生成一道「弧長公式」的題目。
    s = r * θ (θ 為弧度)
    """
    r = random.randint(5, 20)
    if level == 1:
        angle_deg = random.choice([30, 45, 60, 90, 180])
        angle_rad_str = {30: "π/6", 45: "π/4", 60: "π/3", 90: "π/2", 180: "π"}[angle_deg]
        question_text = f"一個半徑為 {r} 的扇形，其圓心角為 {angle_rad_str} 弧度，請問其弧長是多少？"
        correct_answer = f"{r}/6*π" if angle_deg == 30 else f"{r}/4*π" if angle_deg == 45 else f"{r}/3*π" if angle_deg == 60 else f"{r}/2*π" if angle_deg == 90 else f"{r}π"
    else: # level 2
        angle_deg = random.randint(20, 150)
        question_text = f"一個半徑為 {r} 的扇形，其圓心角為 {angle_deg}°，請問其弧長是多少？ (π≈3.14, 四捨五入至小數點後一位)"
        arc_length = r * (angle_deg * 3.14159 / 180)
        correct_answer = str(round(arc_length, 1))
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().replace(" ", "").replace("pi", "π")
    correct = str(correct_answer).strip().replace(" ", "")
    is_correct = (user == correct) or (abs(float(user.replace("π","3.14"))) - float(correct.replace("π","3.14"))) < 0.1
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}