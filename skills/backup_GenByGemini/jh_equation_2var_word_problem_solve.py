# skills/jh_equation_2var_word_problem_solve.py
import random

def generate(level=1):
    """
    生成一道「解二元一次應用問題」的題目。
    """
    # 雞兔同籠問題
    chickens = random.randint(10, 20)
    rabbits = random.randint(5, 15)
    
    heads = chickens + rabbits
    legs = 2 * chickens + 4 * rabbits
    
    question = f"雞兔同籠，已知共有 {heads} 個頭，{legs} 隻腳。請問雞和兔子各有幾隻？"
    answer = f"{chickens},{rabbits}"

    question_text = f"請解下列應用問題：\n\n{question}\n\n(請回答 雞的數量,兔子的數量，例如: 20,15)"
    correct_answer = answer

    context_string = "學習解讀應用問題，列出二元一次聯立方程式並求解。"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": "text",
        "context_string": context_string,
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的答案是否正確。
    """
    user = user_answer.strip().replace(" ", "")
    correct = str(correct_answer).strip().replace(" ", "")

    try:
        user_c, user_r = map(int, user.split(','))
        correct_c, correct_r = map(int, correct.split(','))
        if user_c == correct_c and user_r == correct_r:
            is_correct = True
            result_text = f"完全正確！答案是雞 {correct_c} 隻，兔子 {correct_r} 隻。"
        else:
            is_correct = False
            result_text = f"答案不正確。正確答案是：雞 {correct_c} 隻，兔子 {correct_r} 隻。"
    except ValueError:
        is_correct = False
        result_text = f"請用 '雞,兔' 的格式作答，例如 20,15。正確答案是：雞 {correct.split(',')[0]} 隻，兔子 {correct.split(',')[1]} 隻。"

    return {"correct": is_correct, "result": result_text, "next_question": True}