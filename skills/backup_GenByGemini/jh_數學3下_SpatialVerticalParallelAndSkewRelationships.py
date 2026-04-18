import random
from fractions import Fraction

# --- Data for Cuboid Geometry ---

# ASCII representation of the cuboid, wrapped in <pre> for formatting.
CUBOID_ASCII = """
<pre>
      H -------- G
     /|         /|
    / |        / |
   E -------- F  |
   |  D -------|- C
   | /        | /
   |/         |/
   A -------- B
</pre>
"""

# Define all edges and faces. Using sorted lists for deterministic behavior if seed is set.
EDGES = sorted(['AB', 'BC', 'CD', 'AD', 'EF', 'FG', 'GH', 'EH', 'AE', 'BF', 'CG', 'DH'])
FACES = sorted(['ABCD', 'EFGH', 'ABFE', 'CDHG', 'BCGF', 'ADHE'])

# Pre-computed relationships for edges
EDGE_RELATIONS = {
    # Edges along X-axis
    'AB': {'parallel': ['CD', 'EF', 'GH'], 'perpendicular': ['AD', 'AE', 'BC', 'BF'], 'skew': ['CG', 'DH', 'EH', 'FG']},
    'CD': {'parallel': ['AB', 'EF', 'GH'], 'perpendicular': ['BC', 'CG', 'AD', 'DH'], 'skew': ['AE', 'BF', 'EH', 'FG']},
    'EF': {'parallel': ['AB', 'CD', 'GH'], 'perpendicular': ['AE', 'EH', 'BF', 'FG'], 'skew': ['BC', 'CG', 'AD', 'DH']},
    'GH': {'parallel': ['AB', 'CD', 'EF'], 'perpendicular': ['CG', 'DH', 'FG', 'EH'], 'skew': ['AE', 'BF', 'AD', 'BC']},
    # Edges along Y-axis
    'AD': {'parallel': ['BC', 'EH', 'FG'], 'perpendicular': ['AB', 'AE', 'CD', 'DH'], 'skew': ['BF', 'CG', 'EF', 'GH']},
    'BC': {'parallel': ['AD', 'EH', 'FG'], 'perpendicular': ['AB', 'BF', 'CD', 'CG'], 'skew': ['AE', 'DH', 'EF', 'GH']},
    'EH': {'parallel': ['AD', 'BC', 'FG'], 'perpendicular': ['AE', 'EF', 'DH', 'GH'], 'skew': ['AB', 'BF', 'CD', 'CG']},
    'FG': {'parallel': ['AD', 'BC', 'EH'], 'perpendicular': ['BF', 'EF', 'CG', 'GH'], 'skew': ['AB', 'AE', 'CD', 'DH']},
    # Edges along Z-axis
    'AE': {'parallel': ['BF', 'CG', 'DH'], 'perpendicular': ['AB', 'AD', 'EF', 'EH'], 'skew': ['BC', 'CD', 'FG', 'GH']},
    'BF': {'parallel': ['AE', 'CG', 'DH'], 'perpendicular': ['AB', 'BC', 'EF', 'FG'], 'skew': ['AD', 'CD', 'EH', 'GH']},
    'CG': {'parallel': ['AE', 'BF', 'DH'], 'perpendicular': ['BC', 'CD', 'FG', 'GH'], 'skew': ['AB', 'AD', 'EF', 'EH']},
    'DH': {'parallel': ['AE', 'BF', 'CG'], 'perpendicular': ['AD', 'CD', 'EH', 'GH'], 'skew': ['AB', 'BC', 'EF', 'FG']},
}

# Pre-computed relationships for lines and planes
LINE_PLANE_RELATIONS = {
    # X-axis edges
    'AB': {'parallel': ['CDHG', 'EFGH'], 'perpendicular': ['ADHE', 'BCGF']},
    'CD': {'parallel': ['ABFE', 'EFGH'], 'perpendicular': ['ADHE', 'BCGF']},
    'EF': {'parallel': ['ABCD', 'CDHG'], 'perpendicular': ['ADHE', 'BCGF']},
    'GH': {'parallel': ['ABCD', 'ABFE'], 'perpendicular': ['ADHE', 'BCGF']},
    # Y-axis edges
    'AD': {'parallel': ['BCGF', 'EFGH'], 'perpendicular': ['ABFE', 'CDHG']},
    'BC': {'parallel': ['ADHE', 'EFGH'], 'perpendicular': ['ABFE', 'CDHG']},
    'EH': {'parallel': ['ABCD', 'BCGF'], 'perpendicular': ['ABFE', 'CDHG']},
    'FG': {'parallel': ['ABCD', 'ADHE'], 'perpendicular': ['ABFE', 'CDHG']},
    # Z-axis edges
    'AE': {'parallel': ['BCGF', 'CDHG'], 'perpendicular': ['ABCD', 'EFGH']},
    'BF': {'parallel': ['ADHE', 'CDHG'], 'perpendicular': ['ABCD', 'EFGH']},
    'CG': {'parallel': ['ADHE', 'ABFE'], 'perpendicular': ['ABCD', 'EFGH']},
    'DH': {'parallel': ['BCGF', 'ABFE'], 'perpendicular': ['ABCD', 'EFGH']},
}

