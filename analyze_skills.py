import pandas as pd

df = pd.read_excel('課本題庫.xlsx')

# 篩選題目數 >= 10 的 skills
skill_counts = df['skill_id'].value_counts()
large_skills = skill_counts[skill_counts >= 10]

print(f"題目數 >= 10 的技能：{len(large_skills)} 個\n")
print(large_skills.sort_values(ascending=False).head(20))
print(f"\n最小：{large_skills.min()}, 最大：{large_skills.max()}")
