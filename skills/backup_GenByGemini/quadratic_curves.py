import random

def generate_quadratic_curves_question():
    """動態生成一道「二次曲線」的題目 (判斷類型)"""
    # Ax^2 + Bxy + Cy^2 + Dx + Ey + F = 0
    # 判斷類型主要看 B^2 - 4AC
    # < 0: 橢圓或圓
    # = 0: 拋物線
    # = 0: 拋物線
    # > 0: 雙曲線
    
    conic_type = random.choice(['ellipse', 'parabola', 'hyperbola'])
    
    if conic_type == 'ellipse':
        # A, C 同號，B=0
        A = random.randint(1, 5)
        C = random.randint(1, 5)
        while A == C: # 避免是圓
            C = random.randint(1, 5)
        B = 0
        equation_str = f"{A}x^2 + {C}y^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        answer = "橢圓"
    elif conic_type == 'parabola':
        # A=0 或 C=0 (但不同時為0), B=0
        if random.choice([True, False]):
            A = random.randint(1, 5)
            C = 0
        else:
            A = 0
            C = random.randint(1, 5)
        B = 0
        if A == 0:
            equation_str = f"{C}y^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        else:
            equation_str = f"{A}x^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        answer = "拋物線"
    else: # hyperbola
        # A, C 異號，B=0
        A = random.randint(1, 5)
        C = random.randint(-5, -1)
        B = 0
        equation_str = f"{A}x^2 {C}y^2 + {random.randint(-5, 5)}x + {random.randint(-5, 5)}y + {random.randint(-5, 5)} = 0"
        answer = "雙曲線"
        
    question_text = f"請問下列方程式代表哪一種二次曲線？\n{equation_str}"
    
    return {
        "text": question_text,
        "answer": answer,
        "validation_function_name": None
    }