# Pre-computed relationships for planes
PLANE_PLANE_RELATIONS = {
    'ABCD': {'parallel': ['EFGH'], 'perpendicular': ['ABFE', 'BCGF', 'CDHG', 'ADHE']},
    'EFGH': {'parallel': ['ABCD'], 'perpendicular': ['ABFE', 'BCGF', 'CDHG', 'ADHE']},
    'ABFE': {'parallel': ['CDHG'], 'perpendicular': ['ABCD', 'EFGH', 'ADHE', 'BCGF']},
    'CDHG': {'parallel': ['ABFE'], 'perpendicular': ['ABCD', 'EFGH', 'ADHE', 'BCGF']},
    'ADHE': {'parallel': ['BCGF'], 'perpendicular': ['ABCD', 'EFGH', 'ABFE', 'CDHG']},
    'BCGF': {'parallel': ['ADHE'], 'perpendicular': ['ABCD', 'EFGH', 'ABFE', 'CDHG']},
}

# --- Problem Generation Functions ---

def generate(level=1):
    """
    生成三維空間中線與面關係的題目。
    題型包含：
    1. 線與線的關係 (選擇題)
    2. 線與面的關係 (選擇題)
    3. 面與面的關係 (選擇題)
    4. 線與面的關係 (是非題)
    5. 面與面的關係 (是非題)
    """
    problem_type = random.choice([
        'line_line_mc', 'line_plane_mc', 'plane_plane_mc',
        'line_plane_tf', 'plane_plane_tf'
    ])

    if problem_type == 'line_line_mc':
        return generate_line_line_mc()
    elif problem_type == 'line_plane_mc':
        return generate_line_plane_mc()
    elif problem_type == 'plane_plane_mc':
        return generate_plane_plane_mc()
    elif problem_type == 'line_plane_tf':
        return generate_line_plane_tf()
    else: # 'plane_plane_tf'
        return generate_plane_plane_tf()

def generate_line_line_mc():
    ref_edge = random.choice(EDGES)
    rel_type, rel_text = random.choice([
        ('parallel', '平行'),
        ('perpendicular', '垂直'),
        ('skew', '歪斜')
    ])

    correct_options = EDGE_RELATIONS[ref_edge][rel_type]
    correct_answer = random.choice(correct_options)

    all_other_edges = [e for e in EDGES if e != ref_edge and e not in correct_options]
    distractors = random.sample(all_other_edges, 3)

    options = distractors + [correct_answer]
    random.shuffle(options)
    
    correct_choice = chr(ord('A') + options.index(correct_answer))
    options_text = "<br>".join([f"({chr(ord('A') + i)}) ${opt}$" for i, opt in enumerate(options)])

    question_text = f"參考下方長方體，下列哪一條直線與直線 ${ref_edge}$ 互為{rel_text}關係？{CUBOID_ASCII}{options_text}"
    
    return {
        "question_text": question_text,
        "answer": correct_choice,
        "correct_answer": correct_choice
    }

def generate_line_plane_mc():
    ref_edge = random.choice(EDGES)
    rel_type, rel_text = random.choice([
        ('parallel', '平行'),
        ('perpendicular', '垂直')
    ])

    correct_options = LINE_PLANE_RELATIONS[ref_edge][rel_type]
    correct_answer = random.choice(correct_options)
    
    # A line can also be *on* a plane. Exclude these from distractors.
    on_plane_faces = [f for f in FACES if all(c in f for c in ref_edge)]
    
    distractor_pool = [f for f in FACES if f not in correct_options and f not in on_plane_faces]
    distractors = random.sample(distractor_pool, min(3, len(distractor_pool)))
    
    # Ensure we have 3 distractors. Unlikely to be needed for a cuboid, but robust.
    # Fix: Removed reference to 'options' in while loop condition
    while len(distractors) < 3:
        potential_distractor = random.choice(FACES)
        if potential_distractor not in correct_options and potential_distractor != correct_answer and potential_distractor not in distractors:
             distractors.append(potential_distractor)

    options = distractors + [correct_answer]
    random.shuffle(options)
    
    correct_choice = chr(ord('A') + options.index(correct_answer))
    options_text = "<br>".join([f"({chr(ord('A') + i)}) 平面 ${opt}$" for i, opt in enumerate(options)])

    question_text = f"參考下方長方體，下列哪一個平面與直線 ${ref_edge}$ 互相{rel_text}？{CUBOID_ASCII}{options_text}"
    
    return {
        "question_text": question_text,
        "answer": correct_choice,
        "correct_answer": correct_choice
    }

