import random
from fractions import Fraction
import re

def remove_latex_math(text):
    """Removes LaTeX math delimiters $...$ from a string for internal comparison."""
    # This regex handles cases where $...$ might contain special chars that need escaping
    return re.sub(r'\$(.*?)\$', r'\1', text)

def generate(level=1):
    """
    生成「機率定義回顧與性質」相關題目。
    包含：
    1. 區分三種機率定義（古典、統計頻率、主觀）
    2. 判斷機率基本性質的正確性
    3. 統計頻率機率的簡單計算
    """
    problem_type = random.choice([
        'identify_probability_type',
        'property_check_multiple_choice',
        'frequentist_calculation'
    ])

    if problem_type == 'identify_probability_type':
        return generate_identify_probability_type_problem()
    elif problem_type == 'property_check_multiple_choice':
        return generate_property_check_multiple_choice_problem()
    elif problem_type == 'frequentist_calculation':
        return generate_frequentist_calculation_problem()

def generate_identify_probability_type_problem():
    """
    生成識別機率類型的問題。
    題目會描述一個情境，要求學生判斷其屬於古典機率、統計頻率客觀機率或主觀機率。
    """
    scenarios = [
        # (question_text, correct_type_keyword)
        (r"投擲一枚公正的硬幣，出現正面的機率是多少？", "古典機率"),
        (r"從一副洗好的撲克牌中抽取一張，抽到紅心K的機率是多少？", "古典機率"),
        (r"一個袋子裡有3個紅球和2個藍球，隨機抽取一個是紅球的機率是多少？", "古典機率"),
        (r"在一次射擊比賽中，某射手射擊100發，命中80發。他接下來一發命中的機率估計是多少？", "統計頻率客觀機率"),
        (r"某工廠在生產了1000個燈泡後，發現其中有5個是壞的。下一個生產的燈泡是壞的機率是多少？", "統計頻率客觀機率"),
        (r"根據過去20年的氣象資料，某地在7月15日下雨的頻率是每年50%。明年7月15日下雨的機率是多少？", "統計頻率客觀機率"),
        (r"某位投資者認為，他購買的股票明天會上漲的機率是70%。", "主觀機率"),
        (r"你覺得今天遇到老同學的機率有多大？", "主觀機率"),
        (r"一位醫生評估某病人手術成功的機率是95%。", "主觀機率")
    ]
    question_template, correct_type = random.choice(scenarios)

    question_text = f"以下情境屬於哪一種機率定義？請從「古典機率」、「統計頻率客觀機率」或「主觀機率」中選一個作答。<br><br>{question_template}"
    
    return {
        "question_text": question_text,
        "answer": correct_type,
        "correct_answer": correct_type
    }

def generate_property_check_multiple_choice_problem():
    """
    生成判斷機率基本性質的題目。
    題目包含多個陳述，學生需選出所有正確的選項。
    """
    all_statements = [
        # (statement_text, is_correct)
        (r"任何事件發生的機率 $P(A)$ 總是在 $0$ 到 $1$ 之間（包含 $0$ 和 $1$）。", True),
        (r"一件不可能發生的事件，其機率為 $0$。", True),
        (r"一件必然發生的事件，其機率為 $1$。", True),
        (r"如果某事件 $A$ 的機率為 $P(A)$，則其補集事件 $A'$ （$A$ 不發生）的機率 $P(A')$ 為 $1 - P(A)$。", True),
        (r"所有可能結果的機率總和必定等於 $1$。", True),
        (r"某人預測下週股票上漲的機率為 $1.2$，這是合理的判斷。", False),
        (r"某人估計今天下雨的機率為 $40\\%$，不下雨的機率為 $70\\%$，這是不合理的判斷。", True),
        (r"某投手投球100次，其中有60次好球。這表示他接下來的10次投球中，一定會有6次好球。", False),
        (r"機率可以用百分之兩百來表示，只要信念足夠。", False),
        (r"機率值可以是負數。", False),
        (r"古典機率的計算前提是每個基本事件發生的可能性都相等。", True),
        (r"統計頻率的客觀機率需要透過大量重複實驗或觀察數據來估計。", True),
        (r"主觀機率是一種基於個人信念或經驗的機率，即使數據不足也可以形成。", True),
        (r"只要事件發生的次數夠多，統計頻率機率會越接近理論上的真實機率。", True)
    ]

    # Randomly select a subset of statements
    num_statements = random.randint(3, 5)
    selected_statements_with_truth = random.sample(all_statements, num_statements)

    question_parts = [r"請選出所有正確的選項。"]
    correct_options = []
    
    for i, (statement, is_correct) in enumerate(selected_statements_with_truth):
        question_parts.append(f"({i+1}) {statement}")
        if is_correct:
            correct_options.append(str(i+1))

    question_text = "<br>".join(question_parts)
    
    # If no options are correct, the answer is "None"
    correct_answer_str = " ".join(correct_options) if correct_options else "None"

    return {
        "question_text": question_text,
        "answer": correct_answer_str, 
        "correct_answer": correct_answer_str
    }

