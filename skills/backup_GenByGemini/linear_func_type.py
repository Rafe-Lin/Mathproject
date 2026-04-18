import random

def generate(level=1):
    """
    生成一個判斷線型函數類型的題目。
    """
    # level 參數暫時未使用，但保留以符合架構
    a = random.randint(-5, 5)
    b = random.randint(-5, 5)

    # 格式化函數表達式
    if a == 0:
        func_str = f"y = {b}"
        func_type = "常數函數"
        graph_type = "水平線"
    elif a == 1:
        if b > 0:
            func_str = f"y = x + {b}"
        elif b < 0:
            func_str = f"y = x - {-b}"
        else: # b == 0
            func_str = f"y = x"
        func_type = "一次函數"
        graph_type = "斜直線"
    elif a == -1:
        if b > 0:
            func_str = f"y = -x + {b}"
        elif b < 0:
            func_str = f"y = -x - {-b}"
        else: # b == 0
            func_str = f"y = -x"
        func_type = "一次函數"
        graph_type = "斜直線"
    else: # a != 0, 1, -1
        if b > 0:
            func_str = f"y = {a}x + {b}"
        elif b < 0:
            func_str = f"y = {a}x - {-b}"
        else: # b == 0
            func_str = f"y = {a}x"
        func_type = "一次函數"
        graph_type = "斜直線"

    question_text = f"請問函數 {func_str} 是哪一種類型的線型函數？其圖形是哪一種線？ (請回答：函數類型,圖形類型，例如：一次函數,斜直線)"
    
    correct_answer = f"{func_type},{graph_type}"

    return {
        "question_text": question_text,
        "answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者對線型函數的分類是否正確。
    """
    # 清理使用者輸入，允許不同的分隔符和空格
    user_ans_parts = [part.strip() for part in user_answer.replace(' ', '').replace('，', ',').split(',')]
    correct_ans_parts = correct_answer.split(',')

    if len(user_ans_parts) != 2:
        return {"correct": False, "result": "請提供兩個答案，並用逗號分隔，例如：一次函數,斜直線"}

    user_func_type, user_graph_type = user_ans_parts
    correct_func_type, correct_graph_type = correct_ans_parts

    # 檢查函數類型
    is_func_type_correct = False
    if (user_func_type == correct_func_type):
        is_func_type_correct = True

    # 檢查圖形類型
    is_graph_type_correct = False
    if (user_graph_type == correct_graph_type):
        is_graph_type_correct = True

    if is_func_type_correct and is_graph_type_correct:
        return {"correct": True, "result": "完全正確！"}
    else:
        feedback = f"答案不完全正確。正確答案是：{correct_func_type}, {correct_graph_type}。 "
        if not is_func_type_correct:
            feedback += f"您在函數類型的判斷上出錯了。"
        if not is_graph_type_correct:
            feedback += f"您在圖形類型的判斷上出錯了。"
        return {"correct": False, "result": feedback}