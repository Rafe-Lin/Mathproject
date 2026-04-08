# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/kg_data_loader.py
功能說明 (Description): 知識圖譜 JSON 資料加載器，從 kg_outputs 目錄讀取並快取知識圖譜資料
執行語法 (Usage): from core.kg_data_loader import KGDataLoader
版本資訊 (Version): V1.0
更新日期 (Date): 2026-04-07
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class KGDataLoader:
    """知識圖譜 JSON 資料加載器"""
    
    def __init__(self, kg_outputs_path: str):
        """
        初始化 KG 資料加載器
        
        Args:
            kg_outputs_path: kg_outputs 目錄的路徑
        """
        self.kg_outputs_path = Path(kg_outputs_path)
        self.cache = {}  # 快取已加載的資料
        self._load_all_data()
    
    def _load_all_data(self):
        """掃描並加載所有 JSON 檔案"""
        if not self.kg_outputs_path.exists():
            logger.warning(f"KG 輸出目錄不存在: {self.kg_outputs_path}")
            return
        
        # 遍歷所有年級目錄
        for grade_dir in self.kg_outputs_path.iterdir():
            if not grade_dir.is_dir():
                continue
            
            grade_name = grade_dir.name
            self.cache[grade_name] = {}
            
            # 遍歷該年級下的所有 JSON 檔案
            for json_file in grade_dir.glob('*.json'):
                if json_file.name == 'all_units.json':
                    continue
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        unit_id = json_file.stem
                        self.cache[grade_name][unit_id] = data
                        logger.debug(f"已加載: {grade_name}/{unit_id}")
                except Exception as e:
                    logger.error(f"載入 JSON 檔案失敗 {json_file}: {str(e)}")
    
    def get_all_grades(self) -> List[str]:
        """
        獲取所有年級
        
        Returns:
            年級名稱列表，如 ['國一上', '國一下', ...]
        """
        return sorted(self.cache.keys())
    
    def get_units_for_grade(self, grade: str) -> Dict[str, Any]:
        """
        獲取特定年級的所有單元
        
        Args:
            grade: 年級名稱
        
        Returns:
            {單元ID: 單元資料} 的字典
        """
        return self.cache.get(grade, {})
    
    def get_unit_data(self, grade: str, unit_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取特定單元的資料
        
        Args:
            grade: 年級名稱
            unit_id: 單元 ID
        
        Returns:
            單元資料字典，或 None 如果找不到
        """
        return self.cache.get(grade, {}).get(unit_id)
    
    def get_all_units_info(self, grade: str) -> Optional[Dict[str, Any]]:
        """
        獲取特定年級的 all_units.json 資料
        
        Args:
            grade: 年級名稱
        
        Returns:
            all_units.json 的內容
        """
        try:
            all_units_path = self.kg_outputs_path / grade / 'all_units.json'
            if all_units_path.exists():
                with open(all_units_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"載入 all_units.json 失敗 ({grade}): {str(e)}")
        
        return None
    
    def get_graph_data(self, grade: str, unit_id: Optional[str] = None) -> Dict[str, Any]:
        """
        獲取知識圖譜的節點和連接資料
        
        Args:
            grade: 年級名稱
            unit_id: 單元 ID（可選）。如果提供，只返回該單元的資料；否則返回該年級所有單元的合併資料
        
        Returns:
            包含 'nodes' 和 'links' 的字典
        """
        nodes = []
        links = set()  # 使用 set 避免重複
        visited_nodes = set()
        
        if unit_id:
            # 獲取特定單元資料
            unit_data = self.get_unit_data(grade, unit_id)
            if unit_data:
                nodes_data = unit_data.get('nodes', [])
                self._process_nodes(nodes_data, nodes, links, visited_nodes)
        else:
            # 獲取整個年級的資料
            all_units_info = self.get_all_units_info(grade)
            if all_units_info:
                for unit in all_units_info.get('units', []):
                    nodes_data = unit.get('nodes', [])
                    self._process_nodes(nodes_data, nodes, links, visited_nodes)
        
        # 將 links 集合轉換為列表
        links_list = [{'source': s, 'target': t} for s, t in links]
        
        return {
            'nodes': nodes,
            'links': links_list
        }
    
    def _process_nodes(self, nodes_data: List[Dict], nodes: List, links: set, visited: set):
        """
        處理節點資料，提取節點和連接關係
        
        Args:
            nodes_data: 原始節點資料
            nodes: 累積的節點列表
            links: 累積的連接集合
            visited: 已訪問的節點集合
        """
        for node_data in nodes_data:
            node_id = node_data.get('id')
            
            # 避免重複添加相同節點
            if node_id not in visited:
                visited.add(node_id)
                
                # 構建節點信息
                node = {
                    'id': node_id,
                    'level': node_data.get('level'),
                    'name': node_data.get('name'),
                    'parent_id': node_data.get('parent_id')
                }
                
                # 添加可選欄位
                if 'description' in node_data:
                    node['description'] = node_data['description']
                if 'difficulty' in node_data:
                    node['difficulty'] = node_data['difficulty']
                
                nodes.append(node)
                
                # 添加父子連接
                parent_id = node_data.get('parent_id')
                if parent_id:
                    links.add((parent_id, node_id))
    
    def search_nodes(self, grade: str, keyword: str, unit_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        搜尋節點（按名稱或描述）
        
        Args:
            grade: 年級名稱
            keyword: 搜尋關鍵字
            unit_id: 單元 ID（可選）
        
        Returns:
            匹配的節點列表
        """
        results = []
        keyword_lower = keyword.lower()
        
        if unit_id:
            unit_data = self.get_unit_data(grade, unit_id)
            if unit_data:
                nodes_data = unit_data.get('nodes', [])
                self._search_nodes_in_list(nodes_data, keyword_lower, results)
        else:
            all_units_info = self.get_all_units_info(grade)
            if all_units_info:
                for unit in all_units_info.get('units', []):
                    nodes_data = unit.get('nodes', [])
                    self._search_nodes_in_list(nodes_data, keyword_lower, results)
        
        return results
    
    def _search_nodes_in_list(self, nodes_data: List[Dict], keyword: str, results: List):
        """在節點列表中搜尋關鍵字"""
        for node in nodes_data:
            name = node.get('name', '').lower()
            description = node.get('description', '').lower()
            
            if keyword in name or keyword in description:
                results.append(node)
    
    def get_difficulty_distribution(self, grade: str, unit_id: Optional[str] = None) -> Dict[int, int]:
        """
        獲取難度分佈
        
        Args:
            grade: 年級名稱
            unit_id: 單元 ID（可選）
        
        Returns:
            {難度: 數量} 的字典
        """
        distribution = {}
        
        if unit_id:
            unit_data = self.get_unit_data(grade, unit_id)
            if unit_data:
                nodes_data = unit_data.get('nodes', [])
                self._count_difficulty(nodes_data, distribution)
        else:
            all_units_info = self.get_all_units_info(grade)
            if all_units_info:
                for unit in all_units_info.get('units', []):
                    nodes_data = unit.get('nodes', [])
                    self._count_difficulty(nodes_data, distribution)
        
        return distribution
    
    def _count_difficulty(self, nodes_data: List[Dict], distribution: Dict):
        """計算難度分佈"""
        for node in nodes_data:
            difficulty = node.get('difficulty')
            if difficulty is not None:
                distribution[difficulty] = distribution.get(difficulty, 0) + 1


# 全局 KG 資料加載器實例
_kg_loader: Optional[KGDataLoader] = None


def get_kg_loader() -> KGDataLoader:
    """
    獲取全局 KG 資料加載器實例（懶初始化）
    
    Returns:
        KGDataLoader 實例
    """
    global _kg_loader
    if _kg_loader is None:
        # 獲取專案根目錄
        project_root = Path(__file__).parent.parent
        kg_outputs_path = project_root / 'kg_outputs'
        _kg_loader = KGDataLoader(str(kg_outputs_path))
    
    return _kg_loader
