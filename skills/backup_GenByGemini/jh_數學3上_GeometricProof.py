import random
from fractions import Fraction

def generate(level=1):
    """
    生成「幾何證明」相關題目。
    包含：
    1. 辨識已知條件與求證結論
    2. 平行線性質證明的填充
    3. 三角形全等證明的填充
    4. 三角形相似證明的填充
    """
    problem_type = random.choice(['identify_given_prove', 'parallel_lines_proof', 'congruence_proof', 'similarity_proof'])
    
    if problem_type == 'identify_given_prove':
        return generate_identify_problem()
    elif problem_type == 'parallel_lines_proof':
        return generate_parallel_lines_proof_problem()
    elif problem_type == 'congruence_proof':
        return generate_congruence_proof_problem()
    else: # similarity_proof
        return generate_similarity_proof_problem()

def _create_fill_in_the_blank_problem(proofs):
    """Helper function to generate fill-in-the-blank proof problems."""
    selected_proof = random.choice(proofs)
    
    min_blanks = 2
    max_blanks = len(selected_proof["blanks"])
    if max_blanks > 3:
        min_blanks = 3
    if min_blanks > max_blanks:
        min_blanks = max_blanks
    num_blanks_to_create = random.randint(min_blanks, max_blanks)

    blank_keys = sorted(list(selected_proof["blanks"].keys()))
    blanks_to_use = sorted(random.sample(blank_keys, num_blanks_to_create))
    
    answers = []
    format_dict = {}
    
    for key in blank_keys:
        val = selected_proof["blanks"][key]
        if key in blanks_to_use:
            blank_marker = "( __________ )" if len(val) > 6 else "( _____ )"
            format_dict[key] = blank_marker
            answers.append(val)
        else:
            # Check if value needs math mode formatting
            if any(c in val for c in "=<>\\^°0123456789"):
                format_dict[key] = f"${val}$"
            else:
                format_dict[key] = val
                
    proof_text_list = [line.format_map(format_dict) for line in selected_proof["proof_steps"]]
    question_proof = "<br>".join(proof_text_list)
    
    instruction = selected_proof.get("instruction", "在空格內填入適當的答案。")
    
    question_text = f"{instruction}<br><b>已知：</b>{selected_proof['known']}<br><b>求證：</b>{selected_proof['prove']}<br><br>{question_proof}<br><br>請依序填入空格內的答案，並用逗號 `,` 分隔。"
    correct_answer = ",".join(answers)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_identify_problem():
    """辨識已知條件與求證結論"""
    problems = [
        {
            "statement": "四邊形 $ABCD$ 中，$OA=OC$，$OB=OD$，且 $AC \\perp BD$，說明四邊形 $ABCD$ 是菱形。",
            "given": "$OA=OC$、$OB=OD$、$AC \\perp BD$",
            "prove": "四邊形 $ABCD$ 是菱形"
        },
        {
            "statement": "$\\triangle ABC$ 中，$AB=AC$，$D$ 為 $BC$ 的中點，求證 $AD \\perp BC$。",
            "given": "$\\triangle ABC$ 中，$AB=AC$，$D$ 為 $BC$ 的中點",
            "prove": "$AD \\perp BC$"
        },
        {
            "statement": "如圖，$\\angle A$、$\\angle B$ 的兩邊分別平行，求證：$\\angle A=\\angle B$。",
            "given": "$\\angle A$、$\\angle B$ 的兩邊分別平行",
            "prove": "$\\angle A=\\angle B$"
        },
        {
            "statement": "等腰 $\\triangle ABC$ 中，$AB=AC$，且 $BD$、$CE$ 分別為 $AC$、$AB$ 上的高，求證：$BD=CE$。",
            "given": "等腰 $\\triangle ABC$ 中，$AB=AC$，$BD$、$CE$ 分別為 $AC$、$AB$ 上的高",
            "prove": "$BD=CE$"
        }
    ]
    
    selected = random.choice(problems)
    
    question_text = f"根據以下敘述，寫出「已知條件」與「求證結論」。<br><b>題目：</b>{selected['statement']}<br>（請用「已知條件：...；求證結論：...」的格式作答）"
    correct_answer = f"已知條件：{selected['given']}；求證結論：{selected['prove']}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parallel_lines_proof_problem():
    """平行線性質證明的填充題"""
    proofs = [
        {
            "known": "如圖，$\\angle A$、$\\angle B$ 的兩邊分別平行 ($AC // BE$, $AD // BF$)。",
            "prove": "$\\angle A=\\angle B$。",
            "instruction": "在空格內填入證明過程中的理由或結論。",
            "proof_steps": [
                "證明：",
                "∵$AC // BE$，",
                "∴$\\angle A=\\angle 1$ ( {BLANK_1} )，",
                "∵$AD // BF$，",
                "∴$\\angle B=\\angle 1$ ( {BLANK_2} )，",
                "故 {BLANK_3}。"
            ],
            "blanks": {
                "BLANK_1": "同位角相等",
                "BLANK_2": "同位角相等",
                "BLANK_3": "\\angle A=\\angle B"
            }
        },
        {
            "known": "如圖，$\\angle A$、$\\angle B$ 的兩邊分別平行 ($AC // BE$, $AD // BF$)。",
            "prove": "$\\angle A＋\\angle B=180^{\\circ}$。",
            "instruction": "在空格內填入證明過程中的理由或結論。",
            "proof_steps": [
                "證明：",
                "∵$AC // BE$，",
                "∴$\\angle A=\\angle 1$ ( {BLANK_1} )",
                "∵$AD // BF$，",
                "∴$\\angle 1＋\\angle B=180^{\\circ}$ ( {BLANK_2} )",
                "故 {BLANK_3}。"
            ],
            "blanks": {
                "BLANK_1": "內錯角相等",
                "BLANK_2": "同側內角互補",
                "BLANK_3": "\\angle A＋\\angle B=180^{\\circ}"
            }
        }
    ]
    return _create_fill_in_the_blank_problem(proofs)

