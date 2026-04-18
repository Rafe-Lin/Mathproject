"""
═══════════════════════════════════════════════════════════════════════
生成时序正确的AKT训练数据
遵循台湾课纲的严格课程顺序 (一上→一下→二上→二下→三上)
═══════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
from scipy.special import expit as sigmoid

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# ═══════════════════════════════════════════════════════════════════
# 课程结构定义
# ═══════════════════════════════════════════════════════════════════

CURRICULUM = {
    "一上": [
        ("jh_數學1上_CommonDivisibilityRules", [10]),
        ("jh_數學1上_FourArithmeticOperationsOfIntegers", [12]),
        ("jh_數學1上_IntegerAdditionOperation", [11]),
    ],
    "一下": [
        ("jh_數學1下_RectangularCoordinatePlaneAndCoordinateRepresentation", [12]),
        ("jh_數學1下_DrawingGraphsOfTwoVariableLinearEquations", [12]),
    ],
    "二上": [
        ("jh_數學2上_BasicPropertiesOfRadicalOperations", [13]),
        ("jh_數學2上_FourOperationsOfRadicals", [14]),
        ("jh_數學2上_PolynomialAdditionAndSubtraction", [10]),
        ("jh_數學2上_PolynomialDivision", [11]),
        ("jh_數學2上_WordProblems", [11]),
    ],
    "二下": [
        ("jh_數學2下_MeaningAndPropertiesOfParallelograms", [10]),
        ("jh_數學2下_IdentifyingAndConstructingParallelograms", [12]),
        ("jh_數學2下_PropertiesOfRectanglesRhombusesKitesAndSquares", [13]),
    ],
    "三上": [
        ("jh_數學3上_ParallelLinesProportionalSegmentsProperty", [26]),
        ("jh_數學3上_ApplicationOfParallelLinesProportionalSegmentsProperty", [13]),
        ("jh_數學3上_GeometricProof", [11]),
        ("jh_數學3上_InscribedAngleParallelChordsAndCyclicQuadrilateral", [11]),
    ],
}

SEMESTER_ORDER = list(CURRICULUM.keys())  # 课程顺序

# 构建全局技能列表和映射
ALL_SKILLS = []
SKILL_TO_SEMESTER = {}
for semester, skills in CURRICULUM.items():
    for skill_id, problems in skills:
        ALL_SKILLS.append(skill_id)
        SKILL_TO_SEMESTER[skill_id] = semester

print("课程结构:")
for semester in SEMESTER_ORDER:
    count = len(CURRICULUM[semester])
    print(f"  {semester}: {count} 个技能")

# ═══════════════════════════════════════════════════════════════════
# 学生进度模型
# ═══════════════════════════════════════════════════════════════════

def assign_student_progress():
    """
    根据IRT能力参数，决定学生能学到哪个学期。
    
    假设：
    - 能力高 (θ > 0.5) → 可学到三上（完整5学期）
    - 能力中等 (0 < θ ≤ 0.5) → 可学到二下（4学期）
    - 能力低 (-1 < θ ≤ 0) → 可学到二上（3学期）
    - 能力很低 (θ ≤ -1) → 只到一下（2学期）
    """
    theta = np.random.normal(0, 0.8)
    
    if theta > 0.5:
        max_semester_idx = 4  # 三上
    elif theta > 0:
        max_semester_idx = 3  # 二下
    elif theta > -1:
        max_semester_idx = 2  # 二上
    else:
        max_semester_idx = 1  # 一下
    
    return theta, max_semester_idx

# ═══════════════════════════════════════════════════════════════════
# 从题库读取题目信息
# ═══════════════════════════════════════════════════════════════════

print("\n读取题库...")
df_problems = pd.read_excel('课本题庫.xlsx')

# 为每个技能建立题目集
skill_problems = {}
for skill_name in ALL_SKILLS:
    problems_df = df_problems[df_problems['skill_id'] == skill_name]
    problem_ids = problems_df['id'].tolist()
    skill_problems[skill_name] = problem_ids
    
print(f"✓ 加载了 {len(ALL_SKILLS)} 个技能的题目\n")

# ═══════════════════════════════════════════════════════════════════
# IRT难度参数
# ═══════════════════════════════════════════════════════════════════

problem_difficulty = {}
for skill_name, problem_ids in skill_problems.items():
    for problem_id in problem_ids:
        if problem_id not in problem_difficulty:
            # 从题库读取难度等级
            prob_row = df_problems[df_problems['id'] == problem_id]
            if len(prob_row) > 0:
                difficulty = prob_row['difficulty_level'].values[0]
                if pd.isna(difficulty):
                    difficulty = 2
                base_b = float(difficulty) - 2  # -1, 0, 1
            else:
                base_b = 0
            
            b = base_b + np.random.normal(0, 0.2)
            problem_difficulty[problem_id] = np.clip(b, -2, 2)

print(f"✓ 为 {len(problem_difficulty)} 道题设置了难度参数\n")

# ═══════════════════════════════════════════════════════════════════
# 生成时序正确的学生作答序列
# ═══════════════════════════════════════════════════════════════════

print("="*70)
print("生成时序正确的训练数据...")
print("="*70)

interactions = []
student_stats = []

N_STUDENTS = 600

for student_id in range(1, N_STUDENTS + 1):
    # 1. 分配学生进度
    theta, max_semester_idx = assign_student_progress()
    
    # 2. 按课程顺序逐个学期学习
    total_attempts = 0
    
    for semester_idx in range(max_semester_idx + 1):
        semester = SEMESTER_ORDER[semester_idx]
        skills_in_semester = CURRICULUM[semester]
        
        # 当前学期内，每个技能做题数量
        n_skills_in_semester = len(skills_in_semester)
        
        for skill_name, problem_list in skills_in_semester:
            # 该技能下的作答数
            # 模拟：学生对某个技能会做多次作答，而不是只做一题
            n_attempts_this_skill = np.random.randint(4, 12)
            
            for _ in range(n_attempts_this_skill):
                # 从该技能的题库中随机选择题目
                if skill_name in skill_problems and len(skill_problems[skill_name]) > 0:
                    problem_id = np.random.choice(skill_problems[skill_name])
                    
                    # IRT: 答对概率
                    b = problem_difficulty.get(problem_id, 0)
                    p_correct = sigmoid(theta - b)
                    correct = int(np.random.random() < p_correct)
                    
                    interactions.append({
                        'studentId': student_id,
                        'problemId': problem_id,
                        'skill': skill_name,
                        'correct': correct,
                    })
                    
                    total_attempts += 1
    
    student_stats.append({
        'student_id': student_id,
        'theta': theta,
        'max_semester': SEMESTER_ORDER[max_semester_idx],
        'total_attempts': total_attempts,
    })
    
    if student_id % 100 == 0:
        print(f"  已生成 {student_id}/600 名学生的数据...")

# ═══════════════════════════════════════════════════════════════════
# 数据验证
# ═══════════════════════════════════════════════════════════════════

df_interactions = pd.DataFrame(interactions)
df_stats = pd.DataFrame(student_stats)

print(f"\n✓ 生成了 {len(df_interactions):,} 筆互動記錄\n")

print("【数据统计】")
print(f"  学生数: {df_interactions['studentId'].nunique()}")
print(f"  题目数: {df_interactions['problemId'].nunique()}")
print(f"  技能数: {df_interactions['skill'].nunique()}")
print(f"  全局正确率: {df_interactions['correct'].mean():.1%}")

print("\n【学生进度分布】")
print(df_stats['max_semester'].value_counts().sort_index())

print("\n【技能互动分布】")
skill_interactions = df_interactions['skill'].value_counts()
for skill in ALL_SKILLS:
    count = skill_interactions.get(skill, 0)
    print(f"  {skill}: {count:5,} 筆")

# ═══════════════════════════════════════════════════════════════════
# 时序验证
# ═══════════════════════════════════════════════════════════════════

print("\n【时序性验证】")
SEMESTER_MAP = {}
CURRICULUM_ORDER = {}
order = 0
for semester, skills in CURRICULUM.items():
    for skill_name, _ in skills:
        SEMESTER_MAP[skill_name] = semester
        CURRICULUM_ORDER[skill_name] = order
        order += 1

violations = []
for student_id in df_interactions['studentId'].unique():
    student_data = df_interactions[df_interactions['studentId'] == student_id].copy()
    skills_sequence = student_data['skill'].values
    
    for i in range(1, len(skills_sequence)):
        prev_skill = skills_sequence[i-1]
        curr_skill = skills_sequence[i]
        
        prev_order = CURRICULUM_ORDER.get(prev_skill, -1)
        curr_order = CURRICULUM_ORDER.get(curr_skill, -1)
        
        if prev_order >= 0 and curr_order >= 0 and curr_order < prev_order:
            violations.append((student_id, prev_skill, curr_skill))

print(f"  时序违反总数: {len(violations):,} (占比 {100*len(violations)/len(df_interactions):.2f}%)")
print(f"  完全遵循课程顺序的学生: {600 - len(set(v[0] for v in violations))}/600 " +
      f"({100*(600 - len(set(v[0] for v in violations)))/600:.1f}%)")

# ═══════════════════════════════════════════════════════════════════
# 保存数据
# ═══════════════════════════════════════════════════════════════════

output_path = './synthesized_training_data_sequential.csv'
df_interactions.to_csv(output_path, index=False)
print(f"\n✓ 数据已保存到: {output_path}")

print("\n" + "="*70)
print("数据生成完成！这次数据完全遵循课程顺序。")
print("="*70)
