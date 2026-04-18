import random

# --- Helper functions for line relationships in a cuboid ---
def make_canonical_edge(v1, v2):
    """Sorts vertices alphabetically to create a canonical representation of an edge."""
    return tuple(sorted((v1, v2)))

def get_cuboid_data():
    """Defines cuboid edges and their parallel groups."""
    # Assuming standard cuboid vertices A-D (bottom) and E-H (top, A below E)
    # A: front-left-bottom, B: front-right-bottom, C: back-right-bottom, D: back-left-bottom
    # E: front-left-top (above A), F: front-right-top (above B), G: back-right-top (above C), H: back-left-top (above D)

    all_edges_raw = [
        ('A','B'), ('B','C'), ('C','D'), ('D','A'), # Bottom face (ABCD)
        ('E','F'), ('F','G'), ('G','H'), ('H','E'), # Top face (EFGH)
        ('A','E'), ('B','F'), ('C','G'), ('D','H')  # Vertical edges
    ]
    all_edges = [make_canonical_edge(v1,v2) for v1,v2 in all_edges_raw]

    # Group parallel edges. Each list within parallel_groups is a set of parallel edges.
    parallel_groups = [
        # X-direction (e.g., length)
        [make_canonical_edge('A','B'), make_canonical_edge('D','C'), make_canonical_edge('E','F'), make_canonical_edge('H','G')],
        # Y-direction (e.g., width)
        [make_canonical_edge('A','D'), make_canonical_edge('B','C'), make_canonical_edge('E','H'), make_canonical_edge('F','G')],
        # Z-direction (e.g., height)
        [make_canonical_edge('A','E'), make_canonical_edge('B','F'), make_canonical_edge('C','G'), make_canonical_edge('D','H')]
    ]
    return all_edges, parallel_groups

def get_relationship(line1, line2, parallel_groups):
    """
    Determines the relationship between two lines (edges) in a cuboid.
    Assumes line1 and line2 are canonical tuples (v1, v2) with v1 < v2.
    """
    if line1 == line2:
        return 'coincident' # For these problems, we generally consider distinct lines.

    # Intersecting check: share a common vertex
    if set(line1).intersection(set(line2)):
        return 'intersecting'

    # Parallel check: belong to the same parallel group
    for group in parallel_groups:
        if line1 in group and line2 in group:
            return 'parallel'

    # If neither intersecting nor parallel, they must be skew (不共平面且不相交)
    return 'skew'

