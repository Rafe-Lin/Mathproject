# 📊 深度分析：Math 分数偏低原因

## 问题: Math 分数只有 28.45/50

### 当前分数分布

```
Ab2/Ab3 - L4 (数学质量) 详细得分:
├─ L4.1 数值正确性: 5.00/5  ✅ 满分！
├─ L4.2 视觉格式:    4.00/5  ⚠️ 扣 1 分
├─ L4.3 数学对象:    5.00/5  ✅ 满分！(Ab2/Ab3 提升)
└─ L4.4 MQI质量:     0.20/5  ❌ 仅 4%！

Math Total = L3.2(外部测试) + L4(数学质量) + Complexity
           = 3.00 + 15.45 + ? 
           = 28.45/50
```

---

## 🔍 问题分析

### 1. **MQI (Mathematical Quality Index) 极低**

**当前: 0.20/5 (仅 4%)**

MQI 评分项目包括：
- ❌ **题目多样性** - 生成逻辑过于简单/固定
- ❌ **数学复杂度** - Level 参数未充分利用
- ❌ **教学价值** - 缺乏认知挑战梯度

**代码问题示例：**
```python
def generate(level=1, **kwargs):
    terms1 = []
    for i in range(3, 5):  # ❌ 固定循环！每次都生成 2 项
        coeff = 1 + level * i
        radicand = 2 + level * i * 2
        # ...
```

**问题：**
- 题目结构完全固定（永远是 2 项根式 + 1 个乘法）
- Level 参数只影响系数大小，不影响题型结构
- 缺乏随机性（每次运行几乎一样）

---

### 2. **视觉格式扣分 (-1 分)**

**当前: 4.00/5**

可能原因：
- LaTeX 格式不完全符合标准
- 括号使用不当
- 化简过程展示不清晰

**代码检查：**
```python
part2_str = f"{k}(\\sqrt{{{rad1}}} + \\sqrt{{{rad2}}})"
# 可能问题: 缺少 $$...$$ 标记，或括号嵌套不当
```

---

### 3. **复杂度指标偏低**

```python
avg_complexity_math_ops: 1.0          # 数学操作数量
avg_complexity_inference_steps: 1.0   # 推理步骤数
avg_complexity_ast_nodes: 3507.0      # AST 节点（包含 Domain Libs）
avg_complexity_loop_depth: 1.0        # 循环深度
```

**解读：**
- 数学操作数量太少（只有 1 个主要运算）
- 推理步骤单一（没有多步骤化简）
- 复杂度不足以挑战学生

---

## 💡 改进建议

### A. **提升 MQI 分数 (目标: 3-4/5)**

#### 1. **增加题型多样性**
```python
def generate(level=1, **kwargs):
    # 随机选择题型
    question_types = [
        'addition_only',      # 纯加减根式
        'multiplication',     # 乘法展开
        'mixed_operations'    # 混合运算
    ]
    q_type = random.choice(question_types)
    
    # 随机项数 (2-5 项)
    num_terms = random.randint(2, 3 + level)
    
    # ...
```

#### 2. **Level 参数影响结构**
```python
if level == 1:
    # 简单: 2-3 项，只加减
    num_terms = random.randint(2, 3)
    operations = ['+', '-']
elif level == 2:
    # 中等: 3-4 项，加入一个乘法
    num_terms = random.randint(3, 4)
    has_multiplication = True
else:
    # 困难: 4-5 项，多个乘法或分数
    num_terms = random.randint(4, 5)
    has_complex_fraction = True
```

#### 3. **增加随机性**
```python
# 随机系数范围
coeff_range = range(1, 5 + level * 2)

# 随机根指数
radicand_pool = [2, 3, 5, 6, 8, 12, 18, 24, 27, 32, 48, 50, 72]
radicands = random.sample(radicand_pool, num_terms)
```

---

### B. **修复视觉格式 (目标: 5/5)**

