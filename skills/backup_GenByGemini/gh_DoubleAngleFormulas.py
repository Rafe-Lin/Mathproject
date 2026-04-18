import random
from fractions import Fraction

# Helper to format fractions for display in LaTeX
def format_fraction(frac):
    if frac.denominator == 1:
        return str(frac.numerator)
    # Use double braces for LaTeX command arguments within f-strings or .format()
    return r"\\frac{{{}}}{{{}}}".format(frac.numerator, frac.denominator)

# Helper to format angle ranges for quadrants in LaTeX
def format_angle_range(quadrant):
    if quadrant == 1: return r"0 < \\theta < \\frac{{\\pi}}{{2}}"
    if quadrant == 2: return r"\\frac{{\\pi}}{{2}} < \\theta < \\pi"
    if quadrant == 3: return r"\\pi < \\theta < \\frac{{3\\pi}}{{2}}"
    if quadrant == 4: return r"\\frac{{3\\pi}}{{2}} < \\theta < 2\\pi"
    return "" # Should not happen with current random choice

def generate(level=1):
    """
    生成「二倍角公式」相關題目。
    包含：
    1. 已知 sinθ 或 cosθ 及象限，求 sin 2θ, cos 2θ, tan 2θ。
    2. 已知 sinθ + cosθ 的值，求 sin 2θ。
    """
    problem_type = random.choice(['quadrant_given', 'sum_cos_sin'])

    if problem_type == 'quadrant_given':
        return generate_quadrant_given_problem()
    elif problem_type == 'sum_cos_sin':
        return generate_sum_cos_sin_problem()

