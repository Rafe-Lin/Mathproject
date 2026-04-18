# skills/jh_equation_word_problem_setup.py
import random

def generate(level=1):
    """
    生成一道「應用問題列式」的題目。
    """
    scenarios = [
        ("小明買了 5 支筆，總共花了 100 元，假設一支筆 x 元，請依題意列出方程式。", "5x=100"),
        ("一個長方形的長比寬多 3 公分，周長是 30 公分。假設寬是 x 公分，請依題意列出方程式。", "2(x+(x+3))=30"),
        ("小華的年齡比小明大 5 歲，兩人年齡和是 25 歲。假設小明的年齡是 x 歲，請依題意列出方程式。", "x+(x+5)=25"),
        ("連續三個偶數的和是 66。假設最小的偶數是 x，請依題意列出方程式。", "x+(x+2)+(x+4)=66"),
    ]

    question, answer = random.choice(scenarios)

    question_text = f"請依據以下情境列出一元一次方程式（不需計算）：\n\n{question}"
    correct_answer = answer

    context_string = "學習將應用問題的情境轉化為數學方程式。"

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

    # 簡單的直接比對，未來可擴充更智能的比對（如符號運算庫）
    if user == correct:
        is_correct = True
    else:
        is_correct = False

    result_text = f"完全正確！列式為 {correct_answer}。" if is_correct else f"列式不正確。參考答案為：{correct_answer}"
    return {
        "correct": is_correct,
        "result": result_text,
        "next_question": True
    }