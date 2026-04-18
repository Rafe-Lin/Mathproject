import random
import math
from fractions import Fraction

# Helper function for binomial PMF
def binomial_pmf(n, k, p):
    """
    Calculates the probability P(X=k) for a binomial distribution B(n, p).
    Uses fractions for precise calculation before converting to float.
    """
    if not (0 <= k <= n):
        return Fraction(0)
    
    p_frac = Fraction(p)
    q_frac = Fraction(1) - p_frac
    
    combinations = math.comb(n, k)
    
    # Calculate (p^k) and (q^(n-k)) as Fractions
    term_p = p_frac ** k
    term_q = q_frac ** (n - k)
    
    prob_frac = Fraction(combinations) * term_p * term_q
    
    return prob_frac

def generate(level=1):
    """
    生成假設檢定 (Hypothesis Testing) 的題目。
    題目內容包含：設定假設、選擇檢定統計量、設定顯著水準，
    並要求學生找出拒絕域，以及根據試驗結果做出判斷。
    """
    
    # Determine scenario and parameters for the problem context
    scenarios = [
        {"item": "投籃球機器人", "action": "罰球命中率", "param_name": "p"},
        {"item": "火車", "action": "誤點機率", "param_name": "p"},
        {"item": "某科系新生", "action": "男女錄取比例 (女生人數比例)", "param_name": "p"}
    ]
    
    scenario = random.choice(scenarios)
    item = scenario["item"]
    action = scenario["action"]
    param_name = scenario["param_name"]

    # Number of trials (n) for the binomial distribution
    # Keeping n in a manageable range for manual probability calculation if needed
    n = random.randint(6, 10) 

    # Hypothesized probability (p0)
    # Using fractions for precise calculation with binomial PMF
    p0_options = [Fraction(1, 2), Fraction(1, 4), Fraction(1, 5), Fraction(1, 10), Fraction(3, 4), Fraction(2, 5)]
    p0 = random.choice(p0_options)
    
    # Significance level (alpha)
    alpha = random.choice([0.05, 0.01])

    # Determine the type of hypothesis test (one-sided only for simplicity, as per examples)
    # 'lower_tail': H0: p >= p0 (reject if X is small), H1: p < p0
    # 'upper_tail': H0: p <= p0 (reject if X is large), H1: p > p0
    hypothesis_type = random.choice(['lower_tail', 'upper_tail'])

    # Construct the H0 statement for display
    h0_statement_display = ""
    if hypothesis_type == 'lower_tail':
        h0_statement_display = f"${param_name} \\ge {p0}$"
    else: # upper_tail
        h0_statement_display = f"${param_name} \\le {p0}$"
        
    # Description of the test statistic
    test_statistic_desc = f"隨機觀察{n}次（或{n}名），統計成功（或特定事件發生）的次數（或人數）"
    
    # Calculate the rejection region
    rejection_region_list = []
    
    if hypothesis_type == 'lower_tail':
        cumulative_prob = Fraction(0)
        for k in range(n + 1):
            prob_k = binomial_pmf(n, k, p0)
            cumulative_prob += prob_k
            # If the cumulative probability is less than alpha, k is in the rejection region
            if float(cumulative_prob) < alpha:
                rejection_region_list.append(k)
            else:
                # Stop when cumulative probability exceeds or equals alpha
                break
    else: # upper_tail
        cumulative_prob = Fraction(0)
        # Iterate from n down to 0 to find the upper tail
        for k in range(n, -1, -1): 
            prob_k = binomial_pmf(n, k, p0)
            cumulative_prob += prob_k
            # If the cumulative probability from the upper tail is less than alpha, k is in the rejection region
            if float(cumulative_prob) < alpha:
                rejection_region_list.insert(0, k) # Insert at beginning to keep the list sorted
            else:
                break
    
    # Format the rejection region string for output
    if not rejection_region_list:
        rejection_region_str = "無" # "None" if no region is found
    else:
        # Use raw string for LaTeX braces to avoid f-string parsing issues with backslashes
        rejection_region_str = r"$\{$" + ", ".join(map(str, rejection_region_list)) + r"$\}$"

    # Generate an observed result for the experiment
    observed_x = random.randint(0, n)
    
    # Determine the decision based on the observed result and rejection region
    decision_text = ""
    if observed_x in rejection_region_list:
        decision_text = r"拒絕 $\text{H}_0$"
    else:
        decision_text = r"不拒絕 $\text{H}_0$"

    # Construct the question text using f-strings and LaTeX
    question_text = (
        f"題目: 某{item}宣稱其{action} {h0_statement_display}。今檢定此{item}的{action}，並列出前三個步驟如下：<br>"
        f"①假設「{item}的{action} {h0_statement_display}」；<br>"
        f"②確立檢定統計量為「{test_statistic_desc}」；<br>"
        f"③設定顯著水準為 ${alpha}$。<br><br>"
        f"回答下列問題。<br><br>"
        f"$1$ 設隨機變數 $X$ 表示成功次數，求拒絕域。<br><br>"
        f"$2$ 若試驗的結果為成功 ${observed_x}$ 次，則是否拒絕「{item}的{action} {h0_statement_display}」的假設？"
    )
    
    correct_answer_part1 = rejection_region_str
    correct_answer_part2 = decision_text
    
    # Store the answers for internal checking and display
    return {
        "question_text": question_text,
        "answer": (correct_answer_part1, correct_answer_part2), # Tuple for robust internal checking
        "correct_answer": f"1. {correct_answer_part1}<br>2. {correct_answer_part2}" # Formatted for display
    }

