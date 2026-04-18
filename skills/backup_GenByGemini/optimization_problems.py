# \微分應用\最佳化問題
import random

def generate(level=1):
    """
    生成一道「最佳化問題」的應用題。
    """
    if level == 1:
        perimeter = random.choice([20, 40, 60, 80, 100])
        question_text = f"一個周長為 {perimeter} 公尺的矩形，其可能的最大面積是多少平方公尺？"
        # 2(L+W)=P => L+W=P/2. Area=LW. Max area when L=W=P/4 (正方形)
        side = perimeter / 4
        correct_answer = str(side * side)
    else: # level 2
        question_text = "一個底面為正方形的開頂長方體容器，容積為 32 立方公分。請問如何設計能使其表面積最小？\n(此為觀念題，關鍵在於列出表面積函數並微分求極值)"
        correct_answer = "觀念題"
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": "text"}

def check(user_answer, correct_answer):
    if correct_answer == "觀念題": return {"correct": True, "result": "觀念正確！解決最佳化問題的關鍵是建立目標函數，並利用微分找極值。", "next_question": True}
    user = user_answer.strip().replace(" ", "")
    is_correct = (user == correct_answer)
    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    return {"correct": is_correct, "result": result_text, "next_question": True}