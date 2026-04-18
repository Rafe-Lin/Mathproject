import random
from fractions import Fraction
import re

def format_event_set(event_set):
    """
    Formats a Python set of tuples into a LaTeX-friendly string representation,
    e.g., {(1,2),(3,4)} or \emptyset.
    Elements within tuples are formatted without spaces (e.g., (1,2) instead of (1, 2)).
    """
    if not event_set:
        return r"\emptyset"
    
    # Sort for consistent output. Sorting tuples works lexicographically.
    sorted_elements = sorted(list(event_set))
    
    formatted_tuples = []
    for element in sorted_elements:
        if isinstance(element, tuple) and len(element) == 2:
            # Manually format (val1,val2) to ensure no space, like "(1,2)"
            formatted_tuples.append(f"({element[0]},{element[1]})")
        else:
            # Fallback for unexpected elements, though not expected for this skill
            formatted_tuples.append(str(element))
            
    return f"{{{','.join(formatted_tuples)}}}"

def parse_event_set(s):
    """
    Parses a string representation of a set (e.g., '{(1,2),(3,4)}', '{ (正 , 反), (反 , 正) }')
    into a Python set of tuples (e.g., {(1,2), (3,4)}, {("正","反"), ("反","正")}).
    Handles various spacing and empty set representations.
    """
    s = s.strip().replace(' ', '') # Remove all spaces for easier parsing
    if s == r"\emptyset" or s == "{}" or s == "∅": # Handle empty set representations
        return set()

    s_content = s.strip('{}') # Remove outer braces
    if not s_content: # If only braces or empty after stripping
        return set()

    elements = set()
    # Regex to find all (item1,item2) patterns.
    # It specifically looks for content inside parentheses.
    tuple_strings = re.findall(r'\(([^)]*)\)', s_content)
    
    for ts in tuple_strings:
        parts = [p.strip() for p in ts.split(',')]
        if len(parts) == 2:
            try:
                # Try converting to int for numerical elements (e.g., dice rolls)
                val1 = int(parts[0])
                val2 = int(parts[1])
                elements.add((val1, val2))
            except ValueError:
                # If not integers, treat as strings (e.g., for coin flips "正", "反")
                elements.add((parts[0], parts[1]))
    return elements

