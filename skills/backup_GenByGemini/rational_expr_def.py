# skills/rational_expr_def.py
import random

def generate(level=1):
    """
    生成一道「分式的基本概念」題目
    """
    # level 參數暫時未使用，但保留以符合架構
    # 隨機生成分母 g(x)
    root1 = random.randint(-5, 5)
    root2 = random.randint(-5, 5)
    
    # 確保根不重複，讓題目有意義
    while root1 == root2:
        root2 = random.randint(-5, 5)

    # g(x) = (x - root1)(x - root2) = x² - (root1+root2)x + root1*root2
    b = -(root1 + root2)
    c = root1 * root2

    # 格式化分母字串
    g_str = "x²"
    if b != 0: g_str += f" {'+' if b > 0 else '-'} {abs(b)}x"
    if c != 0: g_str += f" {'+' if c > 0 else '-'} {abs(c)}"

    # 隨機生成分子 f(x)
    f_str = f"{random.randint(1,5)}x + {random.randint(-5,5)}"

    question_text = f"對於分式 ( {f_str} ) / ( {g_str} )，請問 x 不可以等於哪些數？\n(若有多個答案，請用逗號分隔)"
    
    # 答案就是分母的根
    answers = sorted([root1, root2])
    correct_answer = f"{answers[0]},{answers[1]}"
    
    context_string = f"找出使分式 ( {f_str} ) / ( {g_str} ) 分母為零的 x 值"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """檢查使用者輸入的 x 值是否正確"""
    user_nums = sorted([int(n.strip()) for n in user_answer.split(',') if n.strip()])
    correct_nums = sorted([int(n.strip()) for n in correct_answer.split(',')])
    
    if user_nums == correct_nums:
        return {"correct": True, "result": f"完全正確！答案是 {correct_answer}。"}
    else:
        return {"correct": False, "result": f"答案不正確。正確答案是：{correct_answer}"}