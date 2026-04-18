# -*- coding: utf-8 -*-
"""
統一清理 Healer - 一次性解決所有代碼污染問題
- 重複定義 (重複 class/function)
- 變量遮蔽污染 (覆蓋預定義名稱)
- 變量使用順序 (使用前未定義)
"""

import ast
import re
import logging

logger = logging.getLogger(__name__)


class UnifiedCleanupHealer:
    """統一清理所有代碼問題的 Healer
    
    一次性AST遍歷完成所有修復，避免反復刪除和添加的問題
    """
    
    # 預定義的工具函數/類名稱（來自 build_calculation_skeleton）
    PREDEFINED_NAMES = {
        'IntegerOps',
        'FractionOps',  # Add other ops if needed
        'fmt_num',
        'to_latex',
        'clean_latex_output',
        'safe_choice',
        'op_latex',
        'random_nonzero',
        'is_divisible',
        'safe_eval',
    }
    
    def __init__(self):
        self.total_fixes = 0
        self.duplicate_count = 0
        self.shadowing_count = 0
        self.variable_order_count = 0
    
    def _remove_duplicate_classes_via_string(self, code):
        """
        【NEW】字符串级别的重复类删除
        使用正则表达式识别和删除重复的类定义
        """
        lines = code.split('\n')
        # ★★★ CRITICAL FIX: 初始化時包含預定義名稱，確保 AI 生成的同名類被視為重複 ★★★
        seen_classes = set(self.PREDEFINED_NAMES)
        lines_to_remove = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 匹配 class 定義
            class_match = re.match(r'^class\s+(\w+)\s*[\(:]', line)
            if class_match:
                class_name = class_match.group(1)
                
                if class_name in seen_classes:
                    # 這是重複定義
                    logger.warning(f"🔴 檢測到重複 class: {class_name} 在第 {i+1} 行")
                    
                    start_line = i
                    base_indent = len(line) - len(line.lstrip())
                    
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j]
                        if not next_line.strip():
                            j += 1
                            continue
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent <= base_indent:
                            break
                        j += 1
                    
                    # 向上刪除空行
                    while start_line > 0:
                        prev_line = lines[start_line - 1]
                        if not prev_line.strip():
                            start_line -= 1
                        else:
                            break
                    
                    for k in range(start_line, j):
                        lines_to_remove.append(k)
                    
                    logger.info(f"   → 將刪除第 {start_line+1} 到 {j} 行")
                    self.duplicate_count += 1
                    
                    i = j
                    continue
                else:
                    seen_classes.add(class_name)
            
            i += 1
        
        if not lines_to_remove:
            return code
        
        lines_to_remove_set = set(lines_to_remove)
        new_lines = [lines[i] for i in range(len(lines)) if i not in lines_to_remove_set]
        return '\n'.join(new_lines)
    
    def heal(self, code):
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.warning(f"AST 解析失敗: {e}")
            return code, 0
        
        # 第一步：處理字符串級別的重複類定義
        code_after_strdup = self._remove_duplicate_classes_via_string(code)
        
        if code_after_strdup != code:
            try:
                tree = ast.parse(code_after_strdup)
                code = code_after_strdup
            except SyntaxError:
                logger.warning("字符串去重後 AST 解析失敗，回到原始代碼")
                code_after_strdup = code
        
        # 第一遍：掃描
        scanner = ProblemScanner(self.PREDEFINED_NAMES)
        scanner.visit(tree)
        
        string_duplicate_count = self.duplicate_count
        self.duplicate_count += len(scanner.duplicate_nodes)
        self.shadowing_count = len(scanner.shadowing_nodes)
        self.variable_order_count = scanner.variable_reorder_count
        self.total_fixes = self.duplicate_count + self.shadowing_count + self.variable_order_count
        
        if self.total_fixes == 0:
            return code, self.duplicate_count
        
        # 第二遍：清理
        cleaner = CodeCleaner(scanner.duplicate_nodes, scanner.shadowing_nodes,
                              scanner.variable_reorders)
        new_tree = cleaner.visit(tree)
        
        fixed_code = ast.unparse(new_tree)
        
        if self.duplicate_count > 0:
            logger.info(f"✅ 移除 {self.duplicate_count} 個重複定義")
        if self.shadowing_count > 0:
            logger.info(f"✅ 移除 {self.shadowing_count} 個污染賦值")
        if self.variable_order_count > 0:
            logger.info(f"✅ 修復 {self.variable_order_count} 個變量順序問題")
        
        return fixed_code, self.total_fixes


