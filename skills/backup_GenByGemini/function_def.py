import random

def generate(level=1):
    """
    生成一個判斷是否為函數的題目。
    """
    # level 參數暫時未使用，但保留以符合架構
    points = []
    x_values = set()
    is_function = random.choice([True, False])

    num_points = random.randint(4, 5)

    if is_function:
        # 生成一個函數關係
        for _ in range(num_points):
            x = random.randint(-5, 5)
            # 確保 x 值不重複
            while x in x_values:
                x = random.randint(-5, 5)
            x_values.add(x)
            y = random.randint(-5, 5)
            points.append((x, y))
        correct_answer = "是"
    else:
        # 生成一個非函數關係 (一對多)
        x_values_list = random.sample(range(-5, 6), num_points - 1)
        # 隨機選一個 x 來重複
        repeated_x = random.choice(x_values_list)
        
        temp_x_values = set()
        for x in x_values_list:
            y = random.randint(-5, 5)
            points.append((x, y))
            temp_x_values.add(x)

        # 加入重複的 x，但 y 不同
        y1 = random.randint(-5, 5)
        # 確保 y 值不同
        y2 = random.randint(-5, 5)
        while y2 == y1:
            y2 = random.randint(-5, 5)
        
        # 找到與 repeated_x 配對的點並移除
        points = [p for p in points if p[0] != repeated_x]
        # 重新加入兩個點
        points.append((repeated_x, y1))
        points.append((repeated_x, y2))
        random.shuffle(points)
        correct_answer = "否"

    points_str = ", ".join([f"({p[0]}, {p[1]})" for p in points])
    question_text = f"給定一組點的集合 S = {{{points_str}}}。請問這個關係 y 是 x 的函數嗎？ (請回答 '是' 或 '否')"

    return {
        "question_text": question_text,
        "answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者對函數定義的判斷是否正確。
    """
    user_ans = user_answer.strip()
    if user_ans in ["是", "是函數", "yes", "y"]:
        user_ans_bool = "是"
    elif user_ans in ["否", "不是函數", "no", "n"]:
        user_ans_bool = "否"
    else:
        return {"correct": False, "result": "請回答 '是' 或 '否'。"}

    if user_ans_bool == correct_answer:
        return {"correct": True, "result": "完全正確！"}
    else:
        if correct_answer == "是":
            return {"correct": False, "result": "答案不正確。這是一個函數，因為每個 x 值都只對應到一個 y 值。"}
        else:
            return {"correct": False, "result": "答案不正確。這不是一個函數，因為至少有一個 x 值對應到多個 y 值。"}