#### 1. **统一 LaTeX 格式**
```python
# 确保所有数学式都用 $$...$$ 或 $...$ 包裹
question_text = f'化簡 $$({part1_str}) + {part2_str}$$'
# ✅ 正确！

# 检查答案格式
correct_answer = RadicalOps.format_expression(simplified_dict)
# 需要确保 format_expression 返回标准 LaTeX 格式
```

#### 2. **括号规范**
```python
# 乘法项需要适当的括号
if has_parentheses:
    term = f"({inner_expr})"
else:
    term = inner_expr
```

---

### C. **提升数学复杂度**

#### 1. **多步骤化简**
```python
# 示例: 需要先展开乘法，再合并同类项
# ($\sqrt{18} + \sqrt{50}$)($\sqrt{3} - \sqrt{2}$)
# = $\sqrt{54} - \sqrt{36} + \sqrt{150} - \sqrt{100}$
# = $3\sqrt{6} - 6 + 5\sqrt{6} - 10$
# = $8\sqrt{6} - 16$
```

#### 2. **增加推理步骤**
```python
# Record intermediate steps for MQI
steps = []
steps.append(f"展开: {expanded_expr}")
steps.append(f"化简: {simplified_expr}")
steps.append(f"合并: {final_expr}")
```

---

## 🎯 预期改进效果

### 修改前 (当前)
```
L4.4 MQI: 0.20/5
Math Total: 28.45/50
```

### 修改后 (预期)
```
L4.4 MQI: 3.50/5  (+3.30)
L4.2 视觉: 5.00/5  (+1.00)
Math Total: 32.75/50  (+4.30)

总分提升: 73.95 → 78.25
```

---

## ✅ 行动清单

### 优先级 1 (必须)
- [ ] 修改 `generate()` 函数，增加题型随机性
- [ ] 让 `level` 参数影响题目结构（不只是系数大小）
- [ ] 增加根式项数的随机性 (2-5 项)

### 优先级 2 (推荐)
- [ ] 检查并统一 LaTeX 格式
- [ ] 增加多步骤化简题型
- [ ] 添加认知梯度设计

### 优先级 3 (可选)
- [ ] 记录中间步骤用于 MQI 评估
- [ ] 增加题目类型选项 (kwargs)
- [ ] 添加题目难度自适应

---

## 📝 修改建议代码模板

```python
def generate(level=1, **kwargs):
    # [1] 随机化参数
    num_terms = random.randint(2, min(3 + level, 5))
    has_multiplication = (level >= 2) and random.random() > 0.5
    
    # [2] 随机选择根指数（避免重复）
    radicand_pool = [2, 3, 5, 6, 8, 12, 18, 24, 27, 32, 48, 50, 72]
    radicands = random.sample(radicand_pool, num_terms)
    
    # [3] 随机系数
    coeffs = [random.randint(-level-2, level+3) for _ in range(num_terms)]
    
    # [4] 构建题目
    terms1 = []
    for i, (coeff, radicand) in enumerate(zip(coeffs, radicands)):
        if coeff == 0:
            continue
        is_first = (len(terms1) == 0)
        terms1.append(RadicalOps.format_term_unsimplified(coeff, radicand, is_first))
    
    # [5] 可选的乘法项
    if has_multiplication:
        k = random.randint(2, 3 + level)
        rad1, rad2 = random.sample([2, 3, 5, 6], 2)
        part2_str = f"{k}(\\sqrt{{{rad1}}} \\pm \\sqrt{{{rad2}}})"
        question_text = f'化簡 $$({part1_str}) + {part2_str}$$'
    else:
        question_text = f'化簡 $${part1_str}$$'
    
    # [6] 计算正确答案（需要根据实际项重新计算）
    # ...
    
    return {
        'question_text': question_text,
        'answer': '',
        'correct_answer': correct_answer,
        'mode': 1
    }
```

---

**总结: 当前代码的主要问题是"太固定、太简单"，导致 MQI 评分极低。需要增加随机性和多样性。**