class ProblemScanner(ast.NodeVisitor):
    def __init__(self, predefined_names=None):
        self.predefined_names = predefined_names or UnifiedCleanupHealer.PREDEFINED_NAMES
        self.defined_names = {}
        self.duplicate_nodes = set()
        self.shadowing_nodes = set()
        self.variable_reorders = {}
        self.variable_reorder_count = 0
        self.first_use = {}
        self.first_assign = {}
    
    def visit_ClassDef(self, node):
        name = node.name
        # ★★★ CRITICAL FIX: 檢查是否與預定義名稱衝突 ★★★
        if name in self.defined_names or name in self.predefined_names:
            logger.warning(f"🔴 重複 class 定義 (或覆蓋系統保留字): {name}")
            self.duplicate_nodes.add(id(node))
        else:
            self.defined_names[name] = ('class', node.lineno, id(node))
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        name = node.name
        # ★★★ CRITICAL FIX: 檢查是否與預定義名稱衝突 ★★★
        if name in self.defined_names or name in self.predefined_names:
            logger.warning(f"🔴 重複 function 定義 (或覆蓋系統保留字): {name}()")
            self.duplicate_nodes.add(id(node))
        else:
            self.defined_names[name] = ('function', node.lineno, id(node))
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                if var_name in self.predefined_names:
                    logger.warning(f"🔴 污染賦值: {var_name} = ... (覆蓋預定義)")
                    self.shadowing_nodes.add(id(node))
                elif var_name in self.defined_names:
                    def_type, def_line, _ = self.defined_names[var_name]
                    if def_type in ('class', 'function') and node.lineno > def_line:
                        logger.warning(f"🔴 污染賦值: {var_name} = ... (覆蓋 {def_type})")
                        self.shadowing_nodes.add(id(node))
                
                if var_name not in self.first_assign:
                    self.first_assign[var_name] = (node.lineno, id(node))
        self.generic_visit(node)
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            var_name = node.id
            if var_name not in self.first_use and not self._is_builtin(var_name):
                self.first_use[var_name] = node.lineno
        self.generic_visit(node)
    
    def _is_builtin(self, name):
        builtins = {
            'True', 'False', 'None', 'print', 'len', 'range', 'str', 'int', 
            'float', 'list', 'dict', 'set', 'tuple', 'abs', 'sum', 'min', 'max',
            'random', 'math', 're', 'os', 'sys', 'staticmethod', 'classmethod',
            'property', 'super', 'object', 'Exception', 'ValueError',
        }
        return name in builtins or name in self.predefined_names


class CodeCleaner(ast.NodeTransformer):
    def __init__(self, duplicate_nodes, shadowing_nodes, variable_reorders):
        self.duplicate_nodes = duplicate_nodes
        self.shadowing_nodes = shadowing_nodes
        self.variable_reorders = variable_reorders
    
    def visit_ClassDef(self, node):
        if id(node) in self.duplicate_nodes:
            return None
        self.generic_visit(node)
        return node
    
    def visit_FunctionDef(self, node):
        if id(node) in self.duplicate_nodes:
            return None
        self.generic_visit(node)
        return node
    
    def visit_Assign(self, node):
        if id(node) in self.shadowing_nodes:
            return None
        self.generic_visit(node)
        return node


def heal_unified(code):
    """統一清理入口"""
    logger.info("🔧 Step 4.5: Unified Cleanup (重複 + 污染 + 變量順序)")
    healer = UnifiedCleanupHealer()
    fixed_code, total_fixes = healer.heal(code)
    
    if total_fixes > 0:
        logger.info(f"   ✅ 總共修復 {total_fixes} 個問題 "
                   f"(重複={healer.duplicate_count}, 污染={healer.shadowing_count}, "
                   f"變量={healer.variable_order_count})")
    else:
        logger.info("   無需修復")
    
    return fixed_code, total_fixes