def generate_frequentist_calculation_problem():
    """
    生成統計頻率客觀機率的簡單計算問題。
    題目給出實驗次數和事件發生次數，要求計算機率。
    """
    event_name = random.choice(["命中率", "良率", "成功率", "出現正面機率", "特定候選人支持率"])
    num_trials = random.randint(50, 200) * 10 # 500 to 2000 trials
    
    # Ensure a reasonable probability (not 0 or 1 unless specifically intended)
    num_successes_min = int(num_trials * 0.1)
    num_successes_max = int(num_trials * 0.9)
    # Handle cases where num_trials is very small (though not expected with current range)
    if num_successes_min >= num_successes_max:
        num_successes = random.randint(1, num_trials - 1) if num_trials > 1 else 1
    else:
        num_successes = random.randint(num_successes_min, num_successes_max)
    
    prob_fraction = Fraction(num_successes, num_trials)
    
    # Decide whether to ask for fraction, decimal, or percentage
    answer_format = random.choice(['fraction', 'decimal', 'percentage'])
    
    question_text_base = f"某項實驗或觀察進行了 ${num_trials}$ 次，其中某事件發生了 ${num_successes}$ 次。根據統計頻率，該事件發生的機率為何？"
    
    if event_name == "命中率":
        question_text_base = f"某射手進行射擊練習，射擊了 ${num_trials}$ 發，其中命中 ${num_successes}$ 發。根據此數據，估計該射手的命中率是多少？"
    elif event_name == "良率":
        question_text_base = f"某工廠生產了 ${num_trials}$ 個產品，經檢測發現有 ${num_successes}$ 個是良品。根據此數據，估計該產品的良率是多少？"
    elif event_name == "成功率":
        question_text_base = f"某項實驗重複進行了 ${num_trials}$ 次，其中有 ${num_successes}$ 次獲得成功。根據此數據，估計該實驗的成功率是多少？"
    elif event_name == "出現正面機率":
        question_text_base = f"小明投擲一枚硬幣 ${num_trials}$ 次，其中出現正面 ${num_successes}$ 次。根據此數據，估計硬幣出現正面的機率是多少？"
    elif event_name == "特定候選人支持率":
        question_text_base = f"某項民意調查隨機訪問了 ${num_trials}$ 位選民，其中有 ${num_successes}$ 位表示支持A候選人。根據此數據，估計A候選人的支持率是多少？"

    correct_answer_str = ""
    if answer_format == 'fraction':
        correct_answer_str = f"$\\frac{{{prob_fraction.numerator}}}{{{prob_fraction.denominator}}}$"
        question_text = f"{question_text_base} (請以最簡分數表示)"
    elif answer_format == 'decimal':
        prob_decimal = round(float(prob_fraction), 3) # Round to 3 decimal places
        correct_answer_str = str(prob_decimal)
        question_text = f"{question_text_base} (請四捨五入到小數點後三位)"
    else: # percentage
        prob_percentage = round(float(prob_fraction) * 100, 1) # Round to one decimal place for percentage
        correct_answer_str = f"{prob_percentage}\\%"
        question_text = f"{question_text_base} (請以百分比表示，四捨五入到小數點後一位)"

    return {
        "question_text": question_text,
        "answer": correct_answer_str,
        "correct_answer": correct_answer_str
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_stripped = user_answer.strip()
    correct_answer_stripped = correct_answer.strip()

    # Remove LaTeX math delimiters from the correct answer for internal comparison
    correct_answer_for_comp = remove_latex_math(correct_answer_stripped)
    user_answer_for_comp = remove_latex_math(user_answer_stripped) # Assume user doesn't use LaTeX usually

    is_correct = False

    # Case 1: Multiple choice (space-separated numbers or "None")
    if ' ' in correct_answer_for_comp or correct_answer_for_comp.lower() == 'none':
        user_parts = set(user_answer_for_comp.upper().split())
        correct_parts = set(correct_answer_for_comp.upper().split())
        is_correct = (user_parts == correct_parts)
    else:
        # Case 2: Numerical answer (fraction, decimal, percentage) or keyword
        # Try to convert both to Fraction or float for robust numerical comparison
        
        user_val_str = user_answer_for_comp.replace('%', '')
        correct_val_str = correct_answer_for_comp.replace('%', '')

        try:
            # Attempt float comparison (handling percentages as float values)
            # Use Fraction for parsing if '/' is present, then convert to float
            user_float = float(Fraction(user_val_str)) if '/' in user_val_str else float(user_val_str)
            correct_float = float(Fraction(correct_val_str)) if '/' in correct_val_str else float(correct_val_str)
            
            # Adjust for percentage if '%' was present in original string
            if '%' in user_answer_for_comp: user_float /= 100.0
            if '%' in correct_answer_for_comp: correct_float /= 100.0

            is_correct = abs(user_float - correct_float) < 1e-6

        except (ValueError, ZeroDivisionError):
            # If float/Fraction conversion fails (e.g., text answer like '古典機率'), do string comparison
            # Using .upper() for case-insensitivity
            is_correct = (user_answer_for_comp.upper() == correct_answer_for_comp.upper())
            
    result_text = f"完全正確！答案是 ${correct_answer_stripped}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_stripped}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}