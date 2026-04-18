"""
═════════════════════════════════════════════════════════════════
合成 AKT 訓練數據
基於題庫和 IRT 模型生成學生作答記錄（助力訓練 AUC > 0.75）
═════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
from scipy.special import expit as sigmoid
import os

# =============================================
# 配置參數
# =============================================
RANDOM_SEED = 42
N_STUDENTS = 600  # 學生數（增加以達到每skill 3000+ 互動）
MIN_INTERACTIONS_PER_SKILL = 3000  # 每個skill最少互動數
TARGET_AVG_CORRECTS_PER_STUDENT = 100  # 每個學生平均作答題數（增加到100-150題）

# =============================================
# 1. 讀取題庫
# =============================================
print("讀取題庫...")
df_problems = pd.read_excel('課本題庫.xlsx')

# 篩選題目數 >= 10 的技能
skill_counts = df_problems['skill_id'].value_counts()
selected_skills = skill_counts[skill_counts >= 10].index.tolist()

print(f"選定技能數：{len(selected_skills)}")
print(f"技能列表：{selected_skills}\n")

# 只保留選定技能的題目
df_problems = df_problems[df_problems['skill_id'].isin(selected_skills)].copy()
df_problems = df_problems.reset_index(drop=True)

# 創建問題ID和映射
problems_grouped = df_problems.groupby('skill_id')
skill_to_problems = {}
problem_to_skill = {}

for skill_id in selected_skills:
    problems = df_problems[df_problems['skill_id'] == skill_id]
    problem_ids = problems['id'].tolist()
    skill_to_problems[skill_id] = problem_ids
    for pid in problem_ids:
        problem_to_skill[pid] = skill_id

print(f"選定題目總數：{df_problems.shape[0]}")
print("\n各技能題目數：")
for skill_id in sorted(selected_skills):
    count = len(skill_to_problems[skill_id])
    print(f"  {skill_id}: {count:3d} 題")

# =============================================
# 2. IRT 模型參數設置
# =============================================
np.random.seed(RANDOM_SEED)

# 給每個問題設難度參數 b（預設 0-1 範圍）
# 結合difficulty_level調整
problem_difficulty = {}
for _, row in df_problems.iterrows():
    pid = row['id']
    difficulty_level = row['difficulty_level']
    # 難度等級：1(簡單) -> b=-1, 2(中等) -> b=0, 3(困難) -> b=1
    if pd.isna(difficulty_level):
        b = np.random.normal(0, 0.5)
    else:
        base_b = float(difficulty_level) - 2  # -1, 0, 1
        b = base_b + np.random.normal(0, 0.3)
    problem_difficulty[pid] = np.clip(b, -2, 2)

# 給每個學生設能力參數 θ（normal distribution, mean=0, std=0.8）
student_ability = {}
for sid in range(1, N_STUDENTS + 1):
    theta = np.random.normal(0, 0.8)
    student_ability[sid] = np.clip(theta, -3, 3)

print(f"\n學生能力參數統計:")
abilities = list(student_ability.values())
print(f"  平均：{np.mean(abilities):.3f}")
print(f"  標準差：{np.std(abilities):.3f}")
print(f"  範圍：[{np.min(abilities):.3f}, {np.max(abilities):.3f}]")

# =============================================
# 3. 合成作答記錄
# =============================================
print("\n合成作答記錄...")

interactions = []
student_interaction_count = {sid: 0 for sid in range(1, N_STUDENTS + 1)}
skill_interaction_count = {skill: 0 for skill in selected_skills}

# 為了達到每個skill至少3000筆互動，需要大約 3000 * 17 / N_STUDENTS = 1530 題/學生
# 所以設定每個學生做 80-120 題（分配過程會自動調節）

for student_id in range(1, N_STUDENTS + 1):
    theta = student_ability[student_id]
    
    # 每個學生隨機做 100-150 題（增加題目數以達到目標互動數）
    n_problems_this_student = np.random.randint(100, 151)
    
    # 按技能均衡分配（每個skill 4-10 題）
    problems_pool = []
    for skill_id in selected_skills:
        # 每個skill 4-10 題
        n_this_skill = np.random.randint(4, 11)
        skill_problems = skill_to_problems[skill_id]
        sampled = np.random.choice(skill_problems, 
                                   min(n_this_skill, len(skill_problems)),
                                   replace=True)
        problems_pool.extend(sampled)
    
    # 隨機打亂順序
    np.random.shuffle(problems_pool)
    problems_pool = problems_pool[:n_problems_this_student]
    
    for problem_id in problems_pool:
        skill_id = problem_to_skill[problem_id]
        b = problem_difficulty[problem_id]
        
        # IRT 模型：P(correct) = sigmoid(θ - b)
        p_correct = sigmoid(theta - b)
        correct = int(np.random.random() < p_correct)
        
        interactions.append({
            'studentId': student_id,
            'problemId': problem_id,
            'skill': skill_id,
            'correct': correct,
        })
        
        student_interaction_count[student_id] += 1
        skill_interaction_count[skill_id] += 1

df_interactions = pd.DataFrame(interactions)

print(f"生成互動記錄數：{len(df_interactions):,}")
print(f"\n各技能互動數統計：")
for skill_id in sorted(selected_skills):
    count = skill_interaction_count[skill_id]
    print(f"  {skill_id}: {count:5d} 筆  " 
          f"{'✓ (≥3000)' if count >= MIN_INTERACTIONS_PER_SKILL else '✗ (<3000)'}")

total_per_skill = len(df_interactions) // len(selected_skills)
print(f"\n平均每個skill：{total_per_skill} 筆")

# =============================================
# 4. 統計驗證
# =============================================
print("\n┌─ 作答正確率統計 ─────────────────┐")
overall_correct_rate = df_interactions['correct'].mean()
print(f"│ 全局正確率：{overall_correct_rate:.3f}")

# 按技能的正確率
print("\n│ 各技能正確率：")
for skill_id in sorted(selected_skills):
    skill_data = df_interactions[df_interactions['skill'] == skill_id]
    skill_acc = skill_data['correct'].mean()
    print(f"│   {skill_id}: {skill_acc:.3f}")

# 按學生的正確率分佈
student_accs = df_interactions.groupby('studentId')['correct'].mean()
print(f"\n│ 學生正確率分佈：")
print(f"│   平均：{student_accs.mean():.3f}")
print(f"│   標準差：{student_accs.std():.3f}")
print(f"│   範圍：[{student_accs.min():.3f}, {student_accs.max():.3f}]")
print("└────────────────────────────────────┘")

# =============================================
# 5. 儲存為 CSV
# =============================================
output_path = './synthesized_training_data.csv'
df_interactions.to_csv(output_path, index=False)
print(f"\n✓ 訓練數據已儲存到：{output_path}")
print(f"\nCSV 內容預覽（前 10 行）：")
print(df_interactions.head(10).to_string())

# =============================================
# 6. 生成統計總結
# =============================================
summary = {
    'Total Interactions': len(df_interactions),
    'N Students': N_STUDENTS,
    'N Skills': len(selected_skills),
    'N Problems': df_interactions['problemId'].nunique(),
    'Overall Correct Rate': round(overall_correct_rate, 4),
    'Avg Interactions per Student': round(len(df_interactions) / N_STUDENTS, 1),
    'Avg Interactions per Skill': round(len(df_interactions) / len(selected_skills), 1),
}

print("\n" + "="*50)
print("生成數據統計總結")
print("="*50)
for key, value in summary.items():
    print(f"{key}: {value}")
print("="*50)