def generate_quadrant_given_problem():
    """
    生成已知 sinθ 或 cosθ 及象限，求 sin 2θ, cos 2θ, tan 2θ 的題目。
    """
    # 選擇一個勾股數組 (a, b 為兩股，c 為斜邊)
    # 確保 a < b 以便於隨機選擇股長
    pythagorean_triples = [
        (3, 4, 5),
        (5, 12, 13),
        (8, 15, 17),
        (7, 24, 25),
    ]
    a_leg, b_leg, hypotenuse = random.choice(pythagorean_triples)

    # 隨機選擇題目給定的是 sinθ 還是 cosθ
    given_trig_func = random.choice(['sin', 'cos'])
    
    # 隨機選擇勾股數組中的哪個股長作為給定三角函數的分子
    numerator_for_given = random.choice([a_leg, b_leg])
    denominator = hypotenuse

    # 隨機選擇象限
    quadrant = random.randint(1, 4)
    quadrant_range_latex = format_angle_range(quadrant)

    # 根據象限判斷 sinθ 和 cosθ 的正負號
    sin_sign = 1 if quadrant in [1, 2] else -1
    cos_sign = 1 if quadrant in [1, 4] else -1

    # 根據給定值確定 sinθ 和 cosθ 的實際值
    if given_trig_func == 'sin':
        sin_theta_val = Fraction(numerator_for_given, denominator) * sin_sign
        # 另一股長用於 cosθ
        other_leg = b_leg if numerator_for_given == a_leg else a_leg
        cos_theta_val = Fraction(other_leg, denominator) * cos_sign
        given_value_str = f"\\sin \\theta = {format_fraction(sin_theta_val)}"
    else: # given_trig_func == 'cos'
        cos_theta_val = Fraction(numerator_for_given, denominator) * cos_sign
        # 另一股長用於 sinθ
        other_leg = b_leg if numerator_for_given == a_leg else a_leg
        sin_theta_val = Fraction(other_leg, denominator) * sin_sign
        given_value_str = f"\\cos \\theta = {format_fraction(cos_theta_val)}"

    # 計算 tanθ。對於選定的勾股數組和非象限角，cosθ 不會為零。
    tan_theta_val = sin_theta_val / cos_theta_val

    # 利用二倍角公式計算 sin 2θ, cos 2θ, tan 2θ
    sin2theta = 2 * sin_theta_val * cos_theta_val
    
    # 選擇一個 cos 2θ 的變形公式，例如 2cos²θ − 1
    cos2theta = 2 * (cos_theta_val**2) - 1
    
    # 計算 tan 2θ
    if cos2theta == 0: # 理論上可能，但對於此類題目通常不會發生
        tan2theta_result = "undefined" 
    else:
        tan2theta_result = sin2theta / cos2theta

    # 構建問題文本
    question_text = (
        f"已知 ${quadrant_range_latex}$，且 ${given_value_str}$，"
        r"求 $\\sin 2\\theta$, $\\cos 2\\theta$ 與 $\\tan 2\\theta$ 的值。"
        "<br>請以「sin2θ值,cos2θ值,tan2θ值」的格式作答，例如 $-1/2, 1/2, -1$。"
    )

    # 構建正確答案字符串
    correct_answer = f"{format_fraction(sin2theta)}, {format_fraction(cos2theta)}, {format_fraction(tan2theta_result)}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sum_cos_sin_problem():
    """
    生成已知 sinθ + cosθ 的值，求 sin 2θ 的題目。
    """
    # 選擇一個勾股數組來生成 sinθ 和 cosθ 的基礎值
    pythagorean_triples = [
        (3, 4, 5),
        (5, 12, 13),
    ]
    a_leg, b_leg, hypotenuse = random.choice(pythagorean_triples)
    
    # 隨機分配 sinθ 和 cosθ 的正負號
    sin_theta_sign = random.choice([1, -1])
    cos_theta_sign = random.choice([1, -1])

    # 隨機決定哪股長對應 sinθ，哪股長對應 cosθ
    if random.random() < 0.5:
        sin_theta_val = Fraction(a_leg * sin_theta_sign, hypotenuse)
        cos_theta_val = Fraction(b_leg * cos_theta_sign, hypotenuse)
    else:
        sin_theta_val = Fraction(b_leg * sin_theta_sign, hypotenuse)
        cos_theta_val = Fraction(a_leg * cos_theta_sign, hypotenuse)

    # 計算 k 值 (sinθ + cosθ)
    k_value = sin_theta_val + cos_theta_val
    # 利用公式 sin 2θ = 2sinθcosθ
    sin2theta = 2 * sin_theta_val * cos_theta_val

    # 構建問題文本
    question_text = (
        f"已知 $\\sin\\theta + \\cos\\theta = {format_fraction(k_value)}$，求 $\\sin 2\\theta$ 的值。"
    )
    correct_answer = format_fraction(sin2theta)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    user_answer 和 correct_answer 可能包含多個逗號分隔的值。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()

    is_correct = False
    feedback_text = ""

    try:
        if "," in correct_answer: # 處理多個答案的情況 (例如 sin 2θ, cos 2θ, tan 2θ)
            user_parts_str = [part.strip() for part in user_answer.split(',')]
            correct_parts_str = [part.strip() for part in correct_answer.split(',')]

            if len(user_parts_str) != len(correct_parts_str):
                feedback_text = "答案數量不符，請確認您提供了所有要求的三角函數值。"
                return {"correct": False, "result": feedback_text, "next_question": True}

            all_match = True
            # 用於提示的 LaTeX 格式的三角函數名稱
            part_names = [r"\\sin 2\\theta", r"\\cos 2\\theta", r"\\tan 2\\theta"]
            
            for i in range(len(correct_parts_str)):
                correct_val_str = correct_parts_str[i]
                user_val_str = user_parts_str[i]

                if correct_val_str == "undefined":
                    # 如果正確答案是 undefined，則使用者答案也必須是 undefined (不區分大小寫)
                    if user_val_str.lower() != "undefined":
                        all_match = False
                        feedback_text += f"您的 ${part_names[i]}$ 值不正確。正確應為 undefined。"
                        break
                else:
                    # 對於數值答案，轉換為 Fraction 進行比較
                    correct_frac = Fraction(correct_val_str)
                    user_frac = Fraction(user_val_str)
                    if user_frac != correct_frac:
                        all_match = False
                        feedback_text += f"您的 ${part_names[i]}$ 值不正確。正確應為 ${format_fraction(correct_frac)}$。"
                        break
            
            if all_match:
                is_correct = True
                feedback_text = "完全正確！"
            else:
                # 如果有部分答案不正確，補充通用提示
                if not feedback_text: 
                     feedback_text = "您的答案不完全正確。"

        else: # 處理單個答案的情況
            user_frac = Fraction(user_answer)
            correct_frac = Fraction(correct_answer)
            is_correct = (user_frac == correct_frac)
            if is_correct:
                feedback_text = f"完全正確！答案是 ${format_fraction(correct_frac)}$。"
            else:
                feedback_text = f"答案不正確。正確答案應為：${format_fraction(correct_frac)}$"

    except ValueError:
        feedback_text = "您的答案格式不正確，請確保輸入的是數字、分數 (例如 3/4) 或 'undefined'。"
    except ZeroDivisionError:
        feedback_text = "您的答案導致除以零錯誤，請檢查您的分數表示。"
    except Exception as e:
        feedback_text = f"檢查答案時發生錯誤：{e}"

    return {"correct": is_correct, "result": feedback_text, "next_question": True}