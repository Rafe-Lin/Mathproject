# 🔍 evals.json 可行性分析

## 当前文件分析

**文件路径:** `agent_skills/jh_數學2上_FourOperationsOfRadicals/evals.json`

---

## ❌ 关键问题

### 1. **JSON 格式错误** (致命)

```json
{
    "evals": [
        // Easy 組 (4 個，weight 1.0)  ← ❌ JSON 不支持 // 注释！
        {
            "eval_id": "radicals_easy_add",
            ...
        }
    ]
}
```

**问题:** 标准 JSON 不支持 `//` 注释，会导致解析失败。

**错误信息预期:**
```
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
```

**解决方案:** 删除所有注释，或使用 JSON5/JSONC 解析器。

---

### 2. **ablation_target 字段错误** (致命)

```json
"ablation_target": "All"  ← ❌ benchmark.py 不识别 "All"
```

**benchmark.py 期望值:**
- `"Ab1"` - Bare prompt (无 Healer)
- `"Ab2"` - Engineered prompt + heal_minimal()
- `"Ab3"` - Engineered prompt + heal() + AST

**当前问题:**
- 所有 12 个测试都设置为 `"All"`
- benchmark.py 会将其识别为 `"Ab3"` (默认值)
- **无法测试 Ab1 和 Ab2！**

---

### 3. **healer_type 字段未使用**

```json
"healer_type": "All"  ← ⚠️ benchmark.py 不读取此字段
```

**说明:**
- benchmark.py 只根据 `ablation_target` 决定使用哪个 Healer
- `healer_type` 字段会被忽略

---

### 4. **weight 字段未实现**

```json
"weight": 1.0  ← ⚠️ benchmark.py 不支持加权评分
```

**说明:**
- benchmark.py 和 evaluate_mcri.py 都没有实现权重系统
- 所有测试会被平等对待
- 这个字段目前无效

---

## ✅ 正确的部分

### 1. **generation_kwargs 字段** ✅

```json
"generation_kwargs": {"level": 1}  ← ✅ 会传递给 generate()
```

**说明:**
- 这个字段会被正确传递给 `generate(level=1, **kwargs)`
- 可以控制题目难度

### 2. **timeout_seconds 字段** ✅

```json
"timeout_seconds": 180  ← ✅ 但 benchmark.py 可能不使用
```

**说明:**
- 字段存在，但需要检查是否被使用
- call_ai_with_retry() 有自己的超时逻辑

### 3. **测试数量扩展** ✅

```
Easy: 4 个测试
Medium: 5 个测试
Hard: 3 个测试
总计: 12 个测试
```

**说明:**
- 从原来的 10 个扩展到 12 个
- 难度分层合理

---

## 🔧 修复方案

### 方案 A: 最小修复（推荐）

**保留原有的 Ab1/Ab2/Ab3 设计**

```json
{
    "evals": [
        {
            "eval_id": "math_2a_radicals_ab1",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab1",
            "description": "簡單根式加減 - Ab1",
            "timeout_seconds": 180,
            "generation_kwargs": {"level": 1}
        },
        {
            "eval_id": "math_2a_radicals_ab1_L2",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab1",
            "description": "中等根式運算 - Ab1",
            "timeout_seconds": 240,
            "generation_kwargs": {"level": 2}
        },
        {
            "eval_id": "math_2a_radicals_ab2",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab2",
            "description": "簡單根式加減 - Ab2",
            "timeout_seconds": 180,
            "generation_kwargs": {"level": 1}
        },
        {
            "eval_id": "math_2a_radicals_ab2_L1_b",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab2",
            "description": "簡單根式乘法 - Ab2",
            "timeout_seconds": 180,
            "generation_kwargs": {"level": 1}
        },
        {
            "eval_id": "math_2a_radicals_ab2_L2",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab2",
            "description": "中等根式運算 - Ab2",
            "timeout_seconds": 240,
            "generation_kwargs": {"level": 2}
        },
        {
            "eval_id": "math_2a_radicals_ab2_L2_b",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab2",
            "description": "中等複雜混合 - Ab2",
            "timeout_seconds": 240,
            "generation_kwargs": {"level": 2}
        },
        {
            "eval_id": "math_2a_radicals_ab3",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab3",
            "description": "簡單根式加減 - Ab3",
            "timeout_seconds": 180,
            "generation_kwargs": {"level": 1}
        },
        {
            "eval_id": "math_2a_radicals_ab3_L1_b",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab3",
            "description": "簡單根式乘法 - Ab3",
            "timeout_seconds": 180,
            "generation_kwargs": {"level": 1}
        },
        {
            "eval_id": "math_2a_radicals_ab3_L2",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab3",
            "description": "中等根式運算 - Ab3",
            "timeout_seconds": 240,
            "generation_kwargs": {"level": 2}
        },
        {
            "eval_id": "math_2a_radicals_ab3_L2_b",
            "skill_name": "jh_數學2上_FourOperationsOfRadicals",
            "ablation_target": "Ab3",
            "description": "中等複雜混合 - Ab3",
            "timeout_seconds": 240,
            "generation_kwargs": {"level": 2}
        }
    ]
}
```

**优点:**
- ✅ 保持 Ab1/Ab2/Ab3 对比实验设计
- ✅ 可以测试 Prompt 工程化效果（Ab1→Ab2）
- ✅ 可以测试 Healer 效果（Ab2→Ab3）
- ✅ 标准 JSON 格式，无注释

---

### 方案 B: 适配新格式（需要修改代码）

如果要使用 `"ablation_target": "All"` 和权重系统，需要：

1. **修改 benchmark.py:**
   ```python
   # 支持 "All" 自动展开为 Ab1/Ab2/Ab3
   if ablation_target == "All":
       for ab in ["Ab1", "Ab2", "Ab3"]:
           # 运行三次
   ```

2. **实现权重系统:**
   ```python
   # 在 evaluate_mcri.py 中添加权重支持
   weighted_score = raw_score * weight
   ```

3. **去除 JSON 注释:**
   - 删除所有 `//` 注释
   - 或使用 `json5` 库解析

**缺点:**
- ❌ 需要大量代码修改
- ❌ 增加系统复杂度
- ❌ 可能引入新 bug

---

## 📋 推荐操作

### 立即修复（必须）

1. **删除所有 JSON 注释**
   ```bash
   # 手动删除所有 // 注释行
   ```

2. **修改 ablation_target**
   ```json
   // 将所有 "ablation_target": "All" 
   // 改为 "Ab1", "Ab2", 或 "Ab3"
   ```

3. **删除无效字段**
   ```json
   // 删除 "healer_type": "All"
   // 删除 "model": "qwen3-14b-nothink" (由 benchmark 决定)
   // 删除 "weight" (暂时不支持)
   ```

### 测试验证

```bash
python -c "import json; json.load(open('agent_skills/jh_數學2上_FourOperationsOfRadicals/evals.json'))"
```

如果没有报错，说明 JSON 格式正确。

---

## 🎯 结论

**当前 evals.json 文件：❌ 不可行**

**原因:**
1. JSON 注释会导致解析失败
2. `"ablation_target": "All"` 不被支持
3. 权重系统未实现

**建议:**
- 使用方案 A（恢复原有的 Ab1/Ab2/Ab3 设计）
- 或修复注释和 ablation_target 字段
- 保留 generation_kwargs（这个有用）

---

**需要我帮你生成修复后的 evals.json 吗？**
