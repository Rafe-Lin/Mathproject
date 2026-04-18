import random

def generate(level=1):
    """
    生成一道「高次不等式圖形與勘根定理/重根」的題目。
    此為觀念題。
    """
    r1, r2 = random.sample(range(-5, 6), 2)
    
    if level == 1: # 奇次重根
        m = random.choice([1, 3])
        n = 1
        behavior = "穿越 x 軸"
    else: # 偶次重根
        m = random.choice([2, 4])
        n = 1
        behavior = "接觸 x 軸但未穿越 (反彈)"

    def format_factor(root, power):
        """輔助函式，格式化 (x-r) 的次方"""
        root_part = f"(x - {root})" if root > 0 else f"(x + {abs(root)})" if root < 0 else "x"
        power_map = {1: "", 2: "²", 3: "³", 4: "⁴", 5: "⁵"}
        power_part = power_map.get(power, f"^{power}")
        return f"{root_part}{power_part}"

    func_str = f"y = {format_factor(r1, m)} * {format_factor(r2, n)}"

    question_text = (
        f"觀察多項式函數 {func_str} 的圖形。\n"
        f"在 x = {r1} 這個根的位置，圖形會發生什麼事？\n\n"
        f"A) 穿越 x 軸\n"
        f"B) 接觸 x 軸但未穿越 (反彈)"
    )
    correct_answer = "A" if m % 2 != 0 else "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。奇數次重根會穿越，偶數次重根會反彈。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}