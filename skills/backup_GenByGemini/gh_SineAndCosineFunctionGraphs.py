import random
import math
from fractions import Fraction

# Helper function to format numbers, especially fractions that are not part of pi terms
def format_number(val):
    if isinstance(val, (int, float)):
        if val == round(val): # Ensure 1.0 -> "1"
            return str(int(val))
        return str(val)
    elif isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        return r"\\frac{{{}}}{{{}}}".format(val.numerator, val.denominator)
    return str(val)

# Helper for formatting coefficients in trigonometric functions
def format_coeff(coeff, for_var=False):
    if coeff == 1:
        return "" if for_var else "1"
    if coeff == -1:
        return "-" if for_var else "-1"
    if isinstance(coeff, Fraction):
        if coeff.denominator == 1:
            return str(coeff.numerator)
        return r"\\frac{{{}}}{{{}}}".format(coeff.numerator, coeff.denominator)
    return str(coeff)

# Helper for formatting angles involving pi
def format_angle(angle):
    if angle == 0:
        return "0"
    
    # Try to express as fraction of pi
    # limit_denominator(1000) helps with floating point inaccuracies for values like 0.5*math.pi
    val_over_pi = Fraction(angle / math.pi).limit_denominator(1000) 
    
    if val_over_pi.denominator == 1:
        if val_over_pi.numerator == 1:
            return r"\\pi"
        if val_over_pi.numerator == -1:
            return r"-\\pi"
        return f"{val_over_pi.numerator}{{\\pi}}"
    
    # Handle negative numerators like -1/2 pi
    if val_over_pi.numerator == -1:
        return r"-\\frac{{\\pi}}{{{}}}".format(val_over_pi.denominator)
    
    return r"\\frac{{{}}}{{{}}}\\pi".format(val_over_pi.numerator, val_over_pi.denominator)

class SineCosineGraphProblem:
    def __init__(self, A, B, C, D, func_type):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.func_type = func_type # "sin" or "cos"

    def get_max_value(self):
        return abs(self.A) + self.D

    def get_min_value(self):
        return -abs(self.A) + self.D

    def get_amplitude(self):
        return abs(self.A)

    def get_period(self):
        # B can be a Fraction, ensure conversion to float for math.pi
        return 2 * math.pi / abs(float(self.B))

    def get_phase_shift_val(self):
        if float(self.B) == 0: return float('inf') # Should not happen for B in trig functions
        return -float(self.C) / float(self.B)

    def get_vertical_shift(self):
        return self.D

    def get_function_latex(self):
        A_latex = format_coeff(self.A, for_var=False) # For '2sin', '-sin'
        func_latex = self.func_type

        # Handle Bx + C term inside the function argument
        arg_content = ""
        
        # Calculate h (phase shift) for B(x-h) form
        h_val = 0
        if float(self.B) != 0 and self.C != 0:
            h_val = -float(self.C) / float(self.B)
        
        # Decide between B(x-h) or Bx+C
        use_B_parentheses_form = False
        if float(self.B) != 0 and self.C != 0:
            # Check if h_val is a "nice" fraction of pi for B(x-h) form
            h_over_pi = Fraction(h_val / math.pi).limit_denominator(10)
            if h_over_pi.denominator <= 6 or abs(h_val) < 1e-9: # Nice fractions like 0, pi/2, pi/4 etc. or effectively 0
                use_B_parentheses_form = True

        if use_B_parentheses_form:
            # Form: B(x - h)
            B_coeff_str = format_coeff(self.B, for_var=True)
            h_str = format_angle(abs(h_val)) # h_str should be positive magnitude

            x_minus_h = ""
            if h_val > 1e-9: # h_val is positive
                x_minus_h = f"x - {h_str}"
            elif h_val < -1e-9: # h_val is negative
                x_minus_h = f"x + {h_str}"
            else: # h_val is 0
                x_minus_h = "x"

            if B_coeff_str == "": # B=1
                arg_content = x_minus_h
            elif B_coeff_str == "-": # B=-1
                # If h_val is 0: -(x) -> -x
                # If h_val > 0: -(x - h) -> -x + h
                # If h_val < 0: -(x + h) -> -x - h
                if h_val > 1e-9: 
                    arg_content = f"-x + {h_str}" 
                elif h_val < -1e-9: 
                    arg_content = f"-x - {h_str}" 
                else: # h_val == 0
                    arg_content = "-x"
            else: # B is something else (e.g. 2, 1/2)
                arg_content = f"{B_coeff_str}({x_minus_h})"
        else:
            # Fallback to Form: Bx + C
            Bx_str = format_coeff(self.B, for_var=True) + "x"
            C_str = ""
            if self.C > 0:
                C_str = f" + {format_angle(self.C)}"
            elif self.C < 0:
                C_str = f" - {format_angle(abs(self.C))}"
            
            # Avoid 1x or -1x, just x or -x
            if Bx_str == "1x": Bx_str = "x"
            if Bx_str == "-1x": Bx_str = "-x"

            arg_content = f"{Bx_str}{C_str}"
            # If B=0, then it's just C, but B!=0 assumption
            if float(self.B) == 0:
                 arg_content = format_angle(self.C) # this case should not happen for B in Bx+C
            elif Bx_str == "" and C_str == "": # e.g. B=1, C=0 -> "x"
                arg_content = "x"
            elif Bx_str == "" and C_str != "": # e.g. B=1, C=pi/2 -> "x + pi/2"
                arg_content = f"x{C_str}"
            elif Bx_str == "-" and C_str != "": # e.g. B=-1, C=pi/2 -> "-x + pi/2"
                arg_content = f"-x{C_str}"


        # Final argument formatting: add parentheses
        if arg_content == "": arg_content = "x" # Default if arg is just 'x'
        arg_latex = f"({arg_content})"

        # Vertical shift D
        D_latex = ""
        if self.D > 0:
            D_latex = f" + {self.D}"
        elif self.D < 0:
            D_latex = f" - {abs(self.D)}"
        
        # Final assembly
        if A_latex == "" and self.A == 1:
             return f"{func_latex}{arg_latex}{D_latex}"
        elif A_latex == "-" and self.A == -1:
             return f"-{func_latex}{arg_latex}{D_latex}"
        else:
             return f"{A_latex}{func_latex}{arg_latex}{D_latex}"


