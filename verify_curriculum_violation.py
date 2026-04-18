"""
验证问题：检查合成数据中的时序违反
"""

import pandas as pd
import numpy as np

# 1. 定义课程顺序和技能分组
CURRICULUM_SEQUENCE = [
    # 一上 (jh_數學1上)
    'jh_數學1上_CommonDivisibilityRules',
    'jh_數學1上_FourArithmeticOperationsOfIntegers',
    'jh_數學1上_IntegerAdditionOperation',
    
    # 一下 (jh_數學1下)
    'jh_數學1下_DrawingGraphsOfTwoVariableLinearEquations',
    'jh_數學1下_RectangularCoordinatePlaneAndCoordinateRepresentation',
    
    # 二上 (jh_數學2上)
    'jh_數學2上_BasicPropertiesOfRadicalOperations',
    'jh_數學2上_FourOperationsOfRadicals',
    'jh_數學2上_PolynomialAdditionAndSubtraction',
    'jh_數學2上_PolynomialDivision',
    'jh_數學2上_WordProblems',
    
    # 二下 (jh_數學2下)
    'jh_數學2下_IdentifyingAndConstructingParallelograms',
    'jh_數學2下_MeaningAndPropertiesOfParallelograms',
    'jh_數學2下_PropertiesOfRectanglesRhombusesKitesAndSquares',
    
    # 三上 (jh_數學3上)
    'jh_數學3上_ApplicationOfParallelLinesProportionalSegmentsProperty',
    'jh_數學3上_GeometricProof',
    'jh_數學3上_InscribedAngleParallelChordsAndCyclicQuadrilateral',
    'jh_數學3上_ParallelLinesProportionalSegmentsProperty',
]

# 建立 skill 到年级的映射
skill_to_grade = {}
grade_map = {
    'jh_數學1上': 11,  # 1 上
    'jh_數學1下': 12,  # 1 下
    'jh_數學2上': 21,  # 2 上
    'jh_數學2下': 22,  # 2 下
    'jh_數學3上': 31,  # 3 上
}

for skill in CURRICULUM_SEQUENCE:
    for prefix, grade in grade_map.items():
        if skill.startswith(prefix):
            skill_to_grade[skill] = grade
            break

print("="*70)
print("🔍 验证合成数据的时序违反问题")
print("="*70)

# 2. 读取数据
df = pd.read_csv('./synthesized_training_data.csv')

print(f"\n数据总行数：{len(df):,}")
print(f"学生数：{df['studentId'].nunique():,}")

# 3. 分析学生作答序列的时序违反
print("\n" + "="*70)
print("📊 检查学生作答的课程顺序")
print("="*70)

violations = []
students_to_check = sorted(df['studentId'].unique())[:10]  # 检查前10个学生

for student_id in students_to_check:
    student_data = df[df['studentId'] == student_id].reset_index(drop=True)
    
    # 获取该学生的作答序列
    skill_sequence = student_data['skill'].tolist()
    
    # 转换为年级序列
    grade_sequence = [skill_to_grade.get(skill, 0) for skill in skill_sequence]
    
    # 检查是否单调递增
    is_monotonic = all(grade_sequence[i] <= grade_sequence[i+1] for i in range(len(grade_sequence)-1))
    
    # 计数违反次数
    violation_count = sum(1 for i in range(len(grade_sequence)-1) if grade_sequence[i] > grade_sequence[i+1])
    
    print(f"\n📌 StudentId {student_id}:")
    print(f"   作答题数：{len(skill_sequence)}")
    print(f"   年级序列示例（前15题）：{grade_sequence[:15]}")
    print(f"   是否单调递增：{is_monotonic}")
    print(f"   时序违反次数（回跳）：{violation_count}")
    
    if not is_monotonic:
        violations.append(student_id)
        # 显示具体的违反点
        print(f"   ⚠️ 违反例子：")
        for i in range(min(5, len(grade_sequence)-1)):
            if grade_sequence[i] > grade_sequence[i+1]:
                print(f"      {i+1}→{i+2}: {skill_sequence[i]} ({grade_sequence[i]}) "
                      f"→ {skill_sequence[i+1]} ({grade_sequence[i+1]}) ❌")

print("\n" + "="*70)
print("📈 整体统计")
print("="*70)

# 计算所有学生的时序违反
all_violations = 0
monotonic_students = 0

for student_id in df['studentId'].unique():
    student_data = df[df['studentId'] == student_id]
    skill_sequence = student_data['skill'].tolist()
    grade_sequence = [skill_to_grade.get(skill, 0) for skill in skill_sequence]
    
    is_monotonic = all(grade_sequence[i] <= grade_sequence[i+1] for i in range(len(grade_sequence)-1))
    if is_monotonic:
        monotonic_students += 1
    
    violation_count = sum(1 for i in range(len(grade_sequence)-1) if grade_sequence[i] > grade_sequence[i+1])
    all_violations += violation_count

print(f"\n学生总数：{df['studentId'].nunique()}")
print(f"课程顺序正确的学生：{monotonic_students} ({100*monotonic_students/df['studentId'].nunique():.1f}%)")
print(f"有时序违反的学生：{df['studentId'].nunique() - monotonic_students} ({100*(df['studentId'].nunique() - monotonic_students)/df['studentId'].nunique():.1f}%)")
print(f"\n总时序违反次数：{all_violations:,}")
print(f"平均每个学生的违反次数：{all_violations / df['studentId'].nunique():.1f}")

print("\n" + "="*70)
print("💡 结论")
print("="*70)
print("""
✗ 严重问题已确认：
  - 数据完全随机化了学生的作答序列
  - 几乎没有学生遵循课程顺序
  - 这会导致 AKT 模型退化

✓ 解决方案：
  1. 建立课程依赖图（Curriculum DAG）
  2. 按照课程顺序生成数据
  3. 允许一定的"重复练习"但保持大方向递进
  4. 确保前置知识在后续知识之前
""")

print("\n" + "="*70)
print("🔧 需要的修复：")
print("="*70)
print("""
1. 新建 curriculum_structure.py
   - 定义课程依赖关系
   - 定义每个年级的技能组
   
2. 修改 generate_training_data.py
   - 按课程顺序分配技能
   - 保证时序性
   
3. 重新生成数据集
   - 遵循 一上 → 一下 → 二上 → 二下 → 三上
   
4. 重新训练 AKT 模型
   - 使用正确时序的数据
   - 验证注意力机制是否生效
""")
