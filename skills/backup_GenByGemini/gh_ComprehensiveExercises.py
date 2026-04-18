import random
import math
from fractions import Fraction

def generate(level=1):
    """
    生成「綜合練習題」相關題目，涵蓋組合、組合數性質與二項式定理的應用。
    """
    problem_types = [
        'combination_properties_tf',                       # T/F on C(n,k) properties, C-P relation, binomial coeff symmetry
        'basic_combination',                               # Simple C(n,k) calculation, pairs, distinct roles
        'conditional_combination',                         # At least one type, exact mix
        'binomial_coefficient_term',                       # Find specific term's coefficient in (ax+by^k)^n
        'sum_of_binomial_coefficients',                    # Problems related to 2^n, inequalities
        'grouping_distinct_groups_roles',                  # Complex grouping into distinct groups with roles
        'distribution_at_least_one_distinct_to_distinct',  # Distinct items to distinct boxes, at least one in each
        'reverse_combination_calc',                        # Find n given C(n,k) result
        'parity_combination_sum',                          # Choose numbers for an even sum
        'permutation_with_repetition_string',              # Permutation of letters with repetitions
        'binomial_theorem_product_coefficient',            # Coefficient from product of binomials
        'geometry_combination_collinear_points'            # Lines/Triangles from points with collinear subset
    ]
    
    # Adjust difficulty based on level if needed, for now, random choice across all
    problem_type = random.choice(problem_types)

    if problem_type == 'combination_properties_tf':
        return generate_combination_properties_tf()
    elif problem_type == 'basic_combination':
        return generate_basic_combination_problem()
    elif problem_type == 'conditional_combination':
        return generate_conditional_combination_problem()
    elif problem_type == 'binomial_coefficient_term':
        return generate_binomial_coefficient_problem()
    elif problem_type == 'sum_of_binomial_coefficients':
        return generate_sum_of_binomial_coefficients_problem()
    elif problem_type == 'grouping_distinct_groups_roles':
        return generate_grouping_distinct_groups_roles_problem()
    elif problem_type == 'distribution_at_least_one_distinct_to_distinct':
        return generate_distribution_at_least_one_distinct_to_distinct_problem()
    elif problem_type == 'reverse_combination_calc':
        return generate_reverse_combination_problem()
    elif problem_type == 'parity_combination_sum':
        return generate_parity_combination_problem()
    elif problem_type == 'permutation_with_repetition_string':
        return generate_permutation_with_repetition_string_problem()
    elif problem_type == 'binomial_theorem_product_coefficient':
        return generate_binomial_theorem_product_coefficient_problem()
    elif problem_type == 'geometry_combination_collinear_points':
        return generate_geometry_combination_collinear_points_problem()