def _normalize_region(text):
    """
    Normalizes the input string for the rejection region to a canonical format.
    Handles LaTeX braces, spaces, and the "無" (none) case.
    """
    text = text.replace(r"$\{$", "{").replace(r"$\}$", "}").replace("$", "").strip()
    if text.upper() == "無":
        return "無"
    text = text.strip('{}').replace(" ", "")
    if not text: # Treat empty string after stripping as "無"
        return "無"
    
    try:
        elements = sorted(map(int, text.split(',')))
        return "{" + ",".join(map(str, elements)) + "}"
    except ValueError:
        return "INVALID_REGION" # Indicate parsing failure

def _normalize_decision(text):
    """
    Normalizes the input string for the decision (reject/not reject H0) to a canonical format.
    Handles LaTeX `\text{H}_0`, spaces, and case insensitivity.
    """
    text = text.replace("$", "").replace(r"\text{H}_0", "H0").strip().upper()
    if "拒絕" in text and "不" not in text: # Catches "拒絕H0", "拒絕 H0" etc.
        return "拒絕H0"
    if "不拒絕" in text: # Catches "不拒絕H0", "不拒絕 H0" etc.
        return "不拒絕H0"
    return "UNKNOWN_DECISION"

def check(user_answer, correct_answer):
    """
    檢查使用者答案是否正確。
    user_answer 預期為一個字串，包含兩部分的答案，可能由 '<br>', ';', 或 '\n' 分隔。
    correct_answer 為一個元組 (rejection_region_str, decision_str)。
    """
    
    correct_ans_part1_raw, correct_ans_part2_raw = correct_answer
    
    # Normalize correct answers to a canonical form for robust comparison
    norm_correct_part1 = _normalize_region(correct_ans_part1_raw)
    norm_correct_part2 = _normalize_decision(correct_ans_part2_raw)

    parsed_user_ans_part1_norm = "UNKNOWN_REGION"
    parsed_user_ans_part2_norm = "UNKNOWN_DECISION"

    # Attempt to split user answer by common delimiters
    user_ans_parts_raw = []
    
    # Prioritize splitting by <br>, then ;, then \n
    temp_parts = [p.strip() for p in user_answer.split('<br>') if p.strip()]
    if len(temp_parts) < 2:
        temp_parts = [p.strip() for p in user_answer.split(';') if p.strip()]
    if len(temp_parts) < 2:
        temp_parts = [p.strip() for p in user_answer.split('\n') if p.strip()]
        
    user_ans_parts_raw = temp_parts
        
    part1_candidate = ""
    part2_candidate = ""

    # Heuristic parsing to identify which part is which
    for part in user_ans_parts_raw:
        if part.startswith("1."):
            part1_candidate = part[2:].strip()
        elif part.startswith("2."):
            part2_candidate = part[2:].strip()
        elif "{" in part or "無" in part or "NULL" in part.upper(): # Likely a rejection region
            if not part1_candidate: 
                part1_candidate = part
        elif ("拒絕" in part or "不拒絕" in part): # Likely a decision
            if not part2_candidate:
                part2_candidate = part
    
    # Normalize the parsed user parts
    parsed_user_ans_part1_norm = _normalize_region(part1_candidate) if part1_candidate else "UNKNOWN_REGION"
    parsed_user_ans_part2_norm = _normalize_decision(part2_candidate) if part2_candidate else "UNKNOWN_DECISION"

    # Compare normalized answers
    is_part1_correct = (parsed_user_ans_part1_norm == norm_correct_part1)
    is_part2_correct = (parsed_user_ans_part2_norm == norm_correct_part2)

    is_correct = is_part1_correct and is_part2_correct
    
    feedback_parts = []
    if not is_part1_correct:
        feedback_parts.append(f"第1題答案不正確。正確答案應為：{correct_ans_part1_raw}")
    if not is_part2_correct:
        feedback_parts.append(f"第2題答案不正確。正確答案應為：{correct_ans_part2_raw}")

    if is_correct:
        result_text = f"完全正確！答案是：<br>1. {correct_ans_part1_raw}<br>2. {correct_ans_part2_raw}"
    else:
        # Provide specific feedback if parts are incorrect, otherwise general parsing advice
        if not feedback_parts: 
            result_text = f"你的答案格式似乎不正確，或無法解析。請嘗試類似 '1. {{0,1}}<br>2. 不拒絕 H0' 的格式。<br>正確答案應為：<br>1. {correct_ans_part1_raw}<br>2. {correct_ans_part2_raw}"
        else:
            result_text = "<br>".join(feedback_parts) + f"<br><br>正確答案應為：<br>1. {correct_ans_part1_raw}<br>2. {correct_ans_part2_raw}"

    return {"correct": is_correct, "result": result_text, "next_question": True}