def generate(level=1):
    """
    生成「空間中兩直線的關係」相關題目。
    探討空間中兩直線的關係，分為共平面（平行、交於一點、重合）與不共平面（歪斜）兩種情況。
    """
    all_edges, parallel_groups = get_cuboid_data()
    
    shape_name = random.choice(['長方體', '正方體'])
    
    # 1. Choose a reference line (e.g., 直線AE)
    reference_line = random.choice(all_edges)
    ref_v1, ref_v2 = reference_line
    
    # 2. Determine the target relationship for the question
    # Level 1 primarily focuses on 'skew' as per examples.
    # Higher levels can mix in 'intersecting' and 'parallel'.
    possible_target_relationships = ['skew']
    if level >= 2:
        possible_target_relationships.extend(['intersecting', 'parallel'])
    
    target_relationship = random.choice(possible_target_relationships)
    
    # Mapping English relationship names to Chinese for question text
    relationship_map = {
        'intersecting': '相交',
        'parallel': '平行',
        'skew': '歪斜'
    }
    
    # 3. Generate candidate lines for the multiple-choice options (e.g., (1)直線AB, (2)直線DH...)
    # Filter out the reference line itself from the pool of candidates
    available_lines_for_options = [edge for edge in all_edges if edge != reference_line]
    
    # Categorize available lines by their relationship to the reference line
    categorized_lines = {
        'intersecting': [],
        'parallel': [],
        'skew': []
    }
    for line in available_lines_for_options:
        rel = get_relationship(reference_line, line, parallel_groups)
        categorized_lines[rel].append(line)
    
    question_options = [] # Stores the actual edge tuples chosen for options
    
    # Ensure there's at least one line with the target relationship among the options.
    # If the target_relationship category is empty (should not happen for a cuboid),
    # we would pick from another category, but this is a robust fallback.
    if categorized_lines[target_relationship]:
        line_for_target_rel = random.choice(categorized_lines[target_relationship])
        question_options.append(line_for_target_rel)
        categorized_lines[target_relationship].remove(line_for_target_rel) # Prevent duplicates
    
    # Fill remaining options (up to 4)
    # First, try to add more lines of the target relationship if available
    random.shuffle(categorized_lines[target_relationship])
    while len(question_options) < 4 and categorized_lines[target_relationship]:
        question_options.append(categorized_lines[target_relationship].pop())

    # Then, add lines from other relationship categories as distractors
    other_relationships = [r for r in ['intersecting', 'parallel', 'skew'] if r != target_relationship]
    random.shuffle(other_relationships) # Randomize which distractor type comes next
    
    for rel_type in other_relationships:
        random.shuffle(categorized_lines[rel_type]) # Shuffle lines within each distractor category
        while len(question_options) < 4 and categorized_lines[rel_type]:
            question_options.append(categorized_lines[rel_type].pop())
            
    # Final shuffle to randomize the display order of all chosen options
    random.shuffle(question_options)
    
    # Build the question text and identify the indices of correct answers
    options_text_list = []
    correct_choices_indices = [] # Stores '1', '2', '3', '4' for correct options

    for i, line_tuple in enumerate(question_options):
        line_v1, line_v2 = line_tuple
        # The question options are displayed as (1), (2), (3), (4)
        options_text_list.append(f"({i+1}) 直線${line_v1}{line_v2}$")
        
        # Check if this option has the target relationship
        actual_rel = get_relationship(reference_line, line_tuple, parallel_groups)
        if actual_rel == target_relationship:
            correct_choices_indices.append(str(i + 1))
            
    # Format the correct answer string as "(1)(2)" for multiple correct choices
    correct_answer_str = "(" + ")(".join(sorted(correct_choices_indices)) + ")"

    # Construct the final question text
    question_text = (
        f"在一個{shape_name}中，$ABCD$ 為底面，$EFGH$ 為頂面，"
        f"且 $A,B,C,D$ 分別位於 $E,F,G,H$ 的正下方。<br>"
        f"下列哪些直線與直線${ref_v1}{ref_v2}$ {relationship_map[target_relationship]}？"
        f"<br>{'<br>'.join(options_text_list)}"
    )

    return {
        "question_text": question_text,
        "answer": correct_answer_str, # The canonical correct answer string used for comparison
        "correct_answer": correct_answer_str # Actual correct answer to show the user
    }

def normalize_choices_answer(answer_str):
    """
    Normalizes a user's multiple-choice answer string into a canonical format.
    E.g., "(3)(4)", "3,4", "4 3", "(4)(3)", "34" all become "(3)(4)".
    Handles various input styles and sorts choices numerically.
    """
    if not isinstance(answer_str, str):
        return ""
    
    # Remove parentheses, spaces, and handle common full-width characters
    normalized = answer_str.replace('(', '').replace(')', '').replace(' ', '').replace('，', ',').strip()
    
    parts = []
    if ',' in normalized:
        parts = normalized.split(',')
    else:
        # If no comma, assume individual digits for choices like "34", but only if purely digits.
        if normalized.isdigit():
            parts = list(normalized)
        else:
            # If it contains non-digits and no comma, it's likely malformed
            return ""

    # Filter out empty strings, attempt to convert to int, sort, then format back to string
    processed_parts = []
    for p in parts:
        p_stripped = p.strip()
        if p_stripped:
            try:
                # Convert to int to ensure numeric sorting, then back to string for formatting
                processed_parts.append(str(int(p_stripped)))
            except ValueError:
                return "" # Return empty string for invalid numeric parts
    
    if not processed_parts:
        return "" # If no valid parts found
        
    sorted_parts = sorted(list(set(processed_parts))) # Use set to remove duplicates, then sort
    
    return "(" + ")(".join(sorted_parts) + ")"

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    """
    user_answer_norm = normalize_choices_answer(user_answer)
    correct_answer_norm = normalize_choices_answer(correct_answer)
    
    is_correct = (user_answer_norm == correct_answer_norm)
    
    result_text = f"完全正確！答案是 ${correct_answer_norm}$。" if is_correct else f"答案不正確。正確答案應為：${correct_answer_norm}$"
    return {"correct": is_correct, "result": result_text, "next_question": True}