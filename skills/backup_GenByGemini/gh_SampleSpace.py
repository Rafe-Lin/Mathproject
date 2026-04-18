import random
import itertools
from fractions import Fraction

# Helper function to format the sample space into a canonical string
def format_sample_space_string(sample_space_elements):
    """
    Formats a list of sample space elements into a canonical string representation.
    Elements can be integers or tuples.
    Example:
    - [0, 1, 2] -> "{0,1,2}"
    - [('正', '正'), ('正', '反')] -> "{(正,正),(正,反)}" (sorted)
    """
    if not sample_space_elements:
        return "{}"

    str_elements = []
    for item in sample_space_elements:
        if isinstance(item, tuple):
            # Convert tuple elements to string, then join, then wrap in parentheses
            str_item_parts = [str(x) for x in item]
            str_elements.append(f"({','.join(str_item_parts)})")
        else:
            str_elements.append(str(item))

    # Sort the string representations for consistent output
    str_elements.sort()

    return f"{{{','.join(str_elements)}}}"

def generate(level=1):
    """
    生成「樣本空間」相關題目。
    包含：
    1. 硬幣投擲 (觀察序列或計數)
    2. 物品抽選 (有/無放回, 考慮/不考慮順序)
    """
    problem_type = random.choice([
        'coin_toss_sequence', 
        'coin_toss_count', 
        'card_draw_no_replacement_ordered', 
        'card_draw_no_replacement_unordered',
        'card_draw_with_replacement_ordered'
    ])
    
    if problem_type == 'coin_toss_sequence':
        return generate_coin_toss_sequence_problem(level)
    elif problem_type == 'coin_toss_count':
        return generate_coin_toss_count_problem(level)
    elif problem_type == 'card_draw_no_replacement_ordered':
        return generate_card_draw_no_replacement_ordered_problem(level)
    elif problem_type == 'card_draw_no_replacement_unordered':
        return generate_card_draw_no_replacement_unordered_problem(level)
    elif problem_type == 'card_draw_with_replacement_ordered':
        return generate_card_draw_with_replacement_ordered_problem(level)

def generate_coin_toss_sequence_problem(level):
    num_tosses = random.randint(2, 3) if level < 3 else random.randint(3, 4)
    outcomes_per_toss = ['正', '反']
    
    # Generate all sequences of outcomes
    sample_space_elements = list(itertools.product(outcomes_per_toss, repeat=num_tosses))
    n_S = len(sample_space_elements)
    
    # Format the sample space for display/explanation
    formatted_S = format_sample_space_string(sample_space_elements)
    
    question_text = f"丟一枚硬幣${num_tosses}$次。<br>觀察每次出現的是正面或反面，寫出其樣本空間與樣本點的個數。"
    
    # The 'answer' field is for the check function, which will verify n(S).
    # The 'correct_answer' field is for displaying the full correct answer in feedback.
    correct_answer_for_check = str(n_S)
    full_correct_answer_text = f"樣本空間 $S={formatted_S}$，樣本點的個數 $n(S)={n_S}$。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_for_check, # This is the numerical part for comparison
        "correct_answer": full_correct_answer_text # This is the full explanation
    }

def generate_coin_toss_count_problem(level):
    num_tosses = random.randint(2, 3) if level < 3 else random.randint(3, 4)
    outcomes_per_toss = ['正', '反']
    
    all_sequences = list(itertools.product(outcomes_per_toss, repeat=num_tosses))
    
    # Collect unique counts of '正'
    counts = set()
    for seq in all_sequences:
        counts.add(seq.count('正'))
    
    sample_space_elements = sorted(list(counts)) # Ensure sorted for canonical representation
    n_S = len(sample_space_elements)
    
    formatted_S = format_sample_space_string(sample_space_elements)
    
    question_text = f"丟一枚硬幣${num_tosses}$次。<br>觀察出現正面的次數，寫出其樣本空間與樣本點的個數。"
    
    correct_answer_for_check = str(n_S)
    full_correct_answer_text = f"樣本空間 $S={formatted_S}$，樣本點的個數 $n(S)={n_S}$。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_for_check,
        "correct_answer": full_correct_answer_text
    }

