# skills/jh_algebra_proof_odd_even.py
import random

def generate(level=1):
    """
    生成一道「奇偶數的代數證明」的題目。
    此為概念/證明題。
    """
    proofs = [
        "證明：奇數 + 奇數 = 偶數。",
        "證明：奇數 + 偶數 = 奇數。",
        "證明：偶數 + 偶數 = 偶數。",
        "證明：奇數 × 奇數 = 奇數。",
        "證明：奇數 × 偶數 = 偶數。",
    ]
    proof_to_show = random.choice(proofs)

    question_text = (
        f"請利用代數方法（例如，設偶數為 2n，奇數為 2n+1）來證明以下敘述：\n\n「{proof_to_show}」\n\n"
        "請在下方的「數位計算紙」上寫下你的證明過程。\n\n"
        "完成後，請點擊「AI 檢查」按鈕。"
    )

    return {
        "question_text": question_text,
        "answer": None,
        "correct_answer": "graph",
        "context_string": "學習使用代數表示法來證明關於奇數和偶數的性質。",
    }

def check(user_answer, correct_answer):
    return {
        "correct": False, 
        "result": "這是一道證明題，請在數位計算紙上作答後，點選「AI 檢查」。",
        "next_question": False
    }