def generate_basic_properties(level):
    func_type = random.choice(["sin", "cos"])
    A = random.choice([1, 2, 3]) * random.choice([1, -1]) # Amplitude can be 1, 2, 3
    
    # B: period affects, try to make periods simple (pi, 2pi, 4pi, pi/2 etc)
    # 2pi/B, so B = 2pi/Period
    # Period multipliers: 1, 2, 0.5, 4, 4/3, 2/3
    possible_periods_mult = [1, 2, Fraction(1,2), 4, Fraction(4,3), Fraction(2,3)] 
    period_mult = random.choice(possible_periods_mult)
    
    B_val = Fraction(2, period_mult)
    
    # C: phase shift, try to make it simple (pi/4, pi/2, pi) or 0
    C_val = random.choice([0, math.pi/4, math.pi/2, math.pi, -math.pi/4, -math.pi/2])
    if level == 1:
        C_val = random.choice([0, math.pi/2, -math.pi/2]) # Simpler phase shifts for level 1

    # D: vertical shift
    D = random.randint(-2, 2)

    prob = SineCosineGraphProblem(A, B_val, C_val, D, func_type)
    
    question_type = random.choice(["period", "max_min", "amplitude", "all_properties"])
    
    question_text = ""
    correct_answer = ""
    
    func_latex = prob.get_function_latex()
    
    if question_type == "period":
        question_text = f"求函數 $y={func_latex}$ 的週期。"
        correct_answer = format_angle(prob.get_period())
    elif question_type == "max_min":
        question_text = f"求函數 $y={func_latex}$ 的最大值及最小值。(格式: 最大值,最小值)"
        correct_answer = f"{prob.get_max_value()},{prob.get_min_value()}"
    elif question_type == "amplitude":
        question_text = f"求函數 $y={func_latex}$ 的振幅。"
        correct_answer = str(prob.get_amplitude())
    else: # all_properties
        question_text = f"對於函數 $y={func_latex}$，求其週期、最大值及最小值。(格式: 週期,最大值,最小值)"
        correct_answer = f"{format_angle(prob.get_period())},{prob.get_max_value()},{prob.get_min_value()}"

    return {
        "question_text": question_text,
        "answer": correct_answer, # Store the answer as calculated
        "correct_answer": correct_answer, # The string representation for display
    }