def generate_two_dice_problem(level):
    """Generates a probability problem based on two dice rolls."""
    S = {(x, y) for x in range(1, 7) for y in range(1, 7)}
    
    event_funcs = []
    event_descs = []

    # Define various types of events for two dice
    
    # Type 1: Sum of points
    sum_val_eq = random.randint(5, 10)
    event_funcs.append(lambda s: {(x, y) for x, y in s if x + y == sum_val_eq})
    event_descs.append(f"甲、乙兩人擲出的點數和為 ${sum_val_eq}$ 的事件")

    sum_op = random.choice(['>', '<'])
    sum_val_ineq = random.randint(7, 9)
    if sum_op == '>':
        event_funcs.append(lambda s: {(x, y) for x, y in s if x + y > sum_val_ineq})
        event_descs.append(f"甲、乙兩人擲出的點數和大於 ${sum_val_ineq}$ 的事件")
    else: # sum_op == '<'
        event_funcs.append(lambda s: {(x, y) for x, y in s if x + y < sum_val_ineq})
        event_descs.append(f"甲、乙兩人擲出的點數和小於 ${sum_val_ineq}$ 的事件")

    # Type 2: Same points
    event_funcs.append(lambda s: {(x, y) for x, y in s if x == y})
    event_descs.append("甲、乙擲出相同點數的事件")

    # Type 3: First die / Second die specific value
    first_die_val = random.randint(1, 6)
    event_funcs.append(lambda s: {(x, y) for x, y in s if x == first_die_val})
    event_descs.append(f"甲擲出 ${first_die_val}$ 點的事件")
    
    second_die_val = random.randint(1, 6)
    event_funcs.append(lambda s: {(x, y) for x, y in s if y == second_die_val})
    event_descs.append(f"乙擲出 ${second_die_val}$ 點的事件")

    # Type 4: Product of points
    product_options = [6, 8, 12, 18, 24, 36] # Common products with multiple combinations
    prod_val = random.choice(product_options)
    event_funcs.append(lambda s: {(x, y) for x, y in s if x * y == prod_val})
    event_descs.append(f"甲、乙擲出點數積為 ${prod_val}$ 的事件")

    # Select two distinct events for A and B to ensure variety
    idx1, idx2 = random.sample(range(len(event_funcs)), 2)
    
    event_A = event_funcs[idx1](S)
    event_B = event_funcs[idx2](S)
    
    desc_A = event_descs[idx1]
    desc_B = event_descs[idx2]

    # Decide what question to ask
    question_options = ["list_A_B", "intersect", "union"]
    if level >= 2: # Introduce complement and mutually exclusive at higher difficulty levels
        question_options.append("complement_A")
        question_options.append("mutually_exclusive")
    
    q_type = random.choice(question_options)
    
    question_text_base = f"甲、乙兩人各擲一粒骰子一次。設 $A$ 表示{desc_A}；$B$ 表示{desc_B}。"
    solution_steps = []
    
    # Prepend common solution setup
    solution_steps.append(f"設序對 $(x,y)$ 表示甲擲出 $x$ 點、乙擲出 $y$ 點。")
    
    if q_type == "list_A_B":
        question_text = f"{question_text_base}<br>(1) 用集合表示事件 $A$ 與事件 $B$。"
        # User needs to provide both. Format: A={...},B={...}
        correct_answer = f"A={format_event_set(event_A)},B={format_event_set(event_B)}"
        
        solution_steps.append(f"因為 $A$ 表示{desc_A}，所以 $A={format_event_set(event_A)}$。")
        solution_steps.append(f"因為 $B$ 表示{desc_B}，所以 $B={format_event_set(event_B)}$。")
        
    elif q_type == "intersect":
        event_intersect = event_A.intersection(event_B)
        question_text = f"{question_text_base}<br>寫出 $A$ 與 $B$ 同時發生的事件。"
        correct_answer = format_event_set(event_intersect)

        solution_steps.append(f"事件 $A={format_event_set(event_A)}$。")
        solution_steps.append(f"事件 $B={format_event_set(event_B)}$。")
        solution_steps.append(f" $A$ 與 $B$ 同時發生的事件 $A \\cap B = {format_event_set(event_intersect)}$。")
        
    elif q_type == "union":
        event_union = event_A.union(event_B)
        question_text = f"{question_text_base}<br>寫出事件 $A \\cup B$。"
        correct_answer = format_event_set(event_union)

        solution_steps.append(f"事件 $A={format_event_set(event_A)}$。")
        solution_steps.append(f"事件 $B={format_event_set(event_B)}$。")
        solution_steps.append(f" $A \\cup B = {format_event_set(event_union)}$。")

    elif q_type == "complement_A":
        event_complement_A = S - event_A
        question_text = f"{question_text_base}<br>寫出事件 $A$ 不發生的事件。"
        correct_answer = format_event_set(event_complement_A)

        solution_steps.append(f"樣本空間 $S={format_event_set(S)}$。")
        solution_steps.append(f"事件 $A={format_event_set(event_A)}$。")
        solution_steps.append(f" $A$ 不發生的事件 $A' = S - A = {format_event_set(event_complement_A)}$。")

    elif q_type == "mutually_exclusive":
        event_intersect = event_A.intersection(event_B)
        is_mutually_exclusive = (len(event_intersect) == 0)
        
        question_text = f"{question_text_base}<br>事件 $A$ 與 $B$ 是否為互斥事件？(請回答 是/否)"
        correct_answer = "是" if is_mutually_exclusive else "否" # Non-LaTeX for Yes/No answer

        solution_steps.append(f"事件 $A={format_event_set(event_A)}$。")
        solution_steps.append(f"事件 $B={format_event_set(event_B)}$。")
        solution_steps.append(f"事件 $A \\cap B = {format_event_set(event_intersect)}$。")
        if is_mutually_exclusive:
            solution_steps.append(f"因為 $A \\cap B = \\emptyset$，所以 $A$ 與 $B$ 為互斥事件。")
        else:
            solution_steps.append(f"因為 $A \\cap B \\neq \\emptyset$，所以 $A$ 與 $B$ 不為互斥事件。")
        
    return {
        "question_text": question_text,
        "answer": correct_answer, # The expected answer for user submission
        "correct_answer": correct_answer, # Store the same for internal checking
        "solution": "<br>".join(solution_steps) # Detailed solution steps
    }