def generate_congruence_proof_problem():
    """三角形全等證明的填充題"""
    proofs = [
        {
            "known": "如圖，等腰 $\\triangle ABC$ 中，$AB=AC$，$D$、$E$ 分別為 $AB$、$AC$ 的中點。",
            "prove": "$BE=CD$。",
            "proof_steps": [
                "證明：",
                "⑴ ∵$D$、$E$ 分別為 $AB$、$AC$ 的中點，∴$AD=\\frac{1}{2} AB$，$AE=\\frac{1}{2}$ {BLANK_1}，",
                "又 $AB=AC$，得 $AD=$ {BLANK_2}。",
                "⑵ 在 $\\triangle ABE$ 和 $\\triangle ACD$ 中，",
                "∵ {BLANK_3} ( 已知 )",
                "{BLANK_4} ( 共用角 )",
                "{BLANK_5}",
                "∴$\\triangle ABE \\cong \\triangle ACD$ ( {BLANK_6} 全等性質 )，",
                "故 $BE=CD$ ( 對應邊相等 )。"
            ],
            "blanks": {
                "BLANK_1": "AC", "BLANK_2": "AE", "BLANK_3": "AB=AC",
                "BLANK_4": "\\angle A=\\angle A", "BLANK_5": "AE=AD", "BLANK_6": "SAS"
            }
        },
        {
            "known": "如圖，四邊形 $ABCD$ 及四邊形 $AEFG$ 皆為正方形，其中 $E$ 點在 $AB$ 上。",
            "prove": "$DE=BG$。",
            "proof_steps": [
                "證明：在 $\\triangle ADE$ 和 $\\triangle ABG$ 中，",
                "∵ {BLANK_1} ( 四邊形 $AEFG$ 為正方形 )",
                "{BLANK_2} ( 四邊形 $ABCD$ 為正方形 )",
                "{BLANK_3} ( 正方形內角 )",
                "∴$\\triangle ADE \\cong \\triangle ABG$ ( {BLANK_4} 全等性質 )，",
                "故 $DE=BG$ ( 對應邊相等 )。"
            ],
            "blanks": {
                "BLANK_1": "AE=AG", "BLANK_2": "AD=AB",
                "BLANK_3": "\\angle DAE=\\angle BAG=90^{\\circ}", "BLANK_4": "SAS"
            }
        },
        {
            "known": "如圖，在正 $\\triangle ABC$ 的兩邊 $AB$、$AC$ 分別往外側作正 $\\triangle ABD$、正 $\\triangle ACE$。",
            "prove": "$BE=CD$。",
            "proof_steps": [
                "證明：⑴ ∵$\\triangle ABC$、$\\triangle ABD$、$\\triangle ACE$ 均為正三角形，",
                "∴$\\angle DAB=\\angle BAC=\\angle CAE=$ {BLANK_1} 度，得 $\\angle BAE=\\angle DAC=$ {BLANK_2} 度。",
                "⑵ 在 $\\triangle ABE$ 和 $\\triangle ADC$ 中，",
                "∵ {BLANK_3} ( $\\triangle ABD$ 為正三角形 )",
                "{BLANK_4}",
                "{BLANK_5} ( $\\triangle ACE$ 為正三角形 )",
                "∴$\\triangle ABE \\cong \\triangle ADC$ ( {BLANK_6} 全等性質 )，故 $BE=CD$ ( 對應邊相等 )。"
            ],
            "blanks": {
                "BLANK_1": "60", "BLANK_2": "120", "BLANK_3": "AB=AD",
                "BLANK_4": "\\angle BAE=\\angle DAC", "BLANK_5": "AE=AC", "BLANK_6": "SAS"
            }
        }
    ]
    return _create_fill_in_the_blank_problem(proofs)

