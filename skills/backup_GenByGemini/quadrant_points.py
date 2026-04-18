# skills/quadrant_points.py
import random

def generate(level=1):
    """生成「象限與點坐標」題目"""
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成一個點的坐標，避開坐標軸上的點
    x = random.randint(-5, 5)
    y = random.randint(-5, 5)
    
    # 確保點不在坐標軸上
    while x == 0 or y == 0:
        x = random.randint(-5, 5)
        y = random.randint(-5, 5)
    
    # 判斷象限
    if x > 0 and y > 0:
        quadrant = "第一象限"
    elif x < 0 and y > 0:
        quadrant = "第二象限"
    elif x < 0 and y < 0:
        quadrant = "第三象限"
    else: # x > 0 and y < 0
        quadrant = "第四象限"
    
    question_text = f"點 ({x}, {y}) 在直角坐標平面的哪個象限？"
    context_string = f"點 ({x}, {y}) 位於 {quadrant}"
    
    return {
        "question_text": question_text,
        "answer": quadrant,
        "correct_answer": quadrant,
        "context_string": context_string
    }

def check(user_answer, correct_answer):
    """檢查答案"""
    if correct_answer is None:
        return {"correct": False, "result": "系統錯誤：缺少正確答案"}
    
    user = user_answer.strip()
    correct = str(correct_answer).strip()
    
    # 允許多種回答方式
    correct_answers = [
        correct,
        correct.replace("象限", ""),
        correct.replace("第", "").replace("象限", ""),
        f"第{correct.replace('象限', '')}象限"
    ]
    
    # 也接受數字回答
    quadrant_map = {
        "1": "第一象限",
        "2": "第二象限", 
        "3": "第三象限",
        "4": "第四象限",
        "一": "第一象限",
        "二": "第二象限",
        "三": "第三象限",
        "四": "第四象限"
    }
    
    if user in quadrant_map:
        user = quadrant_map[user]
    
    if user in correct_answers:
        return {"correct": True, "result": "正確！"}
    else:
        return {"correct": False, "result": f"錯誤，正解：{correct_answer}"}