def generate_two_coins_problem(level):
    """Generates a probability problem based on two coin flips."""
    # Define sample space using strings for "正" (Heads) and "反" (Tails)
    S = {("正", "正"), ("正", "反"), ("反", "正"), ("反", "反")}
    
    event_funcs = []
    event_descs = []

    # Define various types of events for two coin flips
    
    # Type 1: Exactly one 正
    event_funcs.append(lambda s: {("正", "反"), ("反", "正")})
    event_descs.append("恰好出現一次正面的事件")

    # Type 2: Two 反
    event_funcs.append(lambda s: {("反", "反")})
    event_descs.append("出現兩次反面的事件")

    # Type 3: At least one 正
    event_funcs.append(lambda s: {("正", "正"), ("正", "反"), ("反", "正")})
    event_descs.append("至少出現一次正面的事件")

    # Type 4: Two 正
    event_funcs.append(lambda s: {("正", "正")})
    event_descs.append("出現兩次正面的事件")
    
    # Type 5: At least one 反
    event_funcs.append(lambda s: {("正", "反"), ("反", "正"), ("反", "反")})
    event_descs.append("至少出現一次反面的事件")

    # Select two distinct events for A and B
    idx1, idx2 = random.sample(range(len(event_funcs)), 2)
    
    event_A = event_funcs[idx1](S)
    event_B = event_funcs[idx2](S)
    
    desc_A = event_descs[idx1]
    desc_B = event_descs[idx2]

    # Decide what question to ask
    question_options = ["list_A_B", "intersect", "union"]
    if level >= 2:
        question_options.append("complement_A")
        question_options.append("mutually_exclusive")
    
    q_type = random.choice(question_options)
    
    question_text_base = f"丟一枚硬幣二次，觀察每次出現的是正面或反面。設 $A$ 表示{desc_A}，$B$ 表示{desc_B}。"
    solution_steps = []
    
    # Prepend common solution setup
    solution_steps.append(f"設 $( , )$ 代表依次丟出的結果，則樣本空間 $S={format_event_set(S)}$。")

    if q_type == "list_A_B":
        question_text = f"{question_text_base}<br>(1) 用集合表示事件 $A$ 與事件 $B$。"
        correct_answer = f"A={format_event_set(event_A)},B={format_event_set(event_B)}"
        
        solution_steps.append(f"因為 $A$ 表示{desc_A}，所以 $A={format_event_set(event_A)}$。")
        solution_steps.append(f"因為 $B$ 表示{desc_B}，所以 $B={format_event_set(event_B)}$。")

    elif q_type == "intersect":
        event_intersect = event_A.intersection(event_B)
        question_text = f"{question_text_base}<br>寫出 $A$ 與 $B$ 同時發生的事件。"
        correct_answer = format_event_set(event_intersect)

        solution_steps.append(f"事件 $A={format_event_set(event_A)}$。")
        solution_steps.append(f"事件 $B={format_event_set(event_B)}$。")
        solution_steps.append(f" $A$ 與 $B$ 同時發生的事件 $A \\cap B = {format_event_set(event_intersect)}$。")
        
    elif q_type == "union":
        event_union = event_A.union(event_B)
        question_text = f"{question_text_base}<br>寫出事件 $A \\cup B$。"
        correct_answer = format_event_set(event_union)

        solution_steps.append(f"事件 $A={format_event_set(event_A)}$。")
        solution_steps.append(f"事件 $B={format_event_set(event_B)}$。")
        solution_steps.append(f" $A \\cup B = {format_event_set(event_union)}$。")

    elif q_type == "complement_A":
        event_complement_A = S - event_A
        question_text = f"{question_text_base}<br>寫出事件 $A$ 不發生的事件。"
        correct_answer = format_event_set(event_complement_A)

        solution_steps.append(f"事件 $A={format_event_set(event_A)}$。")
        solution_steps.append(f" $A$ 不發生的事件 $A' = S - A = {format_event_set(event_complement_A)}$。")

    elif q_type == "mutually_exclusive":
        event_intersect = event_A.intersection(event_B)
        is_mutually_exclusive = (len(event_intersect) == 0)
        
        question_text = f"{question_text_base}<br>事件 $A$ 與 $B$ 是否為互斥事件？(請回答 是/否)"
        correct_answer = "是" if is_mutually_exclusive else "否"
        
        solution_steps.append(f"事件 $A={format_event_set(event_A)}$。")
        solution_steps.append(f"事件 $B={format_event_set(event_B)}$。")
        solution_steps.append(f"事件 $A \\cap B = {format_event_set(event_intersect)}$。")
        if is_mutually_exclusive:
            solution_steps.append(f"因為 $A \\cap B = \\emptyset$，所以 $A$ 與 $B$ 為互斥事件。")
        else:
            solution_steps.append(f"因為 $A \\cap B \\neq \\emptyset$，所以 $A$ 與 $B$ 不為互斥事件。")
            
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
        "solution": "<br>".join(solution_steps)
    }

