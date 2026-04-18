import random
import math

def generate_basic_n_k_problem():
    """Generates a direct n^k repeated permutation problem."""
    
    scenario_choices = [
        "drinks", "rabbit_holes", "password", "student_to_class"
    ]
    problem_scenario = random.choice(scenario_choices)

    if problem_scenario == "password":
        n_choices = 10 # Digits 0-9
        k_items = random.randint(3, 6)
        question_text = f"要設定一個${k_items}$位數的密碼，每位數字都由0到9中選取。如果數字可以重複，共有多少種不同的密碼？"
        explanation = f"每個位數有 ${n_choices}$ 種選擇（0到9），共 ${k_items}$ 個位數。因此，總密碼數為 ${n_choices}^{{{k_items}}} = {n_choices**k_items}$ 種。"
    elif problem_scenario == "rabbit_holes":
        n_choices = random.randint(2, 4) # Number of holes
        k_items = random.randint(3, 5)   # Number of nights
        question_text = f"某兔子挖了${n_choices}$個可以藏身的洞。已知未來的${k_items}$個晚上，該兔子每晚都待在這${n_choices}$個洞的其中之一來躲避敵人，共有多少種藏身安排？"
        explanation = f"兔子每天晚上有 ${n_choices}$ 個藏身的地方，連續 ${k_items}$ 晚。利用乘法原理，共有 ${n_choices}^{{{k_items}}} = {n_choices**k_items}$ 種藏身安排。"
    elif problem_scenario == "drinks":
        n_choices = random.randint(3, 6) # Number of drink types
        k_items = random.randint(2, 4)   # Number of people
        question_text = f"自動販賣機有${n_choices}$種飲料可供選擇，${k_items}$個人運動完後各購買一罐飲料。共有多少種選購方法？"
        explanation = f"每個人有 ${n_choices}$ 種飲料可選，共有 ${k_items}$ 個人。因此，總選購方法數為 ${n_choices}^{{{k_items}}} = {n_choices**k_items}$ 種。"
    elif problem_scenario == "student_to_class":
        n_choices = random.randint(2, 4) # Number of classes
        k_items = random.randint(3, 5)   # Number of students
        question_text = f"有${k_items}$名學生要分發到${n_choices}$個班級，如果每個班級都可以容納所有學生，共有多少種分發方法？"
        explanation = f"每個學生有 ${n_choices}$ 個班級可供選擇，共有 ${k_items}$ 名學生。因此，總分發方法數為 ${n_choices}^{{{k_items}}} = {n_choices**k_items}$ 種。"
    
    correct_answer_val = n_choices ** k_items

    return {
        "question_text": question_text,
        "answer": str(correct_answer_val),
        "correct_answer": str(correct_answer_val),
        "explanation": explanation
    }

def generate_at_least_one_problem():
    """Generates an n^k problem using the complementary counting principle ('at least one')."""
    
    n_recipients_base = random.randint(3, 4) # Need at least 2 remaining options (n-1)
    k_items = random.randint(3, 5)     # Number of items to distribute

    problem_text_template_choice = random.choice([
        "books_to_people",
        "students_to_classes",
    ])

    if problem_text_template_choice == "books_to_people":
        # Use fixed names for clarity, implies n_recipients is 3.
        n_recipients = 3
        recipient_names_pool = ['甲', '乙', '丙']
        random.shuffle(recipient_names_pool) # Randomize order
        target_recipient_name = recipient_names_pool[0] # Pick one to be the "at least one"
        recipient_names_list = "、".join(recipient_names_pool)
        question_text = f"將${k_items}$本不同的書全部分給{recipient_names_list}人，求{target_recipient_name}至少得1本的分法。"
        explanation_item_label = "書"
    else: # students_to_classes scenario
        n_recipients = n_recipients_base
        class_names_pool = ['A班', 'B班', 'C班', 'D班', '一年級', '二年級']
        random.shuffle(class_names_pool)
        target_recipient_name = class_names_pool[0] # Pick one class to be "at least one"
        
        question_text = f"有${k_items}$名學生要分發到${n_recipients}$個班級，其中一個班級名為'{target_recipient_name}'。求'{target_recipient_name}'班至少分到1名學生的分法。"
        explanation_item_label = "學生"


    # Total ways to distribute k_items to n_recipients
    total_ways = n_recipients ** k_items
    
    # Ways where the specific recipient/category gets none
    ways_without_specific_recipient = (n_recipients - 1) ** k_items
    
    correct_answer_val = total_ways - ways_without_specific_recipient
    
    explanation = (
        f"全部的分法為 ${n_recipients}^{{{k_items}}} = {total_ways}$ 種。<br>"
        f"若 {target_recipient_name} 未得分，則 ${k_items}$ {explanation_item_label}只能分給剩下的 ${n_recipients}-1 = {n_recipients - 1}$ 人（或班級），"
        f"其分法有 $({n_recipients}-1)^{{{k_items}}} = {ways_without_specific_recipient}$ 種。<br>"
        f"因此，{target_recipient_name} 至少得1本的分法為 ${total_ways} - {ways_without_specific_recipient} = {correct_answer_val}$ 種。"
    )

    return {
        "question_text": question_text,
        "answer": str(correct_answer_val),
        "correct_answer": str(correct_answer_val),
        "explanation": explanation
    }


def generate(level=1):
    """
    生成「可重複排列」相關題目。
    包含：
    1. 直接 n^k 應用
    2. 排除法 (至少一個)
    """
    problem_type_weights = {
        'basic_n_k': 0.7,
        'at_least_one': 0.3
    }
    
    if level >= 2: # Increase complexity for higher levels
        problem_type_weights = {
            'basic_n_k': 0.4,
            'at_least_one': 0.6
        }

    problem_type = random.choices(
        list(problem_type_weights.keys()), 
        weights=list(problem_type_weights.values()),
        k=1
    )[0]
    
    if problem_type == 'basic_n_k':
        return generate_basic_n_k_problem()
    else: # 'at_least_one'
        return generate_at_least_one_problem()

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    correct_answer = correct_answer.strip()
    
    is_correct = False
    result_text = ""

    try:
        user_num = int(user_answer)
        correct_num = int(correct_answer)
        if user_num == correct_num:
            is_correct = True
            result_text = f"完全正確！答案是 ${correct_answer}$。"
        else:
            result_text = f"答案不正確。正確答案應為：${correct_answer}$"
    except ValueError:
        result_text = f"請輸入一個有效的整數。正確答案應為：${correct_answer}$"

    return {"correct": is_correct, "result": result_text, "next_question": True}