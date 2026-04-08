#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 KG 数据加载器"""

from core.kg_data_loader import get_kg_loader

print("=" * 60)
print("测试知识图谱 JSON 数据加载器")
print("=" * 60)

# 初始化加载器
loader = get_kg_loader()
print("\n✓ 加载器初始化成功")

# 1. 获取所有年级
grades = loader.get_all_grades()
print(f"\n1. 发现 {len(grades)} 个年级:")
for grade in grades:
    print(f"   - {grade}")

# 2. 获取国一上的单元
units = loader.get_units_for_grade("國一上")
print(f"\n2. 國一上有 {len(units)} 个单元:")
for unit_id in list(units.keys())[:5]:  # 只显示前5个
    print(f"   - {unit_id}")
if len(units) > 5:
    print(f"   ... 还有 {len(units) - 5} 个")

# 3. 获取完整年级的图谱数据
graph = loader.get_graph_data("國一上")
print(f"\n3. 國一上的图谱数据:")
print(f"   - 节点数: {len(graph['nodes'])}")
print(f"   - 连接数: {len(graph['links'])}")

# 4. 获取特定单元的图谱数据
first_unit = list(units.keys())[0]
unit_graph = loader.get_graph_data("國一上", first_unit)
print(f"\n4. {first_unit} 的图谱数据:")
print(f"   - 节点数: {len(unit_graph['nodes'])}")
print(f"   - 连接数: {len(unit_graph['links'])}")

# 5. 获取节点示例
if unit_graph['nodes']:
    sample_node = unit_graph['nodes'][0]
    print(f"\n5. 节点示例:")
    print(f"   - ID: {sample_node.get('id')}")
    print(f"   - 名称: {sample_node.get('name')}")
    print(f"   - 级别: {sample_node.get('level')}")
    print(f"   - 难度: {sample_node.get('difficulty', 'N/A')}")

# 6. 获取难度分布
difficulty_dist = loader.get_difficulty_distribution("國一上")
print(f"\n6. 國一上的难度分布:")
for difficulty in sorted(difficulty_dist.keys()):
    count = difficulty_dist[difficulty]
    print(f"   - 难度 {difficulty}: {count} 个节点")

# 7. 搜索功能
search_results = loader.search_nodes("國一上", "正負")
print(f"\n7. 搜索 '正負' 找到 {len(search_results)} 个结果:")
for i, result in enumerate(search_results[:3]):
    print(f"   {i+1}. {result.get('name')}")
if len(search_results) > 3:
    print(f"   ... 还有 {len(search_results) - 3} 个")

print("\n" + "=" * 60)
print("✓ 所有测试通过!")
print("=" * 60)