def generate(level=1):
    """
    Generates a problem related to probability events and set operations.
    Problems involve scenarios like rolling two dice or flipping two coins.
    """
    scenario = random.choice(['two_dice', 'two_coins'])
    
    if scenario == 'two_dice':
        return generate_two_dice_problem(level)
    elif scenario == 'two_coins':
        return generate_two_coins_problem(level)

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct for event-related problems.
    Handles '是'/'否' answers and set-based answers (including A={...},B={...} format).
    """
    user_answer_stripped = user_answer.strip()
    correct_answer_stripped = correct_answer.strip()

    # Case 1: '是'/'否' answers for mutually exclusive questions
    if correct_answer_stripped in ["是", "否"]:
        is_correct = (user_answer_stripped.upper() == correct_answer_stripped.upper())
        result_text = f"完全正確！答案是 {correct_answer_stripped}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer_stripped}"
        return {"correct": is_correct, "result": result_text, "next_question": True}

    # Case 2: A={...},B={...} format for questions asking to list multiple events
    if "A={" in correct_answer_stripped and "B={" in correct_answer_stripped:
        try:
            # Extract correct sets using regex (insensitive to spacing outside braces)
            match_correct_A = re.search(r"A=(\{[^}]*\})", correct_answer_stripped)
            match_correct_B = re.search(r"B=(\{[^}]*\})", correct_answer_stripped)
            
            # These should always succeed for our generated correct_answer
            correct_A_set = parse_event_set(match_correct_A.group(1))
            correct_B_set = parse_event_set(match_correct_B.group(1))
            
            # Extract user sets (more flexible for user input by removing spaces first)
            user_answer_norm = user_answer_stripped.replace(' ', '') 
            match_user_A = re.search(r"A=(\{[^}]*\})", user_answer_norm)
            match_user_B = re.search(r"B=(\{[^}]*\})", user_answer_norm)

            if match_user_A and match_user_B:
                user_A_set = parse_event_set(match_user_A.group(1))
                user_B_set = parse_event_set(match_user_B.group(1))
                
                is_correct = (user_A_set == correct_A_set) and (user_B_set == correct_B_set)
                result_text = f"完全正確！" if is_correct else f"答案不正確。正確答案應為：${correct_answer_stripped}$"
                return {"correct": is_correct, "result": result_text, "next_question": True}
            else:
                # User input did not match A={...},B={...} pattern
                result_text = f"答案格式不正確。請確認輸入為 $A={{\\dots}}, B={{\\dots}}$ 的形式。正確答案應為：${correct_answer_stripped}$"
                return {"correct": False, "result": result_text, "next_question": True}

        except Exception as e:
            # Catch parsing errors for user input
            result_text = f"處理答案時發生錯誤: {e}。請確認輸入格式與題意相符。正確答案應為：${correct_answer_stripped}$"
            return {"correct": False, "result": result_text, "next_question": True}
    
    # Case 3: Single set answer (e.g., A union B, A complement)
    try:
        parsed_user_set = parse_event_set(user_answer_stripped)
        parsed_correct_set = parse_event_set(correct_answer_stripped)
        
        is_correct = (parsed_user_set == parsed_correct_set)
        
        result_text = f"完全正確！答案是 ${correct_answer_stripped}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_stripped}$"
        return {"correct": is_correct, "result": result_text, "next_question": True}
    except Exception as e:
        # Catch parsing errors for user input
        result_text = f"處理答案時發生錯誤: {e}。請確認輸入格式與題意相符。正確答案應為：${correct_answer_stripped}$"
        return {"correct": False, "result": result_text, "next_question": True}