def generate_plane_plane_mc():
    ref_face = random.choice(FACES)
    rel_type, rel_text = random.choice([
        ('parallel', '平行'),
        ('perpendicular', '垂直')
    ])

    correct_options = PLANE_PLANE_RELATIONS[ref_face][rel_type]
    correct_answer = random.choice(correct_options)
    
    distractor_pool = [f for f in FACES if f != ref_face and f not in correct_options]
    
    # Perpendicular relationships have 4 correct answers, leaving only 1 distractor. We need to handle this.
    if len(distractor_pool) < 3:
        # Use the single distractor and fill the rest with a correct option that isn't the chosen answer.
        distractors = distractor_pool
        fillers = [f for f in correct_options if f != correct_answer]
        while len(distractors) < 3 and fillers:
            distractors.append(fillers.pop())
    else:
        distractors = random.sample(distractor_pool, 3)

    options = distractors + [correct_answer]
    random.shuffle(options)
    
    correct_choice = chr(ord('A') + options.index(correct_answer))
    options_text = "<br>".join([f"({chr(ord('A') + i)}) 平面 ${opt}$" for i, opt in enumerate(options)])

    question_text = f"參考下方長方體，下列哪一個平面與平面 ${ref_face}$ 互相{rel_text}？{CUBOID_ASCII}{options_text}"
    
    return {
        "question_text": question_text,
        "answer": correct_choice,
        "correct_answer": correct_choice
    }

def generate_line_plane_tf():
    is_true_statement = random.choice([True, False])
    rel_type, rel_text = random.choice([
        ('parallel', '平行'),
        ('perpendicular', '垂直')
    ])
    
    ref_edge = random.choice(EDGES)
    
    if is_true_statement:
        target_face = random.choice(LINE_PLANE_RELATIONS[ref_edge][rel_type])
        correct_answer = '是'
    else:
        # Choose a face that does NOT have the specified relationship and is not on the plane.
        on_plane_faces = [f for f in FACES if all(c in f for c in ref_edge)]
        valid_faces = LINE_PLANE_RELATIONS[ref_edge][rel_type]
        invalid_faces = [f for f in FACES if f not in valid_faces and f not in on_plane_faces]
        if not invalid_faces: # Fallback, should not happen in a cuboid
            other_rel = 'perpendicular' if rel_type == 'parallel' else 'parallel'
            target_face = random.choice(LINE_PLANE_RELATIONS[ref_edge][other_rel])
        else:
            target_face = random.choice(invalid_faces)
        correct_answer = '否'

    question_text = f"參考下方長方體，判斷直線 ${ref_edge}$ 與平面 ${target_face}$ 是否互相{rel_text}？ (請回答 是 或 否){CUBOID_ASCII}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_plane_plane_tf():
    is_true_statement = random.choice([True, False])
    rel_type, rel_text = random.choice([
        ('parallel', '平行'),
        ('perpendicular', '垂直')
    ])
    
    ref_face = random.choice(FACES)
    
    if is_true_statement:
        target_face = random.choice(PLANE_PLANE_RELATIONS[ref_face][rel_type])
        correct_answer = '是'
    else:
        valid_faces = PLANE_PLANE_RELATIONS[ref_face][rel_type]
        invalid_faces = [f for f in FACES if f != ref_face and f not in valid_faces]
        target_face = random.choice(invalid_faces)
        correct_answer = '否'

    question_text = f"參考下方長方體，判斷平面 ${ref_face}$ 與平面 ${target_face}$ 是否互相{rel_text}？ (請回答 是 或 否){CUBOID_ASCII}"

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }
    
def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer = user_answer.strip()
    
    is_correct = False
    # For multiple choice (A, B, C, D), be case-insensitive.
    if correct_answer in ['A', 'B', 'C', 'D']:
        if user_answer.upper() == correct_answer:
            is_correct = True
    # For text answers ('是', '否'), be case-sensitive.
    elif user_answer == correct_answer:
        is_correct = True

    result_text = f"完全正確！答案是 {correct_answer}。" if is_correct else f"答案不正確。正確答案應為：{correct_answer}"
    
    return {"correct": is_correct, "result": result_text, "next_question": True}