def generate_card_draw_no_replacement_ordered_problem(level):
    num_items = random.randint(3, 5) if level < 3 else random.randint(4, 6)
    
    max_draw = min(num_items, 3) if level < 3 else min(num_items, 4)
    # Ensure items_to_draw is at least 2 and does not exceed max_draw
    items_to_draw = random.randint(2, max_draw) 
    
    item_labels = list(range(1, num_items + 1))
    
    # Generate permutations (order matters, no replacement)
    sample_space_elements = list(itertools.permutations(item_labels, items_to_draw))
    n_S = len(sample_space_elements)
    
    formatted_S = format_sample_space_string(sample_space_elements)
    
    question_text = f"箱中裝有編號$1$～${num_items}$號的${num_items}$張卡片，今取卡片${items_to_draw}$次，每次一張，卡片取出後不放回。寫出其樣本空間與樣本點的個數。"
    
    correct_answer_for_check = str(n_S)
    full_correct_answer_text = f"樣本空間 $S={formatted_S}$，樣本點的個數 $n(S)={n_S}$。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_for_check,
        "correct_answer": full_correct_answer_text
    }

def generate_card_draw_no_replacement_unordered_problem(level):
    num_items = random.randint(3, 5) if level < 3 else random.randint(4, 6)
    
    max_draw = min(num_items, 3) if level < 3 else min(num_items, 4)
    # Ensure items_to_draw is at least 2 and does not exceed max_draw
    items_to_draw = random.randint(2, max_draw)

    item_labels = list(range(1, num_items + 1))
    
    # Generate combinations (order doesn't matter, no replacement)
    # itertools.combinations yields tuples where elements are in sorted order.
    sample_space_elements = list(itertools.combinations(item_labels, items_to_draw))
    n_S = len(sample_space_elements)
    
    formatted_S = format_sample_space_string(sample_space_elements)
    
    question_text = f"箱中裝有編號$1$～${num_items}$號的${num_items}$張卡片，今同時取出${items_to_draw}$張卡片，取出的卡片無次序之分。寫出其樣本空間與樣本點的個數。"
    
    correct_answer_for_check = str(n_S)
    full_correct_answer_text = f"樣本空間 $S={formatted_S}$，樣本點的個數 $n(S)={n_S}$。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_for_check,
        "correct_answer": full_correct_answer_text
    }

def generate_card_draw_with_replacement_ordered_problem(level):
    num_items = random.randint(2, 4) if level < 3 else random.randint(3, 5)
    
    items_to_draw = random.randint(2, 3) if level < 3 else random.randint(2, 4) # Can be > num_items
    
    item_labels = list(range(1, num_items + 1))
    
    # Generate Cartesian product (order matters, with replacement)
    sample_space_elements = list(itertools.product(item_labels, repeat=items_to_draw))
    n_S = len(sample_space_elements)
    
    formatted_S = format_sample_space_string(sample_space_elements)
    
    question_text = f"箱中裝有編號$1$～${num_items}$號的${num_items}$張卡片，今取卡片${items_to_draw}$次，每次一張，卡片取出後放回。寫出其樣本空間與樣本點的個數。"
    
    correct_answer_for_check = str(n_S)
    full_correct_answer_text = f"樣本空間 $S={formatted_S}$，樣本點的個數 $n(S)={n_S}$。"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_for_check,
        "correct_answer": full_correct_answer_text
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    user_answer 預期只包含樣本點的個數 (n(S))。
    correct_answer 包含詳細的樣本空間和樣本點個數。
    """
    user_answer_stripped = user_answer.strip()
    
    # Example correct_answer: "樣本空間 $S={{(正,正),(正,反),(反,正),(反,反)}}$，樣本點的個數 $n(S)=4$。"
    
    # Extract the numerical part of n(S) from the full correct_answer string
    n_s_str_in_full_answer = ""
    n_s_marker = "n(S)="
    n_s_start_index = correct_answer.find(n_s_marker)
    
    if n_s_start_index != -1:
        # Start looking after "n(S)="
        current_index = n_s_start_index + len(n_s_marker)
        
        # Skip any LaTeX dollar signs that might surround the number
        if current_index < len(correct_answer) and correct_answer[current_index] == '$':
            current_index += 1
            
        while current_index < len(correct_answer) and correct_answer[current_index].isdigit():
            n_s_str_in_full_answer += correct_answer[current_index]
            current_index += 1
            
    try:
        expected_n_S = int(n_s_str_in_full_answer)
        user_n_S = int(user_answer_stripped)
        is_correct = (user_n_S == expected_n_S)
        
    except ValueError:
        is_correct = False
        
    if is_correct:
        result_text = f"完全正確！<br>正確答案是：{correct_answer}"
    else:
        result_text = f"答案不正確。<br>正確答案應為：{correct_answer}"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}