def generate_transformation_problem(level):
    base_func = random.choice(["sin", "cos"])
    
    sub_type = random.choice(['identify_shift', 'construct_function'])
    
    if sub_type == 'identify_shift':
        # Example: y = sin(x + 3pi/4) from y = sin(x)
        func_name = random.choice(["sin", "cos"])
        shift_type = random.choice(["horizontal", "vertical"])

        if shift_type == "vertical":
            vertical_shift_val = random.randint(-3, 3)
            # Ensure there is a shift
            while vertical_shift_val == 0: 
                vertical_shift_val = random.randint(-3, 3) 
            
            target_latex_display = f"{func_name}(x) {'' if vertical_shift_val < 0 else '+'}{vertical_shift_val}"
            
            question_text = f"函數 $y={target_latex_display}$ 的圖形如何從 $y={func_name}(x)$ 的圖形平移得到？"
            if vertical_shift_val > 0:
                correct_answer = f"向上平移 {vertical_shift_val} 單位"
            else:
                correct_answer = f"向下平移 {abs(vertical_shift_val)} 單位"
            
        else: # Horizontal shift
            h_val_options = [math.pi/4, math.pi/2, math.pi, 3*math.pi/4, 3*math.pi/2]
            h_val = random.choice(h_val_options) * random.choice([1, -1])
            shift_sign = "+" if h_val > 0 else "-"
            target_latex_display = f"{func_name}(x {shift_sign} {format_angle(abs(h_val))})"
            
            question_text = f"函數 $y={target_latex_display}$ 的圖形如何從 $y={func_name}(x)$ 的圖形平移得到？請填寫平移方向與單位 (例如: 往左平移 pi/4 單位)"
            
            # y = f(x+h_val) is left shift by h_val
            # y = f(x-h_val) is right shift by h_val
            if h_val > 0: # C = h_val, so -(C/B) = -h_val -> shift to left by h_val
                correct_answer = f"往左平移 {format_angle(h_val)} 單位"
            else: # C = h_val, so -(C/B) = -h_val -> shift to right by abs(h_val)
                correct_answer = f"往右平移 {format_angle(abs(h_val))} 單位"
                
            # Add a second correct option for phase shift by 2pi (for level > 1)
            if level > 1 and h_val != 0:
                base_shift = h_val # This is the C in (x+C)
                
                # y = f(x+C) -> left by C
                # It's also y = f(x+C - 2pi) = f(x - (2pi - C)) -> right by (2pi - C)
                # Or y = f(x+C + 2pi) = f(x - (-2pi - C)) -> left by (-2pi - C)
                
                if base_shift > 0: # e.g. left pi/4 (C = pi/4)
                    # alt: right by 2pi - pi/4 = 7pi/4
                    alt_shift_val = 2*math.pi - base_shift
                    alt_answer = f"往右平移 {format_angle(alt_shift_val)} 單位"
                else: # e.g. right pi/4 (C = -pi/4)
                    # alt: left by 2pi - pi/4 = 7pi/4
                    alt_shift_val = 2*math.pi + base_shift # base_shift is negative here
                    alt_answer = f"往左平移 {format_angle(alt_shift_val)} 單位"
                
                # For `check` function, the correct_answer needs to be 'ans1 或 ans2'
                correct_answer = f"{correct_answer} 或 {alt_answer}"
            
        return {
            "question_text": question_text,
            "answer": correct_answer.lower(), # Store lowercased for check
            "correct_answer": correct_answer, # For display
        }
    
    else: # sub_type == 'construct_function'
        func_name = random.choice(["sin", "cos"])
        A_mult = random.choice([1, 2, 3]) # Amplitude factor
        B_div = random.choice([1, 2, 3]) # Period factor (B = 1/B_div)
        D_add = random.randint(-2, 2) # Vertical shift
        
        description_parts = []
        final_A = A_mult
        final_B = Fraction(1, B_div) # Period becomes B_div times original period
        final_C = 0
        final_D = D_add
        
        if A_mult != 1:
            description_parts.append(f"振幅變為 {A_mult} 倍")
        if B_div != 1:
            description_parts.append(f"週期變為 {B_div} 倍")
        if D_add > 0:
            description_parts.append(f"向上平移 {D_add} 單位")
        elif D_add < 0:
            description_parts.append(f"向下平移 {abs(D_add)} 單位")
        
        # Ensure at least one transformation
        if not description_parts:
            A_mult = random.choice([2, 3])
            final_A = A_mult
            description_parts.append(f"振幅變為 {A_mult} 倍")

        target_func_obj = SineCosineGraphProblem(final_A, final_B, final_C, final_D, func_name)
        target_latex_ans = target_func_obj.get_function_latex()

        question_text = f"將 $y={func_name}(x)$ 的圖形經過以下轉換後，得到哪個函數的圖形？\n轉換步驟：{'、'.join(description_parts)}"
        correct_answer = target_latex_ans
        
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer,
        }

