import random

def generate(level=1):
    """
    生成一道「三垂線定理」的觀念題。
    """
    question_text = (
        "三垂線定理描述了空間中點、線、面之間的垂直關係。其內容為：平面 E 外一點 P，自 P 作平面的垂線，垂足為 O；"
        "再自 O 作平面上一條直線 L 的垂線，垂足為 Q。則下列哪一條連線「必定」會垂直於直線 L？\n\n"
        "A) 線段 PO\n"
        "B) 線段 PQ\n"
        "C) 線段 OQ"
    )
    correct_answer = "B"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    user = user_answer.strip().upper()
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}