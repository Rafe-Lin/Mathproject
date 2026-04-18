"""
═════════════════════════════════════════════════════════════════
改进的 AKT 训练数据生成器 (v2) - 遵循课程顺序
═════════════════════════════════════════════════════════════════

核心改进：
1. ✓ 按照课程顺序（一上→一下→二上→二下→三上）生成数据
2. ✓ 保持时序性：前置知识在后续知识之前
3. ✓ 允许"重复练习"：学高年级时可以复习低年级
4. ✓ 模拟真实学生路径：每个学生的学习速度可能不同
"""

import pandas as pd
import numpy as np
from scipy.special import expit as sigmoid
import os
from curriculum_structure import (
    CURRICULUM_GRADES, SKILL_TO_GRADE, SKILL_TO_SEQUENCE_ORDER,
    CurriculumProgress, validate_sequence
)

# =============================================
# 配置参数
# =============================================
RANDOM_SEED = 42
N_STUDENTS = 600
MIN_INTERACTIONS_PER_SKILL = 3000

# 控制多少比例的题目来自"当前年级" vs "之前学过的年级"
CURRENT_GRADE_RATIO = 0.70  # 70% 来自当前学习的年级
REVIEW_RATIO = 0.30  # 30% 来自之前学过的年级

print("="*70)
print("生成符合课程逻辑的 AKT 训练数据 (v2)")
print("="*70 + "\n")

# =============================================
# 1. 读取题庫
# =============================================
print("读取题库...")
df_problems = pd.read_excel('課本題庫.xlsx')

# 只保留有效的20个技能（17个已确认 + 扩展）
selected_skills = list(SKILL_TO_GRADE.keys())
print(f"使用的技能数：{len(selected_skills)}")

df_problems = df_problems[df_problems['skill_id'].isin(selected_skills)].copy()
df_problems = df_problems.reset_index(drop=True)

# 创建问题ID和映射
problem_to_skill = {}
skill_to_problems = {}
problems_by_grade = {}

for _, row in df_problems.iterrows():
    pid = row['id']
    skill = row['skill_id']
    
    if skill in SKILL_TO_GRADE:
        problem_to_skill[pid] = skill
        grade = SKILL_TO_GRADE[skill]
        
        if skill not in skill_to_problems:
            skill_to_problems[skill] = []
        skill_to_problems[skill].append(pid)
        
        if grade not in problems_by_grade:
            problems_by_grade[grade] = []
        problems_by_grade[grade].append(pid)

print(f"题目总数：{len(problem_to_skill)}")
print(f"按年级的题目分布：")
for grade in ['一上', '一下', '二上', '二下', '三上']:
    count = len(problems_by_grade.get(grade, []))
    print(f"  {grade}: {count} 道")

# =============================================
# 2. 生成 IRT 参数
# =============================================
print("\n生成 IRT 参数...")
np.random.seed(RANDOM_SEED)

# 题目难度（按技能分布）
problem_difficulty = {}
for skill, problems in skill_to_problems.items():
    # 一上技能最简单，三上最难
    grade = SKILL_TO_GRADE[skill]
    grade_difficulty = {
        '一上': -0.5,
        '一下': 0.0,
        '二上': 0.5,
        '二下': 0.5,
        '三上': 1.0,
    }
    base_b = grade_difficulty.get(grade, 0)
    
    for pid in problems:
        b = base_b + np.random.normal(0, 0.3)
        problem_difficulty[pid] = np.clip(b, -2, 2)

# 学生能力（正态分布）
student_ability = {}
for sid in range(1, N_STUDENTS + 1):
    theta = np.random.normal(0, 0.8)
    student_ability[sid] = np.clip(theta, -3, 3)

# =============================================
# 3. 按照课程顺序生成数据
# =============================================
print("\n按照课程顺序生成作答序列...")

interactions = []
student_interaction_count = {sid: 0 for sid in range(1, N_STUDENTS + 1)}
skill_interaction_count = {skill: 0 for skill in selected_skills}

# 年级范围的排序
grade_order = ['一上', '一下', '二上', '二下', '三上']

