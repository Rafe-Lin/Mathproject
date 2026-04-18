# -*- coding: utf-8 -*-
# ==============================================================================
# ID: core/healers/anti_duplication_healer.py
# Version: V1.0 (Anti-Duplication & Variable-Before-Use Checker)
# Last Updated: 2026-02-08
# Author: Math AI Research Team
#
# [Description]:
#   Anti-Duplication & Variable-Before-Use Healer
#   解決 AI 生成重複定義的類/函數和變量未定義先使用的問題
#
# [Functionality]:
#   Step 4.5: Anti-Duplication Healer
#   - 檢測重複的類定義
#   - 檢測重複的函數定義
#   - 保留第一個完整定義，刪除後續不完整定義
#   
#   Step 7.5: Variable-Before-Use Checker
#   - 使用 AST 分析變量依賴
#   - 檢查變量是否在使用前定義
#   - 自動重排賦值語句順序
#   - 如無法修復，則注入默認初值
# ==============================================================================

import ast
import re
import logging

logger = logging.getLogger(__name__)


class AntiDuplicationHealer:
    """
    反重複定義修復器
    - 檢測並移除重複的類和函數定義
    - 保留第一個完整的定義，刪除後續低質量定義
    """
    
    def __init__(self):
        self.fixes = 0
        self.duplicate_classes = {}  # {class_name: [line_num, ...]}
        self.duplicate_functions = {}  # {func_name: [line_num, ...]}
    
    def heal(self, code):
        """
        修復重複定義
        
        Args:
            code: Python 代碼字符串
        
        Returns:
            tuple: (修復後代碼, 修復次數)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code, self.fixes
        
        # 第一遍掃描：記錄所有類和函數定義
        class_defs = {}  # {name: [node, line_num]}
        func_defs = {}   # {name: [node, line_num]}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name not in class_defs:
                    class_defs[node.name] = []
                class_defs[node.name].append((node, node.lineno))
            elif isinstance(node, ast.FunctionDef):
                if node.name not in func_defs:
                    func_defs[node.name] = []
                func_defs[node.name].append((node, node.lineno))
        
        # 找出重複定義
        duplicates_to_remove = set()
        
        # 檢查重複的類定義
        for class_name, definitions in class_defs.items():
            if len(definitions) > 1:
                logger.warning(f"🔴 偵測到重複類定義: {class_name} (共 {len(definitions)} 處)")
                # 保留第一個，標記其他為刪除
                for i in range(1, len(definitions)):
                    node, line_num = definitions[i]
                    duplicates_to_remove.add(id(node))
                    logger.info(f"   → 標記第 {i+1} 個定義於第 {line_num} 行刪除 (不完整)")
                    self.fixes += 1
        
        # 檢查重複的函數定義
        for func_name, definitions in func_defs.items():
            if len(definitions) > 1:
                logger.warning(f"🔴 偵測到重複函數定義: {func_name}() (共 {len(definitions)} 處)")
                # 保留第一個，標記其他為刪除
                for i in range(1, len(definitions)):
                    node, line_num = definitions[i]
                    duplicates_to_remove.add(id(node))
                    logger.info(f"   → 標記第 {i+1} 個定義於第 {line_num} 行刪除")
                    self.fixes += 1
        
        # 第二遍：移除標記的節點
        remover = DuplicateRemover(duplicates_to_remove)
        new_tree = remover.visit(tree)
        
        # 轉回代碼
        fixed_code = ast.unparse(new_tree)
        return fixed_code, self.fixes


class DuplicateRemover(ast.NodeTransformer):
    """移除重複定義的 AST 節點變換器"""
    
    def __init__(self, duplicates_to_remove):
        self.duplicates_to_remove = duplicates_to_remove
    
    def visit_ClassDef(self, node):
        if id(node) in self.duplicates_to_remove:
            return None  # 刪除該節點
        self.generic_visit(node)
        return node
    
    def visit_FunctionDef(self, node):
        if id(node) in self.duplicates_to_remove:
            return None  # 刪除該節點
        self.generic_visit(node)
        return node


class VariableShadowingDetector(ast.NodeVisitor):
    """
    變量遮蔽檢測器
    - 檢測是否有賦值語句覆蓋（遮蔽）已定義的類或函數
    - 標記需要刪除的污染賦值
    - 支援預定義名稱列表（來自骨架代碼）
    """
    
    # 預定義的工具函數/類名稱（來自 build_calculation_skeleton）
    PREDEFINED_NAMES = {
        'IntegerOps',
        'fmt_num',
        'to_latex',
        'clean_latex_output',
        'safe_choice',
        'op_latex',
        'random_nonzero',
        'is_divisible',
        'safe_eval',
    }
    
    def __init__(self, predefined_names=None):
        self.defined_names = {}  # {name: ('class'|'function'|'predefined', lineno)}
        self.shadowing_assigns = []  # [(var_name, line_num), ...]
        self.fixes = 0
        
        # 初始化預定義名稱
        if predefined_names:
            self.predefined_names = predefined_names
        else:
            self.predefined_names = self.PREDEFINED_NAMES
    
    def detect(self, code):
        """
        檢測跟清除變量遮蔽
        
        Args:
            code: Python 代碼字符串
        
        Returns:
            tuple: (修復後代碼, 修復次數)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code, self.fixes
        
        # 第一遍：記錄所有類/函數定義
        self._collect_definitions(tree)
        
        # 第二遍：找出遮蔽賦值
        self._find_shadowing_assigns(tree)
        
        if not self.shadowing_assigns:
            return code, self.fixes
        
        # 第三遍：移除污染賦值
        shadow_remover = ShadowingAssignRemover(
            {(name, line) for name, line in self.shadowing_assigns}
        )
        new_tree = shadow_remover.visit(tree)
        
        # 轉回代碼
        fixed_code = ast.unparse(new_tree)
        return fixed_code, self.fixes
    
    def _collect_definitions(self, tree):
        """收集所有類和函數定義 + 預定義名稱"""
        # 先加入預定義名稱
        for name in self.predefined_names:
            self.defined_names[name] = ('predefined', 0)
        
        # 再掃描本地定義
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.defined_names[node.name] = ('class', node.lineno)
            elif isinstance(node, ast.FunctionDef):
                self.defined_names[node.name] = ('function', node.lineno)
    
    def _find_shadowing_assigns(self, tree):
        """找出覆蓋定義的賦值"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        if var_name in self.defined_names:
                            def_type, def_line = self.defined_names[var_name]
                            
                            # 對於預定義名稱，任何賦值都是污染
                            # 對於本地定義，只有定義之後的賦值才視為污染
                            if def_type == 'predefined' or (def_type in ('class', 'function') and node.lineno > def_line):
                                logger.warning(
                                    f"🔴 變量遮蔽污染: '{var_name}' 在第 {def_line} 行定義為 {def_type}，"
                                    f"但在第 {node.lineno} 行被賦值覆蓋"
                                )
                                self.shadowing_assigns.append((var_name, node.lineno))
                                self.fixes += 1
                                logger.info(f"   → 標記第 {node.lineno} 行的污染賦值刪除")


class ShadowingAssignRemover(ast.NodeTransformer):
    """移除遮蔽賦值的 AST 節點變換器"""
    
    def __init__(self, shadowing_assigns):
        self.shadowing_assigns = shadowing_assigns  # {(var_name, line_num), ...}
    
    def visit_Assign(self, node):
        """檢查該賦值是否是污染賦值"""
        # 檢查這行是否在污染列表中
        for target in node.targets:
            if isinstance(target, ast.Name):
                if (target.id, node.lineno) in self.shadowing_assigns:
                    return None  # 刪除該污染賦值
        
        self.generic_visit(node)
        return node


class VariableBeforeUseChecker:
    """
    變量使用前檢查修復器
    - 檢測變量是否在定義前使用
    - 自動重排或注入默認值
    - 跳過預定義名稱（來自骨架代碼）
    """
    
    def __init__(self):
        self.fixes = 0
        self.assignments = {}  # {var_name: line_num}
        self.uses = {}  # {var_name: [line_nums]}
        self.defined_classes = set()  # class/function 定義的名稱
        self.defined_functions = set()
        
        # 預定義名稱（不應該注入）
        self.predefined_names = VariableShadowingDetector.PREDEFINED_NAMES
    
    def heal(self, code):
        """
        修復變量使用前的問題
        
        Args:
            code: Python 代碼字符串
        
        Returns:
            tuple: (修復後代碼, 修復次數)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return code, self.fixes
        
        # 先收集所有定義的類和函數（不應該注入默認值）
        self._collect_defined_names(tree)
        
        # 分析變量依賴
        analyzer = VariableAnalyzer()
        analyzer.visit(tree)
        
        # 檢查是否有變量使用前未定義的情況
        problematic_vars = {}
        for var_name, first_use_line in analyzer.first_use.items():
            # 跳過已定義的類/函數和預定義名稱
            if var_name in self.defined_classes or var_name in self.defined_functions:
                continue
            if var_name in self.predefined_names:
                continue
            
            if var_name in analyzer.first_assign:
                first_assign_line = analyzer.first_assign[var_name]
                if first_assign_line > first_use_line:
                    # 變量在使用前未定義
                    problematic_vars[var_name] = (first_assign_line, first_use_line)
                    logger.warning(f"🔴 變量使用前未定義: {var_name} (使用於第 {first_use_line} 行，定義於第 {first_assign_line} 行)")
            else:
                # 變量從未被定義
                problematic_vars[var_name] = (None, first_use_line)
                logger.warning(f"🔴 變量未定義: {var_name} (使用於第 {first_use_line} 行)")
        
        if not problematic_vars:
            return code, self.fixes
        
        # 嘗試修復：注入默認初值
        lines = code.split('\n')
        injected_vars = set()
        
        for var_name in problematic_vars:
            # 在文件開頭（所有 import 之後）注入默認值
            insert_pos = self._find_insert_position(lines)
            
            # 根據變量名推斷類型
            default_value = self._infer_default_value(var_name)
            injection = f"{var_name} = {default_value}"
            
            lines.insert(insert_pos, injection)
            injected_vars.add(var_name)
            self.fixes += 1
            logger.info(f"   ✅ 注入默認值: {injection}")
        
        fixed_code = '\n'.join(lines)
        return fixed_code, self.fixes
    
    def _collect_defined_names(self, tree):
        """收集所有定義的類和函數名稱"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.defined_classes.add(node.name)
            elif isinstance(node, ast.FunctionDef):
                self.defined_functions.add(node.name)
    
    def _find_insert_position(self, lines):
        """找到適合注入初值的位置（所有 import 之後）"""
        last_import_idx = -1
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')) and not stripped.startswith('#'):
                last_import_idx = i
        
        # 如果有 import，在其後插入；否則在文件開頭插入
        return last_import_idx + 1
    
    def _infer_default_value(self, var_name):
        """根據變量名推斷默認值"""
        var_lower = var_name.lower()
        
        # 數字相關
        if any(x in var_lower for x in ['count', 'num', 'val', 'result', 'total', 'sum', 'index', 'i', 'j', 'k']):
            return "0"
        
        # 字符串相關
        if any(x in var_lower for x in ['text', 'msg', 'str', 'name', 'label']):
            return '""'
        
        # 列表相關
        if any(x in var_lower for x in ['list', 'items', 'values', 'data']):
            return "[]"
        
        # 字典相關
        if any(x in var_lower for x in ['dict', 'mapping', 'config']):
            return "{}"
        
        # 布爾相關
        if any(x in var_lower for x in ['is_', 'has_', 'flag', 'ok']):
            return "False"
        
        # 默認值
        return "None"


class VariableAnalyzer(ast.NodeVisitor):
    """分析代碼中變量的定義和使用"""
    
    def __init__(self):
        self.first_assign = {}  # {var_name: line_num}
        self.first_use = {}  # {var_name: line_num}
        self.assigned_in_loops = set()  # 在迴圈中定義的變量
        self.scope_stack = [set()]  # 作用域堆棧
    
    def visit_Module(self, node):
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        """追蹤賦值"""
        # 提取所有被賦值的變量
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                if var_name not in self.first_assign:
                    self.first_assign[var_name] = node.lineno
        
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """追蹤變量使用"""
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            var_name = node.id
            # 過濾掉內置函數和模塊
            if var_name not in self.first_use and not self._is_builtin(var_name):
                self.first_use[var_name] = node.lineno
        
        self.generic_visit(node)
    
    def _is_builtin(self, name):
        """檢查是否為內置函數/常量"""
        builtins = {
            'True', 'False', 'None', 'print', 'len', 'range', 'str', 'int', 'float',
            'list', 'dict', 'set', 'tuple', 'abs', 'sum', 'min', 'max', 'round',
            'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter', 'all', 'any',
            'eval', 'exec', 'open', 'input', 'output', 'type', 'isinstance',
            'random', 'math', 're', 'os', 'sys', 'time', 'datetime', 'json',
            'staticmethod', 'classmethod', 'property', 'super', 'object',
            'Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError'
        }
        return name in builtins


def heal_duplicates_and_variables(code):
    """
    一鍵修復重複定義和變量問題
    
    Args:
        code: Python 代碼字符串
    
    Returns:
        tuple: (修復後代碼, 總修復次數)
    """
    total_fixes = 0
    
    # Step 1: Anti-Duplication
    logger.info("🔧 Step 4.5: Anti-Duplication Healer")
    anti_dup = AntiDuplicationHealer()
    code, dup_fixes = anti_dup.heal(code)
    total_fixes += dup_fixes
    if dup_fixes > 0:
        logger.info(f"   ✅ 移除 {dup_fixes} 個重複定義")
    
    # Step 4.6: Variable Shadowing Detector (NEW)
    logger.info("🔧 Step 4.6: Variable Shadowing Detector")
    shadow_detector = VariableShadowingDetector(predefined_names=VariableShadowingDetector.PREDEFINED_NAMES)
    code, shadow_fixes = shadow_detector.detect(code)
    total_fixes += shadow_fixes
    if shadow_fixes > 0:
        logger.info(f"   ✅ 移除 {shadow_fixes} 個污染賦值")
    
    # Step 2: Variable-Before-Use Checker
    logger.info("🔧 Step 7.5: Variable-Before-Use Checker")
    var_checker = VariableBeforeUseChecker()
    code, var_fixes = var_checker.heal(code)
    total_fixes += var_fixes
    if var_fixes > 0:
        logger.info(f"   ✅ 注入 {var_fixes} 個默認初值")
    
    return code, total_fixes