def generate_comparison_problem(level):
    func_type = random.choice(["sin", "cos"])
    
    # Generate 3-4 points within [0, 2pi]
    points = []
    labels = ['a', 'b', 'c', 'd']
    num_points = random.choice([3, 4])
    
    # Ensure points are distinct and spread out for interesting comparisons
    generated_angles = set()
    for i in range(num_points):
        while True:
            # Generate angle near a multiple of pi/4 or pi/6
            base_multiples = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2] # Multiples of pi
            base_angle_mult = random.choice(base_multiples)
            
            offset_mult_options = [-0.1, 0.1, 0.05, -0.05, 0.2, -0.2] # Offset in pi units
            if level > 1:
                 # Add some fractional pi offsets for more variety
                 offset_mult_options.extend([Fraction(1,6)*math.pi, Fraction(-1,6)*math.pi, Fraction(1,8)*math.pi, Fraction(-1,8)*math.pi])
                 
            offset = random.choice(offset_mult_options)
            if isinstance(offset, Fraction): offset = float(offset) # Convert Fraction to float if it's not already
            
            angle = (base_angle_mult * math.pi + offset)
            
            # Normalize to [0, 2pi)
            angle = angle % (2 * math.pi)
            if angle < 0: angle += 2 * math.pi
            
            # Ensure angle is distinct enough from others (min diff 0.1 radians)
            if not any(abs(angle - x) < 0.1 for x in generated_angles):
                generated_angles.add(angle)
                points.append((labels[i], angle))
                break
    
    values = []
    for label, angle in points:
        val = math.sin(angle) if func_type == "sin" else math.cos(angle)
        values.append((label, val, angle))

    # Sort values based on their function value for comparison
    values.sort(key=lambda x: x[1], reverse=True) # Descending order

    comparison_str_parts = []
    for i in range(len(values)):
        comparison_str_parts.append(f"${values[i][0]}={func_type}({format_angle(values[i][2])})$")

    question_text = f"利用 $y={func_type}(x)$ 的圖形比較 {', '.join(comparison_str_parts)} 的大小。請從大到小排列 (例如: a>b>c)。"
    
    correct_answer_list = [v[0] for v in values]
    correct_answer = ">".join(correct_answer_list)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
    }

def generate_equation_solving_problem(level):
    func_type = random.choice(["sin", "cos"])
    
    # Simple equations like sin(x) = k, cos(x) = k
    k_val_options = [-1, -0.5, 0, 0.5, 1]
    
    k_val = random.choice(k_val_options)
    
    # Special representation for k_val in LaTeX
    k_latex = format_number(k_val)
    if k_val == 0.5: k_latex = r"\\frac{{1}}{{2}}"
    elif k_val == -0.5: k_latex = r"-\\frac{{1}}{{2}}"
    

    equation_latex = f"{func_type}(x) = {k_latex}"
    
    range_start = 0
    range_end = 2 * math.pi
    range_latex = r"$0 \\le x < 2\\pi$"

    num_solutions = 0
    # Recalculating based on 0 <= x < 2pi range
    if func_type == "sin":
        if abs(k_val) < 1e-9: num_solutions = 2 # x = 0, pi
        elif abs(k_val - 1) < 1e-9: num_solutions = 1 # x = pi/2
        elif abs(k_val + 1) < 1e-9: num_solutions = 1 # x = 3pi/2
        else: num_solutions = 2 # For k_val in (-1, 0) U (0, 1), two solutions
    elif func_type == "cos":
        if abs(k_val) < 1e-9: num_solutions = 2 # x = pi/2, 3pi/2
        elif abs(k_val - 1) < 1e-9: num_solutions = 1 # x = 0
        elif abs(k_val + 1) < 1e-9: num_solutions = 1 # x = pi
        else: num_solutions = 2 # For k_val in (-1, 0) U (0, 1), two solutions

    question_text = f"利用 $y={func_type}(x)$ 的圖形，求方程式 ${equation_latex}$ 在 {range_latex} 範圍內解的個數。"
    correct_answer = str(num_solutions)

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer,
    }