def generate_similarity_proof_problem():
    """三角形相似證明的填充題"""
    proofs = [
        {
            "known": "如圖，長方形 $ABCD$ 中，$E$、$F$ 兩點分別在 $BC$、$CD$ 上，且 $\\angle AEF=90^{\\circ}$。",
            "prove": "$\\triangle ABE \\sim \\triangle ECF$。",
            "proof_steps": [
                "證明：⑴ ∵四邊形 $ABCD$ 為長方形，∴$\\angle B=90^{\\circ}$，在 $\\triangle ABE$ 中，$\\angle BAE＋\\angle AEB=$ {BLANK_1} $\\cdots\\cdots$①",
                "又 $\\angle AEF=90^{\\circ}$，$\\angle FEC＋\\angle AEB=$ {BLANK_2} $\\cdots\\cdots$②",
                "由①、②可得 {BLANK_3}。",
                "⑵ 在 $\\triangle ABE$ 和 $\\triangle ECF$ 中，∵ $\\angle B=\\angle C=90^{\\circ}$, {BLANK_4}",
                "∴$\\triangle ABE \\sim \\triangle ECF$ ( {BLANK_5} 相似性質 )。"
            ],
            "blanks": {
                "BLANK_1": "90^{\\circ}", "BLANK_2": "90^{\\circ}", "BLANK_3": "\\angle BAE=\\angle FEC",
                "BLANK_4": "\\angle BAE=\\angle FEC", "BLANK_5": "AA"
            }
        },
        {
            "known": "如圖，$\\triangle ABC$ 為正三角形，$P$、$Q$ 兩點分別在 $BC$、$AC$ 上，且 $\\angle APQ=60^{\\circ}$。",
            "prove": "$\\triangle ABP \\sim \\triangle PCQ$。",
            "proof_steps": [
                "證明：在 $\\triangle ABP$ 和 $\\triangle PCQ$ 中：",
                "∵ {BLANK_1} (正三角形性質)",
                "又 $\\angle APC$ 是 $\\triangle ABP$ 的一個外角，故 $\\angle APC = \\angle B + \\angle BAP$。",
                "又 $\\angle APC = \\angle APQ + \\angle CPQ$。",
                "∴ $\\angle B + \\angle BAP = \\angle APQ + \\angle CPQ$。",
                "∵ $\\angle B = 60^{\\circ}$，$\\angle APQ = 60^{\\circ}$",
                "∴ {BLANK_2}",
                "故 $\\triangle ABP \\sim \\triangle PCQ$ ( {BLANK_3} 相似性質 )。"
            ],
            "blanks": {
                "BLANK_1": "\\angle B=\\angle C=60^{\\circ}",
                "BLANK_2": "\\angle BAP=\\angle CPQ",
                "BLANK_3": "AA"
            }
        }
    ]
    return _create_fill_in_the_blank_problem(proofs)

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Normalize by removing all spaces and converting to uppercase.
    # Also handle full-width commas and colons.
    norm_user = user_answer.replace(" ", "").replace("，", ",").replace("：",":").upper()
    norm_correct = correct_answer.replace(" ", "").replace("，", ",").replace("：",":").upper()
    
    is_correct = (norm_user == norm_correct)

    # A slightly more lenient check for A=B vs B=A in fill-in-the-blanks
    if not is_correct and ',' in norm_correct:
        user_parts = norm_user.split(',')
        correct_parts = norm_correct.split(',')
        if len(user_parts) == len(correct_parts):
            all_match = True
            for u, c in zip(user_parts, correct_parts):
                if u == c:
                    continue
                # check for reversed equality
                if '=' in c:
                    sides = c.split('=')
                    if len(sides) == 2 and u == f"{sides[1]}={sides[0]}":
                        continue
                all_match = False
                break
            if all_match:
                is_correct = True
    
    # Handle the "identify" question type specifically, as it doesn't need reversal logic
    if "已知條件" in correct_answer:
        is_correct = (norm_user == norm_correct)
    
    result_text = f"完全正確！" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}