for student_id in range(1, N_STUDENTS + 1):
    theta = student_ability[student_id]
    
    # 每个学生的学习速度不同，可能在某个年级花更长时间
    # 随机决定学生最终到达的学习阶段（或完成全部）
    final_stage = np.random.randint(0, 5)  # 0-4 对应不同的年级
    
    # 每个阶段的题目数（学得越快的学生花越少题目）
    base_problems_per_stage = {
        0: np.random.randint(20, 40),  # 一上
        1: np.random.randint(15, 35),  # 一下
        2: np.random.randint(20, 40),  # 二上
        3: np.random.randint(15, 35),  # 二下
        4: np.random.randint(15, 30),  # 三上
    }
    
    # 生成按课程顺序的作答序列
    all_interactions = []
    
    for stage_idx in range(final_stage + 1):
        # 当前阶段可以学习的年级
        allowed_grades = CurriculumProgress.STAGES[stage_idx]['grades']
        
        # 当前阶段主要学习的是最后一个年级
        primary_grade = allowed_grades[-1]
        
        # 该阶段的题目数
        n_problems_this_stage = base_problems_per_stage[stage_idx]
        
        for _ in range(n_problems_this_stage):
            # 决定选择"当前学习的年级"还是"之前复习的年级"
            if np.random.random() < CURRENT_GRADE_RATIO:
                # 选择当前年级的题目
                selected_grade = primary_grade
            else:
                # 从允许的之前年级中选择（复习）
                available_review_grades = allowed_grades[:-1]
                if available_review_grades:
                    selected_grade = np.random.choice(available_review_grades)
                else:
                    selected_grade = primary_grade
            
            # 从所选年级中随机选择一个技能
            available_skills = CURRICULUM_GRADES[selected_grade]['skills']
            skill = np.random.choice(available_skills)
            
            # 从该技能的题目中选择
            available_problems = skill_to_problems[skill]
            problem_id = np.random.choice(available_problems)
            
            # 生成作答（IRT 模型）
            b = problem_difficulty[problem_id]
            p_correct = sigmoid(theta - b)
            correct = int(np.random.random() < p_correct)
            
            all_interactions.append({
                'studentId': student_id,
                'problemId': problem_id,
                'skill': skill,
                'correct': correct,
                'stage': stage_idx + 1,  # 用于调试
            })
    
    # 将该学生的交互添加到总列表
    interactions.extend(all_interactions)
    
    # 统计
    for inter in all_interactions:
        student_interaction_count[student_id] += 1
        skill_interaction_count[inter['skill']] += 1

df_interactions = pd.DataFrame(interactions)

# 移除调试列
df_interactions = df_interactions.drop('stage', axis=1)

print(f"生成互动记录数：{len(df_interactions):,}")

# =============================================
# 4. 验证时序性
# =============================================
print("\n验证时序性...")

valid_students = 0
total_violations = 0

for student_id in df_interactions['studentId'].unique():
    student_data = df_interactions[df_interactions['studentId'] == student_id]
    skill_sequence = student_data['skill'].tolist()
    
    validation = validate_sequence(skill_sequence)
    if validation['is_valid']:
        valid_students += 1
    total_violations += validation['violations']

print(f"✓ 课程顺序正确的学生：{valid_students}/{len(df_interactions['studentId'].unique())} "
      f"({100*valid_students/len(df_interactions['studentId'].unique()):.1f}%)")
print(f"总时序违反次数：{total_violations:,}")
if total_violations == 0:
    print("✓ 完美！没有任何时序违反")
else:
    print(f"⚠ 平均每个学生：{total_violations/len(df_interactions['studentId'].unique()):.1f} 次违反")

# =============================================
# 5. 统计规范性检查
# =============================================
print("\n=" * 70)
print("📊 统计验证")
print("=" * 70)

print(f"\n各技能互动数：")
for skill in sorted(selected_skills, key=lambda s: SKILL_TO_SEQUENCE_ORDER[s]):
    count = skill_interaction_count[skill]
    grade = SKILL_TO_GRADE[skill]
    status = "✓" if count >= MIN_INTERACTIONS_PER_SKILL else "✗"
    print(f"  {grade:2} {skill:<50}: {count:5,} 筆  [{status}]")

overall_correct_rate = df_interactions['correct'].mean()
print(f"\n全局正确率：{overall_correct_rate:.3f}")

# 按年级的正确率
print("\n按年级的正确率：")
for grade in ['一上', '一下', '二上', '二下', '三上']:
    skills = CURRICULUM_GRADES[grade]['skills']
    grade_data = df_interactions[df_interactions['skill'].isin(skills)]
    if len(grade_data) > 0:
        acc = grade_data['correct'].mean()
        print(f"  {grade}: {acc:.3f}")

# =============================================
# 6. 保存数据
# =============================================
output_path = './synthesized_training_data_v2_curriculum.csv'
df_interactions.to_csv(output_path, index=False)
print(f"\n✓ 新的训练数据已保存到：{output_path}")

# =============================================
# 7. 最终统计
# =============================================
print("\n" + "=" * 70)
print("✅ 生成完成")
print("=" * 70)
print(f"""
数据统计：
  - 互动记录：{len(df_interactions):,} 笔
  - 学生数：{df_interactions['studentId'].nunique()}
  - 技能数：{len(selected_skills)}
  - 题目数：{df_interactions['problemId'].nunique()}
  - 全局正确率：{overall_correct_rate:.1%}

品质保证：
  - 时序一致：{valid_students}/{len(df_interactions['studentId'].unique())} 学生 ({100*valid_students/len(df_interactions['studentId'].nunique()):.0f}%)
  - 最小互动数：{min(skill_interaction_count.values()):,}
  - 最大互动数：{max(skill_interaction_count.values()):,}

✓ 新数据已准备，可用于训练改进的 AKT 模型
""")