def generate(level=1):
    problem_type = random.choice([
        "basic_properties",
        "transformation",
        "comparison",
        "equation_solving"
    ])

    if problem_type == "basic_properties":
        return generate_basic_properties(level)
    elif problem_type == "transformation":
        return generate_transformation_problem(level)
    elif problem_type == "comparison":
        return generate_comparison_problem(level)
    elif problem_type == "equation_solving":
        return generate_equation_solving_problem(level)
    else: # Fallback
        return generate_basic_properties(level)


def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    Handles basic string comparison, and also specific formats for tuple/list answers.
    """
    user_answer_str = str(user_answer).strip().lower().replace(' ', '')
    correct_answer_str = str(correct_answer).strip().lower().replace(' ', '')

    is_correct = False
    feedback = ""

    # Try direct comparison first
    if user_answer_str == correct_answer_str:
        is_correct = True
    else:
        # Normalize pi representations for evaluation
        user_answer_norm_eval = user_answer_str.replace('pi', str(math.pi)).replace(r'\\pi', str(math.pi))
        correct_answer_norm_eval = correct_answer_str.replace('pi', str(math.pi)).replace(r'\\pi', str(math.pi))
        
        # Try to evaluate simple arithmetic if possible (e.g., 2pi vs 6.28)
        try:
            user_eval = float(user_answer_norm_eval) # Attempt direct float conversion
            correct_eval = float(correct_answer_norm_eval) # Attempt direct float conversion
            if abs(user_eval - correct_eval) < 1e-9: # Floating point comparison
                is_correct = True
        except ValueError:
            # If not simple floats, try eval
            try:
                user_eval = eval(user_answer_norm_eval)
                correct_eval = eval(correct_answer_norm_eval)
                if abs(float(user_eval) - float(correct_eval)) < 1e-9:
                    is_correct = True
            except (NameError, SyntaxError, TypeError, ValueError):
                pass # Not an evaluable expression, or pi not handled
        
        if not is_correct:
            # Handle comma-separated answers (e.g., max,min or period,max,min)
            user_parts = [p.strip() for p in user_answer_str.split(',')]
            correct_parts = [p.strip() for p in correct_answer_str.split(',')]

            if len(user_parts) == len(correct_parts):
                all_parts_match = True
                for u_part, c_part in zip(user_parts, correct_parts):
                    # Direct string comparison for parts
                    if u_part == c_part:
                        continue
                    
                    # Try numeric comparison for parts, including pi evaluation
                    try:
                        u_eval_part = eval(u_part.replace('pi', str(math.pi)).replace(r'\\pi', str(math.pi)))
                        c_eval_part = eval(c_part.replace('pi', str(math.pi)).replace(r'\\pi', str(math.pi)))
                        if abs(float(u_eval_part) - float(c_eval_part)) < 1e-9:
                            continue
                    except (ValueError, NameError, SyntaxError, TypeError):
                        pass # Not numeric or pi-evaluable, so consider it a mismatch
                    
                    all_parts_match = False
                    break # A single mismatch means all parts don't match
                
                if all_parts_match:
                    is_correct = True

        # Handle multiple correct answers, like for phase shift (e.g. left pi/4 or right 7pi/4)
        if not is_correct and "或" in correct_answer_str.lower():
            alt_correct_answers = [ans.strip().lower().replace(' ', '') for ans in correct_answer_str.split('或')]
            if user_answer_str in alt_correct_answers:
                is_correct = True
            else:
                # Try evaluating the parts for alternative answers too
                for alt_ans in alt_correct_answers:
                    user_parts = [p.strip() for p in user_answer_str.split(',')]
                    alt_parts = [p.strip() for p in alt_ans.split(',')]
                    
                    if len(user_parts) == len(alt_parts):
                        all_alt_parts_match = True
                        for u_part, a_part in zip(user_parts, alt_parts):
                            if u_part == a_part:
                                continue
                            try:
                                u_eval_part = eval(u_part.replace('pi', str(math.pi)).replace(r'\\pi', str(math.pi)))
                                a_eval_part = eval(a_part.replace('pi', str(math.pi)).replace(r'\\pi', str(math.pi)))
                                if abs(float(u_eval_part) - float(a_eval_part)) < 1e-9:
                                    continue
                            except (ValueError, NameError, SyntaxError, TypeError):
                                pass
                            all_alt_parts_match = False
                            break
                        if all_alt_parts_match:
                            is_correct = True
                            break

    if is_correct:
        feedback = f"完全正確！答案是 ${correct_answer_str}$。"
    else:
        feedback = f"答案不正確。正確答案應為：${correct_answer_str}$"
        
    return {"correct": is_correct, "result": feedback, "next_question": True}