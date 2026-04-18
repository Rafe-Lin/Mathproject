import random
from fractions import Fraction

def fraction_to_latex(frac_obj):
    """
    Converts a Fraction object or an integer to its LaTeX representation.
    For example, Fraction(1, 2) becomes "\\frac{1}{2}", Fraction(3, 1) becomes "3".
    """
    if isinstance(frac_obj, int):
        return str(frac_obj)
    if frac_obj.denominator == 1:
        return str(frac_obj.numerator)
    return r"\\frac{" + str(frac_obj.numerator) + r"}{" + str(frac_obj.denominator) + r"}"

def generate_check_independence_problem():
    """
    Generates a problem to check if two events from a dice roll are independent.
    """
    sample_space_size = 6 # Standard fair die
    
    # Define various events for a fair die roll
    event_definitions = [
        ("奇數點", {1, 3, 5}),
        ("偶數點", {2, 4, 6}),
        ("質數點", {2, 3, 5}),
        ("點數大於3", {4, 5, 6}),
        ("點數小於4", {1, 2, 3}),
        ("出現1或6點", {1, 6}),
        ("出現2或5點", {2, 5}),
        ("出現4或5點", {4, 5}),
        ("出現大於等於5點", {5, 6}),
        ("出現小於等於2點", {1, 2}),
    ]
    
    # Pick two distinct events based on their set content to ensure mathematical difference
    event_A_def_str, event_A_set = random.choice(event_definitions)
    
    available_event_types_for_B = [
        (desc, s) for desc, s in event_definitions 
        if s != event_A_set # Ensure the sets are mathematically distinct
    ]
    
    # If, by chance, all remaining events are identical to A, this would be an error.
    # With the given large set of distinct events, this is highly unlikely for level 1.
    event_B_def_str, event_B_set = random.choice(available_event_types_for_B)
    
    # Calculate probabilities
    P_A = Fraction(len(event_A_set), sample_space_size)
    P_B = Fraction(len(event_B_set), sample_space_size)
    
    event_A_intersect_B_set = event_A_set.intersection(event_B_set)
    P_A_intersect_B = Fraction(len(event_A_intersect_B_set), sample_space_size)
    
    # Check for independence condition P(A∩B) = P(A)P(B)
    is_independent = (P_A_intersect_B == P_A * P_B)
    
    question_text = f"擲一粒公正骰子一次，考慮下列兩事件：<br>" \
                    f"$A$：出現{event_A_def_str}，<br>" \
                    f"$B$：出現{event_B_def_str}。<br>" \
                    f"試問$A$與$B$是否為獨立事件？"
    
    correct_answer_text = "是" if is_independent else "否"
    
    return {
        "question_text": question_text,
        "answer": correct_answer_text,
        "correct_answer": correct_answer_text
    }

