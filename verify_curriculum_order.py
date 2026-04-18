"""
===============================================================
验证脚本：检查合成数据中的时序违反
===============================================================
"""

import pandas as pd
import numpy as np
import os

# 确认当前目录
print(f"当前目录: {os.getcwd()}\n")

# 定义课程结构（按标准台湾课纲）
CURRICULUM = {
    "一上": [
        "jh_數學1上_CommonDivisibilityRules",
        "jh_數學1上_FourArithmeticOperationsOfIntegers",
        "jh_數學1上_IntegerAdditionOperation",
    ],
    "一下": [
        "jh_數學1下_RectangularCoordinatePlaneAndCoordinateRepresentation",
        "jh_數學1下_DrawingGraphsOfTwoVariableLinearEquations",
    ],
    "二上": [
        "jh_數學2上_BasicPropertiesOfRadicalOperations",
        "jh_數學2上_FourOperationsOfRadicals",
        "jh_數學2上_PolynomialAdditionAndSubtraction",
        "jh_數學2上_PolynomialDivision",
        "jh_數學2上_WordProblems",
    ],
    "二下": [
        "jh_數學2下_MeaningAndPropertiesOfParallelograms",
        "jh_數學2下_IdentifyingAndConstructingParallelograms",
        "jh_數學2下_PropertiesOfRectanglesRhombusesKitesAndSquares",
    ],
    "三上": [
        "jh_數學3上_ParallelLinesProportionalSegmentsProperty",
        "jh_數學3上_ApplicationOfParallelLinesProportionalSegmentsProperty",
        "jh_數學3上_GeometricProof",
        "jh_數學3上_InscribedAngleParallelChordsAndCyclicQuadrilateral",
    ],
}

# 构建反向映射
SEMESTER_MAP = {}
CURRICULUM_ORDER = {}
order = 0
for semester, skills in CURRICULUM.items():
    for skill in skills:
        SEMESTER_MAP[skill] = semester
        CURRICULUM_ORDER[skill] = order
        order += 1

print("="*70)
print("数据时序性验证报告")
print("="*70)

# 加载数据
df = pd.read_csv('./synthesized_training_data.csv')
print(f"\n✓ 加载数据: {len(df):,} 筆互動記錄")

# 统计违反情况
violations = []
students_with_violations = set()

for student_id in df['studentId'].unique():
    student_data = df[df['studentId'] == student_id].copy()
    skills_sequence = student_data['skill'].values
    
    for i in range(1, len(skills_sequence)):
        prev_skill = skills_sequence[i-1]
        curr_skill = skills_sequence[i]
        
        # 检查是否是已知技能
        if prev_skill not in CURRICULUM_ORDER or curr_skill not in CURRICULUM_ORDER:
            continue
        
        prev_order = CURRICULUM_ORDER[prev_skill]
        curr_order = CURRICULUM_ORDER[curr_skill]
        
        # 检查时序
        if curr_order < prev_order:
            violations.append({
                'student': student_id,
                'prev_skill': prev_skill,
                'prev_semester': SEMESTER_MAP.get(prev_skill, 'unknown'),
                'curr_skill': curr_skill,
                'curr_semester': SEMESTER_MAP.get(curr_skill, 'unknown'),
            })
            students_with_violations.add(student_id)

print(f"\n【时序违反统计】")
print(f"  总违反次数: {len(violations):,} (占比 {100*len(violations)/len(df):.1f}%)")
print(f"  受影响学生: {len(students_with_violations):,} / {df['studentId'].nunique()} ({100*len(students_with_violations)/df['studentId'].nunique():.1f}%)")

if violations:
    print(f"\n【违反示例】(前 10 条):")
    for i, v in enumerate(violations[:10], 1):
        print(f"  {i}. 学生 {v['student']:3d}: {v['prev_semester']}__{v['prev_skill'].split('_')[-1][:20]:20s} "
              f"→ {v['curr_semester']}__{v['curr_skill'].split('_')[-1][:20]:20s}")

# 检查正确顺序的学生
correct_students = []
for student_id in df['studentId'].unique():
    student_data = df[df['studentId'] == student_id].copy()
    skills_sequence = student_data['skill'].values
    
    is_correct = True
    for i in range(1, len(skills_sequence)):
        prev_order = CURRICULUM_ORDER.get(skills_sequence[i-1], -1)
        curr_order = CURRICULUM_ORDER.get(skills_sequence[i], -1)
        
        if prev_order >= 0 and curr_order >= 0 and curr_order < prev_order:
            is_correct = False
            break
    
    if is_correct:
        correct_students.append(student_id)

print(f"\n【时序正确学生】")
print(f"  完全正确: {len(correct_students)} / {df['studentId'].nunique()} ({100*len(correct_students)/df['studentId'].nunique():.1f}%)")

print("\n" + "="*70)
print("结论：数据时序性已严重破坏！")
print("="*70)