def generate_combination_properties_tf():
    sub_types = [
        'C_n_k_C_n_n_k',
        'C_P_relation_correct',
        'C_P_relation_incorrect',
        'binomial_coeffs_symmetric',
        'C_n_k_definition_statement'
    ]
    sub_type = random.choice(sub_types)

    if sub_type == 'C_n_k_C_n_n_k':
        n = random.randint(5, 15)
        k = random.randint(1, n // 2 if n >= 2 else 1) # Ensure k is valid
        question_text = f"下列敘述對的打「○」，錯的打「×」。<br>$(1) C_{{{n}}}^{{{k}}} = C_{{{n}}}^{{{n-k}}}$。"
        correct_answer = "○"
    elif sub_type == 'C_P_relation_correct':
        n = random.randint(5, 10)
        k = random.randint(1, n)
        question_text = f"下列敘述對的打「○」，錯的打「×」。<br>$(1) C_{{{n}}}^{{{k}}} \\times {k}! = P_{{{n}}}^{{{k}}}$。"
        correct_answer = "○"
    elif sub_type == 'C_P_relation_incorrect':
        n = random.randint(5, 10)
        k = random.randint(1, n)
        incorrect_factor = k
        while incorrect_factor == k: # Ensure it's incorrect
            incorrect_factor = random.randint(1, n + 1)
        question_text = f"下列敘述對的打「○」，錯的打「×」。<br>$(1) C_{{{n}}}^{{{k}}} \\times {incorrect_factor}! = P_{{{n}}}^{{{k}}}$。"
        correct_answer = "×"
    elif sub_type == 'binomial_coeffs_symmetric':
        n = random.randint(5, 10)
        k1 = random.randint(1, n - 1)
        k2 = n - k1
        var1 = random.choice(['x', 'a', 'p'])
        var2 = random.choice(['y', 'b', 'q'])
        while var1 == var2:
            var2 = random.choice(['y', 'b', 'q'])

        question_text = (
            f"下列敘述對的打「○」，錯的打「×」。<br>$(1)$ 在 $({var1}+{var2})^{{{n}}}$ 的展開式中，"
            f"${var1}^{{{k1}}} {var2}^{{{k2}}}$ 項的係數與 ${var1}^{{{k2}}} {var2}^{{{k1}}}$ 項的係數相等。"
        )
        correct_answer = "○"
    elif sub_type == 'C_n_k_definition_statement':
        n = random.randint(5, 10)
        k = random.randint(1, n)
        question_text = (
            f"下列敘述對的打「○」，錯的打「×」。<br>"
            f"從 ${n}$ 個人中選出 ${k}$ 人的組合數為 $C_{{{n}}}^{{{k}}}$。"
        )
        correct_answer = "○"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_basic_combination_problem():
    sub_type = random.choice(['selection', 'pairs', 'grouping_distinct_roles'])

    if sub_type == 'selection':
        total = random.randint(8, 20)
        select = random.randint(3, total - 1) # Ensure select is smaller than total
        question_text = f"從 ${total}$ 個人中選出 ${select}$ 人，共有幾種選法？"
        correct_answer = str(math.comb(total, select))
    elif sub_type == 'pairs':
        n_people = random.randint(10, 30)
        question_text = (
            f"在一場比賽中，規定參與的選手每人都必須和其他選手各比賽一場。"
            f"若有 ${n_people}$ 位選手，請問總共會有幾場比賽？"
        )
        correct_answer = str(math.comb(n_people, 2))
    elif sub_type == 'grouping_distinct_roles':
        total_people = random.randint(7, 12)
        role1_count = random.randint(2, total_people // 2)
        remaining = total_people - role1_count
        role2_count = random.randint(2, max(2, remaining - 1)) # Ensure at least 1 person remains (or just enough for roles)

        # Re-adjust if selected counts exceed total or are impossible
        while role1_count + role2_count > total_people or role2_count < 1:
            role1_count = random.randint(2, total_people // 2)
            remaining = total_people - role1_count
            role2_count = random.randint(2, max(2, remaining - 1))


        role1_name = random.choice(['掃地', '洗碗', '擔任組長'])
        role2_name = random.choice(['拖地', '擦桌子', '擔任副組長'])
        while role1_name == role2_name:
            role2_name = random.choice(['拖地', '擦桌子', '擔任副組長'])

        question_text = (
            f"從 ${total_people}$ 人中選 ${role1_count}$ 人{role1_name}，"
            f"另選 ${role2_count}$ 人{role2_name}，共有幾種選法？"
        )
        answer_val = math.comb(total_people, role1_count) * math.comb(total_people - role1_count, role2_count)
        correct_answer = str(answer_val)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_conditional_combination_problem():
    num_men = random.randint(5, 10)
    num_women = random.randint(4, 9)
    total_select = random.randint(3, 7)
    
    while total_select > num_men + num_women or total_select < 2:
        total_select = random.randint(3, 7)

    sub_types = [
        'exact_mix',
        'at_least_one_type',
        'at_least_one_of_each'
    ]
    sub_type = random.choice(sub_types)

    if sub_type == 'exact_mix':
        select_men = random.randint(1, total_select - 1)
        select_women = total_select - select_men
        while select_men > num_men or select_women > num_women or select_women < 1:
            select_men = random.randint(1, total_select - 1)
            select_women = total_select - select_men

        question_text = (
            f"從 ${num_men}$ 位男生、${num_women}$ 位女生中選派 ${total_select}$ 人參加社區服務，"
            f"請問恰為 ${select_men}$ 男生 ${select_women}$ 女生的選派方法有多少種？"
        )
        answer_val = math.comb(num_men, select_men) * math.comb(num_women, select_women)
        correct_answer = str(answer_val)

    elif sub_type == 'at_least_one_type':
        select_gender = random.choice(['女', '男'])
        
        if select_gender == '女':
            total_ways = math.comb(num_men + num_women, total_select)
            ways_all_men = 0
            if total_select <= num_men:
                ways_all_men = math.comb(num_men, total_select)
            answer_val = total_ways - ways_all_men
            
            question_text = (
                f"從 ${num_men}$ 位男生、${num_women}$ 位女生中選派 ${total_select}$ 人參加社區服務，"
                f"請問至少有 $1$ 名女生的選派方法有多少種？"
            )
        else: # At least one man
            total_ways = math.comb(num_men + num_women, total_select)
            ways_all_women = 0
            if total_select <= num_women:
                ways_all_women = math.comb(num_women, total_select)
            answer_val = total_ways - ways_all_women

            question_text = (
                f"從 ${num_men}$ 位男生、${num_women}$ 位女生中選派 ${total_select}$ 人參加社區服務，"
                f"請問至少有 $1$ 名男生的選派方法有多少種？"
            )
        correct_answer = str(answer_val)

    elif sub_type == 'at_least_one_of_each':
        total_ways = math.comb(num_men + num_women, total_select)
        
        ways_all_men = 0
        if total_select <= num_men:
            ways_all_men = math.comb(num_men, total_select)
        
        ways_all_women = 0
        if total_select <= num_women:
            ways_all_women = math.comb(num_women, total_select)

        answer_val = total_ways - ways_all_men - ways_all_women
        
        question_text = (
            f"從 ${num_men}$ 位男生、${num_women}$ 位女生中選派 ${total_select}$ 人參加社區服務，"
            f"請問男女生至少各 $1$ 名的選派方法有多少種？"
        )
        correct_answer = str(answer_val)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_binomial_coefficient_problem():
    n = random.randint(4, 7)
    coeff1_val = random.randint(1, 3) * random.choice([-1, 1])
    coeff2_val = random.randint(1, 3) * random.choice([-1, 1])
    
    var1_char = random.choice(['x', 'a'])
    var2_char = random.choice(['y', 'b'])
    while var1_char == var2_char:
        var2_char = random.choice(['y', 'b'])
        
    power_var2_base = random.randint(1, 2)

    k = random.randint(1, n-1)
    
    target_pow1 = n - k
    target_pow2 = k * power_var2_base

    term1_str = f"{coeff1_val}{var1_char}"
    term2_str = f"{coeff2_val}{var2_char}^{{{power_var2_base}}}" if power_var2_base > 1 else f"{coeff2_val}{var2_char}"

    if coeff1_val == 1: term1_str = var1_char
    if coeff1_val == -1: term1_str = f"-{var1_char}"
    if coeff2_val == 1: term2_str = f"{var2_char}^{{{power_var2_base}}}" if power_var2_base > 1 else var2_char
    if coeff2_val == -1: term2_str = f"-{var2_char}^{{{power_var2_base}}}" if power_var2_base > 1 else f"-{var2_char}"
    
    if term2_str.startswith('-'):
        question_expression = f"({term1_str}{term2_str})^{{{n}}}"
    else:
        question_expression = f"({term1_str}+{term2_str})^{{{n}}}"

    binomial_coeff_part = math.comb(n, k)
    coeff_val_part = (coeff1_val ** (n - k)) * (coeff2_val ** k)
    final_coefficient = binomial_coeff_part * coeff_val_part

    question_text = (
        f"求 $ {question_expression} $ 展開式中 "
        f"$ {var1_char}^{{{target_pow1}}} {var2_char}^{{{target_pow2}}} $ 項的係數。"
    )
    correct_answer = str(final_coefficient)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_sum_of_binomial_coefficients_problem():
    sub_type = random.choice(['simple_power', 'inequality'])

    if sub_type == 'simple_power':
        n = random.randint(5, 12)
        question_text = f"求 $ C_{{{n}}}^{{0}} + C_{{{n}}}^{{1}} + C_{{{n}}}^{{2}} + \\dots + C_{{{n}}}^{{{n}}} $ 的值。"
        correct_answer = str(2**n)
    elif sub_type == 'inequality':
        n_true = random.randint(8, 12)
        
        sum_type = random.choice(['full', 'exclude_C0', 'exclude_C0_Cn'])

        if sum_type == 'full':
            sum_str = r"C_{{n}}^{{0}} + C_{{n}}^{{1}} + \dots + C_{{n}}^{{n}}"
            target_value = 2**n_true
        elif sum_type == 'exclude_C0':
            sum_str = r"C_{{n}}^{{1}} + C_{{n}}^{{2}} + \dots + C_{{n}}^{{n}}"
            target_value = 2**n_true - 1
        else: # exclude_C0_Cn
            sum_str = r"C_{{n}}^{{1}} + C_{{n}}^{{2}} + \dots + C_{{n}}^{{n-1}}"
            target_value = 2**n_true - 2

        lower_bound = random.randint(target_value - 50, target_value - 10)
        upper_bound = random.randint(target_value + 10, target_value + 50)
        
        while not (lower_bound < target_value < upper_bound):
            lower_bound = random.randint(target_value - 50, target_value - 10)
            upper_bound = random.randint(target_value + 10, target_value + 50)

        question_text = (
            f"求滿足不等式 $ {lower_bound} < {sum_str} < {upper_bound} $ 的正整數 $n$。"
        )
        correct_answer = str(n_true)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_grouping_distinct_groups_roles_problem():
    K = random.randint(2, 3) # Number of groups (and teachers, and places)
    N_teachers = K
    S_per_group = random.randint(2, 3) # Students per group
    M_students = K * S_per_group # Total students

    answer_val = 1
    current_teachers = N_teachers
    current_students = M_students
    
    place_options = ['甲', '乙', '丙']
    places_str = '、'.join(place_options[:K])

    for _ in range(K):
        answer_val *= math.comb(current_teachers, 1)
        answer_val *= math.comb(current_students, S_per_group)
        current_teachers -= 1
        current_students -= S_per_group

    question_text = (
        f"將 ${N_teachers}$ 名教師、${M_students}$ 名學生分成 ${K}$ 組，"
        f"每組由 $1$ 名教師和 ${S_per_group}$ 名學生組成，"
        f"分別安排到 {places_str} 各地參加活動，共有多少種分配方法？"
    )
    correct_answer = str(answer_val)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def generate_distribution_at_least_one_distinct_to_distinct_problem():
    N_people = random.randint(4, 6) # Number of students/people
    K_villages = random.randint(3, 4) # Number of villages/boxes

    while N_people < K_villages:
        N_people = random.randint(4, 6)
        K_villages = random.randint(3, 4)

    answer_val = 0
    for i in range(K_villages + 1):
        term = math.comb(K_villages, i) * ((K_villages - i) ** N_people)
        if i % 2 == 0:
            answer_val += term
        else:
            answer_val -= term
    
    question_text = (
        f"將 ${N_people}$ 名大學生分配到 ${K_villages}$ 個村落服務，"
        f"每個村落至少 $1$ 名，共有多少種分配方法？"
    )
    correct_answer = str(answer_val)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_reverse_combination_problem():
    k = random.choice([2, 3])
    
    n_true = random.randint(5, 15)
    while n_true < k:
        n_true = random.randint(5, 15)

    result_comb = math.comb(n_true, k)
    
    if k == 2:
        question_text = (
            f"桌球比賽中，若規定參與的選手每人都必須和其他選手各比賽一場，"
            f"賽程總計為 ${result_comb}$ 場，則選手共有多少人？"
        )
    else: # k == 3, simpler context
        item_name = random.choice(['物件', '學生', '球'])
        question_text = (
            f"從 ${n_true}$ 個{item_name}中選出 ${k}$ 個，共有 ${result_comb}$ 種選法。請問總共有多少個{item_name}？"
        )

    correct_answer = str(n_true)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_parity_combination_problem():
    total_count = random.randint(7, 10)
    num_select = random.choice([3, 4])
    
    # Ensure num_odd and num_even are sufficient for selections
    # Heuristic: ensure there's at least 'num_select // 2' of each parity
    min_needed = num_select // 2
    
    num_odd_initial = random.randint(max(min_needed, num_select % 2), total_count - min_needed)
    num_even_initial = total_count - num_odd_initial

    # Reroll until valid counts are achieved
    while num_odd_initial < min_needed or num_even_initial < min_needed:
        num_odd_initial = random.randint(max(min_needed, num_select % 2), total_count - min_needed)
        num_even_initial = total_count - num_odd_initial
    
    num_odd = num_odd_initial
    num_even = num_even_initial

    answer_val = 0
    for k_odd_chosen in range(0, num_select + 1, 2):
        k_even_chosen = num_select - k_odd_chosen
        
        if k_odd_chosen <= num_odd and k_even_chosen <= num_even:
            answer_val += math.comb(num_odd, k_odd_chosen) * math.comb(num_even, k_even_chosen)

    question_text = (
        f"從 $1, 2, \\dots, {total_count}$ 這 ${total_count}$ 個數中，"
        f"同時取出 ${num_select}$ 個不同的數，且其和為偶數，共有多少種取法？"
    )
    correct_answer = str(answer_val)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_permutation_with_repetition_string_problem():
    # Example: "snoopy" (s,n,o,o,p,y) Choose 3 letters, arrange.
    word_data = ("snoopy", {'s':1, 'n':1, 'o':2, 'p':1, 'y':1}, 6)
    word, counts_dict, total_len = word_data
    k = 3 # Fixed k for this specific example type

    distinct_chars_list = list(counts_dict.keys()) # ['s', 'n', 'o', 'p', 'y']
    
    answer_val = 0
    
    # Case 1: All 3 distinct letters
    # Choose 3 distinct characters from the types available (s, n, o, p, y) -> C(5,3)
    # Arrange them -> 3!
    answer_val += math.comb(len(distinct_chars_list), k) * math.factorial(k)
    
    # Case 2: 2 letters are the same, 1 is distinct (e.g., o, o, S)
    # Identify characters that appear at least twice: only 'o' in "snoopy"
    chars_with_at_least_2 = [char for char, count in counts_dict.items() if count >= 2]
    
    if chars_with_at_least_2:
        for repeated_char in chars_with_at_least_2:
            # Choose 1 character to be the repeated pair (e.g., 'o', 1 way)
            # Choose 1 distinct character from the *other* distinct types
            remaining_distinct_types = [c for c in distinct_chars_list if c != repeated_char]
            if remaining_distinct_types:
                answer_val += math.comb(len(remaining_distinct_types), 1) * (math.factorial(k) // math.factorial(2))

    question_text = (
        f"從「{word}」一字共 ${total_len}$ 個字母中，"
        f"任選 ${k}$ 個字母排成一列，共有多少種排法？"
    )
    correct_answer = str(answer_val)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_binomial_theorem_product_coefficient_problem():
    n = random.randint(5, 8)
    a_coeff_val = random.randint(1, 4) * random.choice([-1, 1])
    target_power = 2
    
    cn1 = math.comb(n, 1)
    cn2 = math.comb(n, 2)
    
    # Calculate target_value (coefficient of x^2) using a pre-determined 'a_coeff_val'
    # Coefficient = C(n,2) + a_coeff_val * C(n,1)
    target_value = cn2 + a_coeff_val * cn1

    question_text = (
        f"已知 $(1+{a_coeff_val}x)(1+x)^{{{n}}}$ 的展開式中 $x^{{2}}$ 項的係數為 ${target_value}$，"
        f"求實數 $a$ 的值。"
    )
    correct_answer = str(a_coeff_val) # Now we ask for 'a' that makes this true.
    
    # For a problem where 'a' is unknown but target_value is given, and 'a' needs to be calculated:
    # Set a random 'target_value' for the coefficient, then calculate 'a'.
    # e.g., target_value = random.randint(5, 20) * random.choice([-1, 1])
    # a = (target_value - cn2) / cn1
    # Ensure a is integer or simple fraction
    # numerator = target_value - cn2
    # denominator = cn1
    # while numerator % denominator != 0:
    #     n = random.randint(5, 8)
    #     target_value = random.randint(5, 20) * random.choice([-1, 1])
    #     cn1 = math.comb(n, 1)
    #     cn2 = math.comb(n, 2)
    #     numerator = target_value - cn2
    #     denominator = cn1
    # correct_a = Fraction(numerator, denominator)
    # This version is what's in the example. Let's switch to this more challenging one.
    
    target_value_q = random.randint(5, 20) * random.choice([-1, 1])
    
    # Reroll until we get an integer 'a' for simplicity
    while (target_value_q - cn2) % cn1 != 0:
        n = random.randint(5, 8)
        cn1 = math.comb(n, 1)
        cn2 = math.comb(n, 2)
        target_value_q = random.randint(5, 20) * random.choice([-1, 1])

    correct_a = (target_value_q - cn2) // cn1

    question_text = (
        f"已知 $(1+ax)(1+x)^{{{n}}}$ 的展開式中 $x^{{2}}$ 項的係數為 ${target_value_q}$，"
        f"求實數 $a$ 的值。"
    )
    correct_answer = str(correct_a)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_geometry_combination_collinear_points_problem():
    total_points = random.randint(8, 12)
    collinear_points = random.randint(4, min(total_points - 1, 6))
    
    question_type = random.choice(['lines', 'triangles'])
    
    if question_type == 'lines':
        ans_val = math.comb(total_points, 2) - math.comb(collinear_points, 2) + 1
        question_text = (
            f"空間中有 ${total_points}$ 個點，其中有 ${collinear_points}$ 個點共線，"
            f"其餘點不共線。請問這些點共可決定多少條直線？"
        )
    else: # triangles
        ans_val = math.comb(total_points, 3) - math.comb(collinear_points, 3)
        question_text = (
            f"空間中有 ${total_points}$ 個點，其中有 ${collinear_points}$ 個點共線，"
            f"其餘點不共線。請問以這些點中的 $3$ 個點為頂點，共可決定多少個三角形？"
        )
    
    correct_answer = str(ans_val)
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }


def check(user_answer, correct_answer):
    user_answer = user_answer.strip().upper()
    correct_answer = correct_answer.strip().upper()
    
    is_correct = (user_answer == correct_answer)
    
    if not is_correct:
        try:
            user_val = float(Fraction(user_answer))
            correct_val = float(Fraction(correct_answer))
            if abs(user_val - correct_val) < 1e-9:
                is_correct = True
        except (ValueError, ZeroDivisionError):
            pass

    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}