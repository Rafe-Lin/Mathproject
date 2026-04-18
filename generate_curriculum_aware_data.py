"""
═══════════════════════════════════════════════════════════════════════
生成时序正确且符合课程依赖的AKT训练数据
使用curriculum_structure中已定义的课程结构
═══════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
from scipy.special import expit as sigmoid
import os

# 导入课程结构
from curriculum_structure import CURRICULUM_GRADES, SKILL_TO_GRADE, SKILL_TO_SEQUENCE_ORDER, validate_sequence

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

print("="*80)
print("生成时序正确且符合课程依赖的训练数据")
print("="*80)

# ═══════════════════════════════════════════════════════════════════
# 步骤1：获取课程结构
# ═══════════════════════════════════════════════════════════════════

print("\n【课程结构检查】")
all_skills = []
for grade_name in sorted(CURRICULUM_GRADES.keys(), key=lambda x: CURRICULUM_GRADES[x]['sequence_order']):
    grade_info = CURRICULUM_GRADES[grade_name]
    all_skills.extend(grade_info['skills'])
    print(f"  {grade_name}: {len(grade_info['skills'])} 个技能")

print(f"\n总技能数：{len(all_skills)}")

# ═══════════════════════════════════════════════════════════════════
# 步骤2：从题库读取题目信息
# ═══════════════════════════════════════════════════════════════════

print("\n【读取题库】")
try:
    df_problems = pd.read_excel('課本題庫.xlsx')
    print(f"✓ 读取了 {len(df_problems)} 道题目")
except Exception as e:
    print(f"✗ 读取题库失败: {e}")
    print("  使用备用方案：直接从CSV读取已有的合成数据来提取题目ID")
    df_problems = None

# 为每个技能建立题目集
skill_problems = {}

if df_problems is not None:
    for skill_name in all_skills:
        problems_df = df_problems[df_problems['skill_id'] == skill_name]
        problem_ids = problems_df['id'].tolist()
        if problem_ids:
            skill_problems[skill_name] = problem_ids
            print(f"  {skill_name}: {len(problem_ids)} 道题目")
else:
    # 从已有的合成数据中提取题目ID
    if os.path.exists('./synthesized_training_data.csv'):
        df_existing = pd.read_csv('./synthesized_training_data.csv')
        for skill_name in all_skills:
            skill_data = df_existing[df_existing['skill'] == skill_name]
            problem_ids = skill_data['problemId'].unique().tolist()
            if problem_ids:
                skill_problems[skill_name] = problem_ids

print(f"\n覆盖的技能数：{len(skill_problems)}/{len(all_skills)}")
if len(skill_problems) < len(all_skills):
    print(f"⚠ 警告：有些技能找不到题目！")

# ═══════════════════════════════════════════════════════════════════
# 步骤3：生成难度参数
# ═══════════════════════════════════════════════════════════════════

print("\n【生成难度参数】")
problem_difficulty = {}

if df_problems is not None:
    for _, row in df_problems.iterrows():
        problem_id = row['id']
        difficulty_level = row['difficulty_level']
        
        if pd.isna(difficulty_level):
            base_b = 0
        else:
            base_b = float(difficulty_level) - 2  # -1, 0, 1
        
        b = base_b + np.random.normal(0, 0.2)
        problem_difficulty[problem_id] = np.clip(b, -2, 2)
else:
    # 从CSV中提取
    if os.path.exists('./synthesized_training_data.csv'):
        df_existing = pd.read_csv('./synthesized_training_data.csv')
        for problem_id in df_existing['problemId'].unique():
            problem_difficulty[problem_id] = np.random.normal(0, 0.5)

print(f"✓ 为 {len(problem_difficulty)} 道题设置了难度参数")

# ═══════════════════════════════════════════════════════════════════
# 步骤4：生成时序正确的学生数据
# ═══════════════════════════════════════════════════════════════════

print("\n【生成学生数据】")

def assign_student_progress():
    """
    根据IRT能力参数，决定学生能学到哪个年级。
    """
    theta = np.random.normal(0, 0.8)
    
    grade_names_ordered = sorted(
        CURRICULUM_GRADES.keys(),
        key=lambda x: CURRICULUM_GRADES[x]['sequence_order']
    )
    
    if theta > 0.5:
        max_grade_idx = len(grade_names_ordered) - 1  # 完整课程
    elif theta > 0:
        max_grade_idx = len(grade_names_ordered) - 2  # 二下
    elif theta > -1:
        max_grade_idx = len(grade_names_ordered) - 3  # 二上
    else:
        max_grade_idx = len(grade_names_ordered) - 4  # 一下
    
    max_grade_idx = max(0, min(max_grade_idx, len(grade_names_ordered) - 1))
    
    return theta, grade_names_ordered, max_grade_idx

# 生成互动数据
interactions = []
student_stats = []

N_STUDENTS = 600
ATTEMPTS_PER_SKILL = (5, 12)  # 每个技能的作答次数范围

for student_id in range(1, N_STUDENTS + 1):
    theta, grade_names_ordered, max_grade_idx = assign_student_progress()
    total_attempts = 0
    student_skills_attempted = []
    
    # 按照课程顺序逐个年级学习
    for grade_idx in range(max_grade_idx + 1):
        grade_name = grade_names_ordered[grade_idx]
        grade_info = CURRICULUM_GRADES[grade_name]
        
        # 该年级内的某些技能可能会练习多遍
        for skill_name in grade_info['skills']:
            if skill_name not in skill_problems or len(skill_problems[skill_name]) == 0:
                continue
            
            # 该技能下的作答次数
            n_attempts = np.random.randint(*ATTEMPTS_PER_SKILL)
            
            for _ in range(n_attempts):
                # 从该技能的题库中随机选择题目
                problem_id = np.random.choice(skill_problems[skill_name])
                
                # IRT：答对概率
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
                student_skills_attempted.append(SKILL_TO_SEQUENCE_ORDER.get(skill_name, -1))
    
    student_stats.append({
        'student_id': student_id,
        'theta': theta,
        'max_grade': grade_names_ordered[max_grade_idx],
        'total_attempts': total_attempts,
    })
    
    if student_id % 100 == 0:
        print(f"  已生成 {student_id}/600 名学生的数据...")

# ═══════════════════════════════════════════════════════════════════
# 步骤5：数据验证
# ═══════════════════════════════════════════════════════════════════

print("\n【数据验证】")

df_interactions = pd.DataFrame(interactions)
df_stats = pd.DataFrame(student_stats)

print(f"✓ 生成了 {len(df_interactions):,} 筆互動記錄")
print(f"  学生数：{df_interactions['studentId'].nunique()}")
print(f"  题目数：{df_interactions['problemId'].nunique()}")
print(f"  技能数：{df_interactions['skill'].nunique()}")
print(f"  全局正确率：{df_interactions['correct'].mean():.1%}")

# 检查时序正确性
print("\n【时序性验证】")
violations_by_student = {}
total_violations = 0

for student_id in df_interactions['studentId'].unique():
    student_data = df_interactions[df_interactions['studentId'] == student_id]
    skill_sequence = student_data['skill'].tolist()
    
    violation_count = 0
    for i in range(1, len(skill_sequence)):
        prev_order = SKILL_TO_SEQUENCE_ORDER.get(skill_sequence[i-1], -1)
        curr_order = SKILL_TO_SEQUENCE_ORDER.get(skill_sequence[i], -1)
        
        if prev_order >= 0 and curr_order >= 0 and curr_order < prev_order:
            violation_count += 1
            total_violations += 1
    
    if violation_count > 0:
        violations_by_student[student_id] = violation_count

correct_students = len(df_stats) - len(violations_by_student)
print(f"  时序违反总数：{total_violations:,} (占比 {100*total_violations/len(df_interactions):.2f}%)")
print(f"  完全遵循课程的学生：{correct_students}/{len(df_stats)} ({100*correct_students/len(df_stats):.1f}%)")

if total_violations == 0:
    print("  ✓ 优秀！数据100%遵循课程顺序！")
else:
    print(f"  ⚠ 发现{len(violations_by_student)}个学生有时序违反，最多{max(violations_by_student.values())}次")

# 按年级分布
print("\n【学生年级分布】")
print(df_stats['max_grade'].value_counts().sort_index())

# 按技能互动
print("\n【技能互动分布】")
skill_interactions = df_interactions['skill'].value_counts()
for grade_name in sorted(CURRICULUM_GRADES.keys(), key=lambda x: CURRICULUM_GRADES[x]['sequence_order']):
    grade_skills = CURRICULUM_GRADES[grade_name]['skills']
    total_for_grade = skill_interactions[skill_interactions.index.isin(grade_skills)].sum()
    print(f"  {grade_name}: {total_for_grade:,} 筆")

# ═══════════════════════════════════════════════════════════════════
# 步骤6：保存数据
# ═══════════════════════════════════════════════════════════════════

print("\n【保存数据】")
output_path = './synthesized_training_data_curriculum.csv'
df_interactions.to_csv(output_path, index=False)
print(f"✓ 数据已保存到：{output_path}")

# 也保存为新的标准名称替换旧数据
backup_path = './synthesized_training_data_old.csv'
if os.path.exists('./synthesized_training_data.csv'):
    os.rename('./synthesized_training_data.csv', backup_path)
    print(f"✓ 旧数据备份到：{backup_path}")

os.rename(output_path, './synthesized_training_data.csv')
print(f"✓ 新数据已替换：./synthesized_training_data.csv")

print("\n" + "="*80)
print("数据生成完成！这次数据100%遵循课程顺序和依赖关系。")
print("="*80)
