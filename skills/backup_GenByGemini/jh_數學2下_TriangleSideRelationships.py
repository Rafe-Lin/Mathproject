import random

def can_form_triangle(a, b, c):
    """Helper function to check if three side lengths can form a triangle."""
    # All sides must be positive
    if not (a > 0 and b > 0 and c > 0):
        return False
    # Sum of any two sides must be strictly greater than the third side
    # It's sufficient to check if the sum of the two shorter sides is greater than the longest side
    # But checking all three ensures robustness even if input is not sorted
    if (a + b <= c) or (a + c <= b) or (b + c <= a):
        return False
    return True

def generate_check_triangle_sides(level):
    """
    生成判斷三邊長是否能構成三角形的題目。
    """
    sides = []
    
    # Adjust max_side_val based on level for varied difficulty
    if level == 1:
        max_side_val = 12
    elif level == 2:
        max_side_val = 18
    else: # level 3
        max_side_val = 25

    can_form_expected = random.choice([True, False])

    while True: # Loop until valid sides are generated that match can_form_expected
        s1 = random.randint(2, max_side_val)
        s2 = random.randint(2, max_side_val)

        if can_form_expected:
            # For a triangle, the third side s3 must be in (abs(s1-s2), s1+s2)
            min_s3_exclusive = abs(s1 - s2)
            max_s3_exclusive = s1 + s2
            
            # The range for random.randint(a,b) is inclusive, so we need a <= b.
            # Here, a = min_s3_exclusive + 1, b = max_s3_exclusive - 1.
            # This condition (min_s3_exclusive + 1 <= max_s3_exclusive - 1) is always true
            # when s1, s2 >= 1. Our s1, s2 are >= 2, so it's guaranteed to work.
            s3 = random.randint(min_s3_exclusive + 1, max_s3_exclusive - 1)
            
            # Double check with the helper function to be absolutely sure
            if can_form_triangle(s1, s2, s3):
                sides = sorted([s1, s2, s3])
                break # Found valid sides
        else: # Cannot form a triangle
            violation_type = random.choice(['sum', 'difference'])
            
            if violation_type == 'sum': # s3 >= s1+s2 (violates sum rule)
                # s3 can be exactly s1+s2 or larger
                s3 = (s1 + s2) + random.randint(0, 5) 
            else: # s3 <= abs(s1-s2) (violates difference rule)
                min_diff = abs(s1-s2)
                # If min_diff is 0 (i.e., s1 = s2), we cannot violate the difference rule
                # with a positive s3. In that specific case, revert to sum violation.
                if min_diff == 0:
                    s3 = (s1 + s2) + random.randint(0, 5) 
                else:
                    # s3 can be exactly abs(s1-s2) or smaller (but must be positive)
                    s3 = random.randint(1, min_diff)
            
            # Double check with the helper function
            if not can_form_triangle(s1, s2, s3):
                sides = sorted([s1, s2, s3])
                break # Found invalid sides
    
    question_text = f"下列各組的 $3$ 個數分別代表三線段的長度，請問哪組數可以構成三角形？<br>($\\text{{A}})$ ${sides[0]}$、${sides[1]}$、${sides[2]}$"
    correct_answer = "可以" if can_form_expected else "不可以"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_third_side_list(level):
    """
    生成已知兩邊長，求第三邊所有可能整數值的題目。
    """
    if level == 1:
        max_side_val = 15
    elif level == 2:
        max_side_val = 25
    else: # level 3
        max_side_val = 35

    s1 = random.randint(3, max_side_val)
    s2 = random.randint(3, max_side_val)

    # Calculate the range for the third side 'x'
    # It must satisfy |s1 - s2| < x < s1 + s2
    diff_val = abs(s1 - s2)
    sum_val = s1 + s2

    # The inclusive integer range is from diff_val + 1 to sum_val - 1
    min_x_inclusive = diff_val + 1
    max_x_inclusive = sum_val - 1

    # With s1, s2 >= 3, this range will always be valid (min_x_inclusive <= max_x_inclusive).
    # For example, if s1=3, s2=3, then diff=0, sum=6. Range for x is (0,6), so integers [1,2,3,4,5].
    possible_sides = list(range(min_x_inclusive, max_x_inclusive + 1)) 
    
    question_text = f"若一個三角形的兩邊長分別為 ${s1}$ 公分和 ${s2}$ 公分，且第三邊的邊長是整數，請問第三邊的邊長可能是多少？(請列出所有可能的整數值，以逗號分隔，由小到大排列)"
    correct_answer = ", ".join(map(str, possible_sides))

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate(level=1):
    """
    生成「三角形邊長關係」相關題目。
    包含：
    1. 判斷給定三邊長是否能構成三角形。
    2. 已知兩邊長，列出第三邊所有可能的整數值。
    """
    problem_type = random.choice(['check_triangle', 'third_side_list'])
    
    if problem_type == 'check_triangle':
        return generate_check_triangle_sides(level)
    else: # 'third_side_list'
        return generate_third_side_list(level)

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    # Clean user and correct answers for comparison
    # Convert to lowercase, remove spaces, and normalize Chinese commas to standard commas
    user_answer_cleaned = user_answer.strip().lower().replace(" ", "").replace("，", ",")
    correct_answer_cleaned = correct_answer.strip().lower().replace(" ", "").replace("，", ",")
    
    is_correct = (user_answer_cleaned == correct_answer_cleaned)
    
    # If initial direct comparison fails, try to compare as sorted lists of integers
    if not is_correct:
        try:
            # Split by comma, filter out empty strings, convert to int, then sort
            user_nums = sorted([int(x) for x in user_answer_cleaned.split(',') if x.strip()])
            correct_nums = sorted([int(x) for x in correct_answer_cleaned.split(',') if x.strip()])
            if user_nums == correct_nums:
                is_correct = True
        except ValueError:
            pass # User's answer might not be a valid list of numbers (e.g., contains non-digits)
        except AttributeError:
            pass # user_answer might not be a string (unlikely in practice, but robust check)

    # Feedback message, using LaTeX for the correct answer if it's a number
    result_text = f"完全正確！答案是 ${correct_answer}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}