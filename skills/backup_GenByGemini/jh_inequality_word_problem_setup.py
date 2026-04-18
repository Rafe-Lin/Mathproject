# skills/jh_inequality_word_problem_setup.py
import random

def generate(level=1):
    """
    生成一道「不等式應用問題列式」的題目。
    """
    scenarios = [
        ("小明帶了 100 元去買文具，買了一支 30 元的筆和數個 8 元的橡皮擦。假設他買了 x 個橡皮擦，錢還夠用，請依題意列出不等式。", "30+8x<=100"),
        ("某個博物館的門票，全票一張 250 元，學生票一張 150 元。一個旅行團有 50 人，其中有 x 位學生，若總票價不超過 10000 元，請依題意列出不等式。", "150x+250(50-x)<=10000"),
        ("一個梯形的上底為 5 公分，下底為 x 公分，高為 6 公分。若其面積大於 60 平方公分，請依題意列出不等式。", "(5+x)*6/2>60"),
    ]

    question, answer = random.choice(scenarios)

    question_text = f"請依據以下情境列出一元一次不等式（不需化簡或計算）：\n\n{question}"
    correct_answer = answer

    context_string = "學習將應用問題中的「超過、未滿、至少、至多」等條件，轉化為數學不等式。"

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

    # 這裡只做簡單比對，未來可擴充更智能的比對
    if user == correct:
        is_correct = True
        result_text = f"完全正確！列式為 {correct_answer}。"
    else:
        is_correct = False
        result_text = f"列式不正確。參考答案為：{correct_answer}"

    return {"correct": is_correct, "result": result_text, "next_question": True}