def generate_calculate_probability_problem():
    """
    Generates a problem where the probabilities of combined independent events are calculated.
    """
    denominators = [2, 3, 4, 5, 6, 8, 10]
    
    # Generate probabilities for event A and B
    d_a = random.choice(denominators)
    n_a = random.randint(1, d_a - 1)
    P_A = Fraction(n_a, d_a)
    
    d_b = random.choice(denominators)
    n_b = random.randint(1, d_b - 1)
    P_B = Fraction(n_b, d_b)
    
    # Scenarios to provide context for the probabilities
    event_scenarios = [
        "甲、乙兩人同時各做一件事。已知甲完成的機率為",
        "甲、乙兩選手射擊的命中率分別為",
        "甲、乙兩隊贏得某場比賽的機率分別為",
        "根據統計：使用新手機後，三年內會換手機的機率為"
    ]
    scenario_prefix = random.choice(event_scenarios)
    
    # Action words corresponding to scenarios
    action_words_map = {
        "手機": "換手機", "射擊": "命中", "比賽": "贏得", "完成": "完成"
    }
    
    action = "完成" # Default action
    for keyword, act_word in action_words_map.items():
        if keyword in scenario_prefix:
            action = act_word
            break
        
    # Define different types of questions and their calculation functions
    question_types = [
        ("兩人都{action_a}", lambda pa, pb: pa * pb), # P(A∩B)
        ("至少有一人{action_a}", lambda pa, pb: pa + pb - (pa * pb)), # P(A∪B)
        ("兩人都沒{action_a}", lambda pa, pb: (Fraction(1, 1) - pa) * (Fraction(1, 1) - pb)), # P(A'∩B')
        ("甲{action_a}但乙沒{action_a}", lambda pa, pb: pa * (Fraction(1, 1) - pb)), # P(A∩B')
        ("乙{action_a}但甲沒{action_a}", lambda pa, pb: pb * (Fraction(1, 1) - pa)) # P(B∩A')
    ]
    
    question_desc_template, calculation_func = random.choice(question_types)
    question_desc = question_desc_template.replace("{action_a}", action)
    
    calculated_prob = calculation_func(P_A, P_B)
    
    question_text = f"{scenario_prefix} ${fraction_to_latex(P_A)}$ 和 ${fraction_to_latex(P_B)}$，且兩人{action}與否為獨立事件，求{question_desc}的機率。"
    
    correct_answer = str(calculated_prob)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sequential_events_problem():
    """
    Generates a problem involving sequential independent events, typically in a game context.
    Covers consecutive wins or probability of winning a series from an interrupted state.
    """
    denominators = [2, 3, 4, 5] # Use smaller denominators for game probabilities
    
    d_a = random.choice(denominators)
    n_a = random.randint(1, d_a - 1)
    P_A_win_single_game = Fraction(n_a, d_a)
    P_B_win_single_game = Fraction(1, 1) - P_A_win_single_game
    
    problem_scenario_choice = random.choice([
        "consecutive_wins",  # Player A needs to win N consecutive games
        "specific_series_state", # Player A needs 1 win, B needs K wins (simple series calculation)
    ])

    if problem_scenario_choice == "consecutive_wins":
        # Example: 甲選手前兩盤皆敗，求甲贏得比賽的機率 (simplified to N consecutive wins)
        num_consecutive_wins_needed = random.randint(2, 4) # A needs 2, 3, or 4 consecutive wins
        
        question_text = f"設甲單盤獲勝的機率為 ${fraction_to_latex(P_A_win_single_game)}$，且每盤的比賽結果互不影響。<br>" \
                        f"請問甲選手連勝 ${num_consecutive_wins_needed}$ 盤的機率為何？"
        
        calculated_prob = P_A_win_single_game ** num_consecutive_wins_needed
        correct_answer = str(calculated_prob)
        
    elif problem_scenario_choice == "specific_series_state":
        # Scenario: A needs 1 win, B needs `b_wins_to_win` wins (e.g., 2 or 3)
        # This matches the "甲勝2局、乙勝1局" example, where A needs 1 more, B needs 2 more.
        b_wins_to_win = random.choice([2, 3])
        
        calculated_prob_A_wins = Fraction(0, 1)
        # Sum of probabilities where A wins the last game:
        # P(A wins next) + P(B wins then A wins) + P(B wins twice then A wins) ...
        for i in range(b_wins_to_win): # i is number of games B wins before A wins the final game
            calculated_prob_A_wins += (P_B_win_single_game ** i) * P_A_win_single_game
            
        # Ensure probability does not exceed 1 (due to potential tiny floating point errors if not using Fraction, but Fraction handles this well)
        if calculated_prob_A_wins > Fraction(1, 1):
            calculated_prob_A_wins = Fraction(1, 1)

        # Generate context for the question, like current scores in a series
        series_wins_needed = random.choice([3, 4]) # e.g., first to 3 wins, or first to 4 wins
        
        current_A_score = series_wins_needed - 1 # A needs 1 more win
        current_B_score = series_wins_needed - b_wins_to_win # B needs b_wins_to_win more wins
        
        # Randomly choose between asking for P(A wins) or prize distribution
        # If one player is already guaranteed to win (prob 0 or 1), just ask for probability.
        if random.random() < 0.6 or calculated_prob_A_wins == Fraction(0, 1) or calculated_prob_A_wins == Fraction(1, 1):
            question_text = f"甲、乙兩人比賽桌球（不得和局），約定先勝 ${series_wins_needed}$ 局者贏得比賽。" \
                            f"設甲單局獲勝的機率為 ${fraction_to_latex(P_A_win_single_game)}$，且每局的比賽結果互不影響。<br>" \
                            f"已知當比賽進行至甲勝 ${current_A_score}$ 局、乙勝 ${current_B_score}$ 局時，" \
                            f"求甲贏得比賽的機率。"
            
            correct_answer = str(calculated_prob_A_wins)
            
        else: # Ask for prize distribution
            total_prize = random.choice([7200, 8100, 9000, 10000])
            prize_for_A = int(total_prize * calculated_prob_A_wins)
            
            question_text = f"甲、乙兩人比賽桌球（不得和局），約定先勝 ${series_wins_needed}$ 局者可得獎金 ${total_prize}$ 元。" \
                            f"設甲單局獲勝的機率為 ${fraction_to_latex(P_A_win_single_game)}$，且每局的比賽結果互不影響。<br>" \
                            f"已知當比賽進行至甲勝 ${current_A_score}$ 局、乙勝 ${current_B_score}$ 局時，" \
                            f"因故中止且不再比賽，至於獎金的分配，則依若繼續比賽兩人贏得比賽的機率之比例來分配，求甲應分得多少獎金。"
            
            correct_answer = str(prize_for_A)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    Generates a random problem related to independent events.
    The level parameter is not used in this implementation, as all problems are for level 1.
    """
    problem_type_choices = ['check_independence', 'calculate_probability', 'sequential_events']
    problem_type = random.choice(problem_type_choices)
    
    if problem_type == 'check_independence':
        return generate_check_independence_problem()
    elif problem_type == 'calculate_probability':
        return generate_calculate_probability_problem()
    elif problem_type == 'sequential_events':
        return generate_sequential_events_problem()

def check(user_answer, correct_answer):
    """
    Checks if the user's answer is correct.
    Handles fraction, integer, and "是/否" string comparisons.
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    feedback = ""

    try:
        # Try to convert to Fraction, which handles "1/2", "0.5", and integers like "7200".
        user_val = Fraction(user_answer)
        correct_val = Fraction(correct_answer)
        if user_val == correct_val:
            is_correct = True
            feedback = f"完全正確！答案是 ${fraction_to_latex(correct_val)}$。"
        else:
            feedback = f"答案不正確。正確答案應為：${fraction_to_latex(correct_val)}$"
    except ValueError:
        # If conversion to Fraction fails, it's likely a "是" or "否" answer.
        if user_answer.upper() == correct_answer.upper():
            is_correct = True
            feedback = f"完全正確！答案是 {correct_answer}。"
        else:
            feedback = f"答案不正確。正確答案應為：{correct_answer}"
    
    return {"correct": is_correct, "result": feedback, "next_question": True}