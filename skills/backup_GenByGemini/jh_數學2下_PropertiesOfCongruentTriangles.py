import random

def _generate_sss_problem():
    """Generates an SSS (Side-Side-Side) congruence problem."""
    mode = random.choice(['identify', 'calculate'])
    if mode == 'identify':
        s1, s2, s3 = sorted(random.sample(range(5, 20), 3), reverse=True)
        # Ensure triangle inequality
        while s1 >= s2 + s3:
            s1, s2, s3 = sorted(random.sample(range(5, 25), 3), reverse=True)
            
        question_text = (f"在 △ABC 與 △DEF 中，若 AB=DE={s1}，BC=EF={s2}，AC=DF={s3}，"
                         f"則 △ABC 與 △DEF 是否全等？<br>若是，請說明是根據何種全等性質。"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "SSS"
    else:  # calculate
        s1, s2 = random.sample(range(5, 20), 2)
        a = random.randint(2, 5)
        b = random.randint(1, 10)
        x_sol = random.randint(2, 8)
        s3_val = a * x_sol + b
        
        sides = sorted([s1, s2, s3_val], reverse=True)
        while sides[0] >= sides[1] + sides[2]:
            s1, s2 = random.sample(range(5, 25), 2)
            s3_val = a * x_sol + b
            sides = sorted([s1, s2, s3_val], reverse=True)

        s3_expr = f"{a}x + {b}" if b > 0 else f"{a}x - {abs(b)}"
        
        question_text = (f"已知 △ABC ≅ △DEF。若 AB=DE={s1}，BC=EF={s2}，AC={s3_val} 且 DF={s3_expr}，請問 x=？")
        correct_answer = str(x_sol)
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def _generate_sas_problem():
    """Generates an SAS (Side-Angle-Side) congruence problem."""
    mode = random.choice(['identify', 'calculate', 'common_side'])
    if mode == 'identify':
        s1, s2 = random.sample(range(5, 20), 2)
        a1 = random.randint(30, 120)
        question_text = (f"在 △ABC 與 △DEF 中，若 AB=DE={s1}，∠B=∠E={a1}°，BC=EF={s2}，"
                         f"請問 △ABC 與 △DEF 是否全等？<br>若是，請說明是根據何種全等性質。"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "SAS"
    elif mode == 'calculate':
        s1 = random.randint(5, 20)
        a = random.randint(2, 5)
        b = random.randint(1, 10)
        x_sol = random.randint(2, 8)
        s2_val = a * x_sol + b
        s2_expr = f"{a}x + {b}" if b > 0 else f"{a}x - {abs(b)}"
        a1 = random.randint(30, 120)
        
        question_text = (f"已知 △ABC 與 △DEF 根據 SAS 性質全等。若 AB=DE={s1}，∠B=∠E={a1}°，"
                         f"BC={s2_val} 且 EF={s2_expr}，請問 x=？")
        correct_answer = str(x_sol)
    else:  # common_side
        s1 = random.randint(5, 20)
        a1 = random.randint(30, 120)
        question_text = (f"在 △ABD 與 △ACD 中，已知 AB=AC={s1}，且 ∠BAD=∠CAD={a1}°。"
                         f"請問 △ABD 與 △ACD 是否全等？<br>(提示：AD為共用邊)<br>若是，請說明是根據何種全等性質。"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "SAS"
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def _generate_asa_problem():
    """Generates an ASA (Angle-Side-Angle) congruence problem."""
    mode = random.choice(['identify', 'calculate', 'vertical_angle'])
    a1 = random.randint(20, 80)
    a2 = random.randint(20, 150 - a1)
    
    if mode == 'identify':
        s1 = random.randint(5, 20)
        question_text = (f"在 △ABC 與 △DEF 中，若 ∠A=∠D={a1}°，AB=DE={s1}，∠B=∠E={a2}°，"
                         f"請問 △ABC 與 △DEF 是否全等？<br>若是，請說明是根據何種全等性質。"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "ASA"
    elif mode == 'calculate':
        a = random.randint(2, 5)
        b = random.randint(1, 10)
        x_sol = random.randint(2, 8)
        s1_val = a * x_sol + b
        s1_expr = f"{a}x + {b}" if b > 0 else f"{a}x - {abs(b)}"
        
        question_text = (f"已知 △ABC 與 △DEF 根據 ASA 性質全等。若 ∠A=∠D={a1}°，∠B=∠E={a2}°，"
                         f"AB={s1_val} 且 DE={s1_expr}，請問 x=？")
        correct_answer = str(x_sol)
    else:  # vertical_angle
        s1 = random.randint(5, 20)
        question_text = (f"如圖，AC 與 BD 交於 O 點。已知 AO=CO={s1}，∠A=∠C={a1}°，且對頂角 ∠AOB=∠COD。"
                         f"請問 △ABO 與 △CDO 是否全等？<br>若是，請說明是根據何種全等性質。"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "ASA"

    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}
    
def _generate_aas_problem():
    """Generates an AAS (Angle-Angle-Side) congruence problem."""
    mode = random.choice(['identify', 'calculate'])
    a1 = random.randint(20, 80)
    a2 = random.randint(20, 150 - a1)
    
    if mode == 'identify':
        s1 = random.randint(5, 20)
        question_text = (f"在 △ABC 與 △DEF 中，若 ∠A=∠D={a1}°，∠B=∠E={a2}°，AC=DF={s1}，"
                         f"請問 △ABC 與 △DEF 是否全等？<br>若是，請說明是根據何種全等性質。"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "AAS"
    else:  # calculate
        a = random.randint(2, 5)
        b = random.randint(1, 10)
        x_sol = random.randint(2, 8)
        s1_val = a * x_sol + b
        s1_expr = f"{a}x + {b}" if b > 0 else f"{a}x - {abs(b)}"
        
        question_text = (f"已知 △ABC 與 △DEF 根據 AAS 性質全等。若 ∠A=∠D={a1}°，∠C=∠F={a2}°，"
                         f"AB={s1_val} 且 DE={s1_expr}，請問 x=？")
        correct_answer = str(x_sol)
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def _generate_rhs_problem():
    """Generates an RHS (Right-Hypotenuse-Side) congruence problem."""
    mode = random.choice(['identify', 'calculate', 'common_side'])
    if mode == 'identify':
        leg = random.randint(5, 15)
        hyp = random.randint(leg + 1, 25)
        question_text = (f"在直角 △ABC (∠B=90°) 與直角 △DEF (∠E=90°) 中，若斜邊 AC=DF={hyp}，"
                         f"且一股 AB=DE={leg}，請問兩三角形是否全等？<br>若是，請說明是根據何種全等性質。"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "RHS"
    elif mode == 'calculate':
        leg = random.randint(5, 15)
        a = random.randint(2, 5)
        b = random.randint(1, 10)
        x_sol = random.randint(2, 8)
        hyp_val = a * x_sol + b
        while hyp_val <= leg:
            x_sol += 1
            hyp_val = a * x_sol + b

        hyp_expr = f"{a}x + {b}" if b > 0 else f"{a}x - {abs(b)}"
        
        question_text = (f"已知直角 △ABC (∠B=90°) 與直角 △DEF (∠E=90°) 全等。"
                         f"若一股 BC=EF={leg}，斜邊 AC={hyp_val} 且斜邊 DF={hyp_expr}，請問 x=？")
        correct_answer = str(x_sol)
    else:  # common_side
        leg = random.randint(5, 15)
        hyp = random.randint(leg + 1, 25)
        question_text = (f"如圖，AD 垂直 BC 於 D 點，形成兩個直角三角形。若 AB=AC={hyp}，"
                         f"請問 △ADB 與 △ADC 是否全等？<br>(提示：AD為共用邊)<br>若是，請說明是根據何種全等性質。"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "RHS"
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def _generate_invalid_problem():
    """Generates a problem where congruence cannot be determined (SSA or AAA)."""
    case = random.choice(['SSA', 'AAA'])
    if case == 'SSA':
        s1, s2 = random.sample(range(5, 20), 2)
        a1 = random.randint(30, 80)
        question_text = (f"在 △ABC 與 △DEF 中，已知 AB=DE={s1}，BC=EF={s2}，且 ∠A=∠D={a1}°。"
                         f"請問 △ABC 與 △DEF 是否『必然』全等？<br>"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "不一定全等"
    else:  # AAA
        a1 = random.randint(30, 80)
        a2 = random.randint(30, 160 - a1)
        a3 = 180 - a1 - a2
        question_text = (f"在 △ABC 與 △DEF 中，已知 ∠A=∠D={a1}°，∠B=∠E={a2}°，∠C=∠F={a3}°。"
                         f"請問 △ABC 與 △DEF 是否『必然』全等？<br>"
                         f"(請填 SSS, SAS, ASA, AAS, RHS 或 '不一定全等')")
        correct_answer = "不一定全等"
        
    return {"question_text": question_text, "answer": correct_answer, "correct_answer": correct_answer}

def generate(level=1):
    """
    生成關於三角形全等性質的題目。
    """
    postulates = ['SSS', 'SAS', 'ASA', 'AAS', 'RHS', 'Invalid']
    chosen_postulate = random.choice(postulates)
    
    if chosen_postulate == 'SSS':
        return _generate_sss_problem()
    elif chosen_postulate == 'SAS':
        return _generate_sas_problem()
    elif chosen_postulate == 'ASA':
        return _generate_asa_problem()
    elif chosen_postulate == 'AAS':
        return _generate_aas_problem()
    elif chosen_postulate == 'RHS':
        return _generate_rhs_problem()
    else:  # Invalid
        return _generate_invalid_problem()
        
def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_ans = user_answer.strip().upper().replace(' ', '')
    correct_ans = correct_answer.strip().upper().replace(' ', '')
    # For comparison, also keep the original format for feedback
    correct_ans_display = correct_answer.strip()

    is_correct = False
    
    if correct_ans == "不一定全等":
        if user_ans in ["不一定全等", "不一定", "SSA", "AAA", "否", "NO", "N", "不能決定", "無法判斷", "不必然全等"]:
            is_correct = True
    elif user_ans == correct_ans:
        is_correct = True
    
    if not is_correct:
        try:
            if float(user_ans) == float(correct_ans):
                is_correct = True
        except (ValueError, TypeError):
            pass

    if is_correct:
        result_text = f"完全正確！答案是 {correct_ans_display}。"
    else:
        result_text = f"答案不正確。正確答案應為：{correct_ans_display}。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}