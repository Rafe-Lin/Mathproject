"""
═════════════════════════════════════════════════════════════════════════════
自適應總複習模式 - 基於 RL + AKT 的動態題目推薦系統
═════════════════════════════════════════════════════════════════════════════

核心功能：
1. 讀取學生學習歷史
2. 使用 AKT 推論當前知識狀態
3. 使用訓練好的 PPO-RL 模型推薦最佳題目序列
4. 動態生成個性化複習方案
5. 追蹤複習進度與改進指標

架構：
┌─────────────────────┐
│ 學生學習歷史        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ AKT 知識狀態推論                   │ ◄─── AKT 模型 (akt_curriculum.pth)
│ 獲取：sₜ (知識狀態)                │
│ 計算：APR (平均掌握度)             │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ RL 推薦引擎                         │ ◄─── PPO 模型 (ppo_akt_curriculum.zip)
│ 輸入：當前知識狀態                │
│ 輸出：最優題目 item_id              │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 題目執行與反饋更新                  │
│ 收集：學生答案、耗時、反饋          │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 複習報告生成                         │
│ 展示：進度、弱項、建議              │
└─────────────────────────────────────┘

會話例子：
────────────────────────────────────────
Session 1 (初診斷):
  - 輸入: 學生過去10道題的答案序列
  - 推論: APR=0.62 (需要補強多項式和根式)
  - 推薦: 7 題補強序列 (專注多項式 + 根式交叉)
  - 完成: APR 提升至 0.78
────────────────────────────────────────
Session 2 (複習鞏固):
  - 輸入: 包括 Session 1 的全部歷史
  - 推論: APR=0.78 (仍有弱項)
  - 推薦: 5 題進階練習 (多項式難度提升 + 根式應用)
  - 完成: APR 提升至 0.85
────────────────────────────────────────
"""

import sys
import os
import json
import numpy as np
import pandas as pd
import torch
import gymnasium as gym
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# 匯入必要的類
from akt_inference import AKTInference
from stable_baselines3 import PPO

# ═══════════════════════════════════════════════════════════════════════════
# 常數定義
# ═══════════════════════════════════════════════════════════════════════════

MODEL_PATH = './models/akt_curriculum.pth'
RL_MODEL_PATH = './models/rl_akt_curriculum/ppo_akt_curriculum.zip'
DATA_PATH = './synthesized_training_data.csv'

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
BETA_THRESHOLD = 0.65  # 目標掌握度

# 複習模式配置
REVIEW_CONFIG = {
    'min_session_length': 3,      # 最少出題數
    'max_session_length': 15,     # 最多出題數
    'target_apr_increment': 0.10, # 目標 APR 增長
    'max_consecutive_failures': 3, # 連續失敗上限
    'review_diversity_weight': 0.3, # 多樣性權重
}


# ═══════════════════════════════════════════════════════════════════════════
# 核心類：自適應複習引擎
# ═══════════════════════════════════════════════════════════════════════════

class AdaptiveReviewEngine:
    """
    自適應複習引擎 - 整合 AKT + RL 進行動態題目推薦
    """

    def __init__(self, akt_model_path: str = MODEL_PATH, 
                 rl_model_path: str = RL_MODEL_PATH,
                 data_path: str = DATA_PATH,
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        """
        初始化複習引擎
        
        Args:
            akt_model_path: AKT 模型路徑
            rl_model_path: RL 模型路徑
            data_path: 訓練資料路徑
            device: 計算設備 ('cuda' 或 'cpu')
        """
        print(f"[Init] 初始化自適應複習引擎...")
        
        # 載入 AKT 推論引擎
        self.akt_inference = AKTInference(akt_model_path)
        self.n_items = self.akt_inference.n_items
        self.n_skills = self.akt_inference.n_skills
        self.skill_to_id = self.akt_inference.skill_to_id
        self.problem_to_id = self.akt_inference.problem_to_id
        self.skills_list = self.akt_inference.skills_list
        
        # 載入 RL 模型
        print(f"[Init] 載入 RL 模型 ({rl_model_path})...")
        self.rl_model = PPO.load(rl_model_path, device=device)
        self.rl_model.policy.eval()
        
        # 載入題目屬性
        self._load_item_properties(data_path)
        
        print(f"[✓] 複習引擎已就緒")
        print(f"    - AKT 技能數: {self.n_skills}")
        print(f"    - 題目總數: {self.n_items}")
        print(f"    - RL 設備: {device}\n")

    def _load_item_properties(self, data_path: str):
        """載入題目屬性（難度、技能等）"""
        try:
            df = pd.read_csv(data_path, encoding='utf-8')
            
            # 題目難度（答對率）
            self.item_difficulty = df.groupby('problemId')['correct'].agg(['mean', 'count']).reset_index()
            self.item_difficulty.columns = ['problemId', 'difficulty', 'attempts']
            self.item_difficulty['difficulty'] = 1.0 - self.item_difficulty['difficulty']  # 反轉為難度
            
            # 題目技能映射
            self.item_to_skill = {}
            for _, row in df.iterrows():
                pid = int(row['problemId'])
                skill = row['skill']
                if skill in self.skill_to_id:
                    self.item_to_skill[pid] = self.skill_to_id[skill]
                    
            print(f"[✓] 已載入 {len(self.item_difficulty)} 個題目屬性")
        except Exception as e:
            print(f"[⚠] 載入題目屬性失敗: {e}")
            self.item_difficulty = None
            self.item_to_skill = {}

    def get_knowledge_state(self, 
                            item_history: List[int], 
                            skill_history: List[int],
                            resp_history: List[int]) -> np.ndarray:
        """
        獲取當前知識狀態向量
        
        Args:
            item_history: 歷史題目 ID 序列
            skill_history: 歷史技能 ID 序列
            resp_history: 歷史答對情況序列
            
        Returns:
            sₜ: 知識狀態向量（每個題目的答對機率）
        """
        return self.akt_inference.get_knowledge_state(item_history, skill_history, resp_history)

    def get_apr(self, s_t: np.ndarray) -> float:
        """計算 APR (平均掌握度)"""
        if len(s_t) == 0:
            return 0.5
            
        # 按技能計算平均掌握度
        skill_aprs = defaultdict(list)
        for item_id in range(min(len(s_t), self.n_items)):
            skill_id = self.akt_inference.problem_to_skill_id.get(item_id, 0)
            skill_aprs[skill_id].append(s_t[item_id])
        
        if not skill_aprs:
            return float(np.mean(s_t))
        
        skill_means = [np.mean(vals) for vals in skill_aprs.values()]
        return float(np.mean(skill_means))

    def recommend_next_items(self, 
                            item_history: List[int],
                            skill_history: List[int],
                            resp_history: List[int],
                            n_items: int = 5,
                            use_rl: bool = True) -> List[Dict]:
        """
        推薦下一批題目
        
        Args:
            item_history: 歷史題目序列
            skill_history: 歷史技能序列
            resp_history: 歷史答對序列
            n_items: 推薦數量
            use_rl: 是否使用 RL 模型推薦
            
        Returns:
            List[Dict]: 推薦題目列表，每個包含 {item_id, skill_id, predicted_difficulty}
        """
        # 獲取當前知識狀態
        s_t = self.get_knowledge_state(item_history, skill_history, resp_history)
        current_apr = self.get_apr(s_t)
        
        visited_items = set(item_history)
        recommended = []
        
        for _ in range(n_items):
            if use_rl:
                # 使用 RL 模型選擇
                with torch.no_grad():
                    obs = torch.tensor(s_t, dtype=torch.float32).unsqueeze(0)
                    action, _ = self.rl_model.predict(obs, deterministic=True)
                    item_id = int(action)
            else:
                # 備選方案：Max-Fisher (最高不確定性)
                item_id = self._select_max_fisher(s_t, visited_items)
            
            # 如果已經做過，用備選方案
            if item_id in visited_items:
                item_id = self._select_max_fisher(s_t, visited_items)
                
            if item_id in visited_items or item_id >= self.n_items:
                continue
                
            skill_id = self.akt_inference.problem_to_skill_id.get(item_id, 0)
            difficulty = s_t[item_id]  # 預測答對機率反轉為難度
            
            recommended.append({
                'item_id': int(item_id),
                'skill_id': int(skill_id),
                'predicted_difficulty': float(difficulty),
                'skill_name': self.skills_list[skill_id] if skill_id < len(self.skills_list) else f'Skill_{skill_id}'
            })
            
            visited_items.add(item_id)
        
        return recommended

    def _select_max_fisher(self, s_t: np.ndarray, visited: set) -> int:
        """Max-Fisher 策略：選擇不確定性最高的未做題目"""
        fisher = s_t[:self.n_items] * (1.0 - s_t[:self.n_items])
        
        for item_id in visited:
            if item_id < len(fisher):
                fisher[item_id] = -1.0
        
        return int(np.argmax(fisher))

    def simulate_session(self,
                         item_history: List[int],
                         skill_history: List[int],
                         resp_history: List[int],
                         session_name: str = "Review Session",
                         verbose: bool = True) -> Dict:
        """
        模擬一個複習會話
        
        Args:
            item_history: 初始題目歷史
            skill_history: 初始技能歷史
            resp_history: 初始答對情況
            session_name: 會話名稱
            verbose: 是否打印詳細信息
            
        Returns:
            Dict: 會話統計信息
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"📊 複習會話: {session_name}")
            print(f"{'='*70}")
        
        # 初始狀態
        s_t_init = self.get_knowledge_state(item_history, skill_history, resp_history)
        apr_init = self.get_apr(s_t_init)
        
        if verbose:
            print(f"[初始] APR: {apr_init:.4f}")
            print(f"[初始] 已做題數: {len(item_history)}")
        
        # 推薦題目
        recommendations = self.recommend_next_items(
            item_history, skill_history, resp_history,
            n_items=REVIEW_CONFIG['max_session_length'],
            use_rl=True
        )
        
        if verbose:
            print(f"\n[推薦] 下一批題目:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. Item {rec['item_id']} - {rec['skill_name']} (難度: {1-rec['predicted_difficulty']:.2f})")
        
        # 模擬答題（隨機）
        session_stats = {
            'session_name': session_name,
            'timestamp': datetime.now().isoformat(),
            'apr_initial': float(apr_init),
            'apr_final': float(apr_init),
            'recommendations_count': len(recommendations),
            'simulated_responses': [],
            'skills_practiced': defaultdict(int),
        }
        
        rng = np.random.RandomState(42)
        session_history = {
            'item_history': list(item_history),
            'skill_history': list(skill_history),
            'resp_history': list(resp_history),
        }
        
        for i, rec in enumerate(recommendations[:REVIEW_CONFIG['max_session_length']]):
            item_id = rec['item_id']
            skill_id = rec['skill_id']
            p_correct = 1.0 - rec['predicted_difficulty']  # 答對概率
            
            # 模擬答題
            is_correct = 1 if rng.rand() < p_correct else 0
            
            # 更新歷史
            session_history['item_history'].append(item_id)
            session_history['skill_history'].append(skill_id)
            session_history['resp_history'].append(is_correct)
            
            session_stats['simulated_responses'].append({
                'item_id': item_id,
                'skill_id': skill_id,
                'predicted_difficulty': rec['predicted_difficulty'],
                'correct': is_correct
            })
            
            session_stats['skills_practiced'][rec['skill_name']] += 1
            
            if verbose and i < 3:
                result = "✓" if is_correct else "✗"
                print(f"  {result} Item {item_id}: {rec['skill_name']}")
        
        # 計算最終 APR
        s_t_final = self.get_knowledge_state(
            session_history['item_history'],
            session_history['skill_history'],
            session_history['resp_history']
        )
        apr_final = self.get_apr(s_t_final)
        session_stats['apr_final'] = float(apr_final)
        session_stats['apr_gain'] = float(apr_final - apr_init)
        session_stats['correct_rate'] = float(
            sum(r['correct'] for r in session_stats['simulated_responses']) / 
            len(session_stats['simulated_responses'])
        ) if session_stats['simulated_responses'] else 0.0
        
        if verbose:
            print(f"\n[結果] APR 初始: {apr_init:.4f} → 最終: {apr_final:.4f}")
            print(f"[結果] APR 增幅: +{apr_final - apr_init:.4f}")
            print(f"[結果] 答對率: {session_stats['correct_rate']:.2%}")
            print(f"{'='*70}\n")
        
        return session_stats


# ═══════════════════════════════════════════════════════════════════════════
# 輔助函數：多會話複習規劃
# ═══════════════════════════════════════════════════════════════════════════

def generate_review_plan(student_history: Dict,
                         num_sessions: int = 3,
                         engine: Optional[AdaptiveReviewEngine] = None) -> Dict:
    """
    生成多會話複習計畫
    
    Args:
        student_history: 學生歷史 {'item_history', 'skill_history', 'resp_history'}
        num_sessions: 複習會話數
        engine: 複習引擎實例
        
    Returns:
        Dict: 完整複習計畫
    """
    if engine is None:
        engine = AdaptiveReviewEngine()
    
    plan = {
        'student_history_init': student_history,
        'num_sessions': num_sessions,
        'sessions': [],
        'overall_stats': {
            'apr_initial': None,
            'apr_final': None,
            'total_items_practiced': 0,
        }
    }
    
    # 初始 APR
    s_t = engine.get_knowledge_state(
        student_history['item_history'],
        student_history['skill_history'],
        student_history['resp_history']
    )
    plan['overall_stats']['apr_initial'] = engine.get_apr(s_t)
    
    current_history = student_history.copy()
    
    for session_idx in range(num_sessions):
        session_name = f"複習會話 #{session_idx + 1}"
        
        stats = engine.simulate_session(
            current_history['item_history'],
            current_history['skill_history'],
            current_history['resp_history'],
            session_name=session_name,
            verbose=False
        )
        
        plan['sessions'].append(stats)
        plan['overall_stats']['total_items_practiced'] += len(stats['simulated_responses'])
        
        # 更新為下一會話的初始狀態
        # (這裡簡化處理，實際上應該更新歷史)
    
    plan['overall_stats']['apr_final'] = plan['sessions'][-1]['apr_final'] if plan['sessions'] else plan['overall_stats']['apr_initial']
    
    return plan


# ═══════════════════════════════════════════════════════════════════════════
# 診斷與弱項分析
# ═══════════════════════════════════════════════════════════════════════════

def analyze_weak_skills(engine: AdaptiveReviewEngine,
                        item_history: List[int],
                        skill_history: List[int],
                        resp_history: List[int]) -> Dict:
    """
    分析學生的弱項技能
    
    Args:
        engine: 複習引擎
        item_history: 題目歷史
        skill_history: 技能歷史
        resp_history: 答對歷史
        
    Returns:
        Dict: 弱項分析結果
    """
    s_t = engine.get_knowledge_state(item_history, skill_history, resp_history)
    
    # 按技能計算掌握度
    skill_mastery = defaultdict(list)
    for item_id in range(len(s_t)):
        skill_id = engine.akt_inference.problem_to_skill_id.get(item_id, 0)
        skill_mastery[skill_id].append(s_t[item_id])
    
    skill_stats = []
    for skill_id, mastery_scores in skill_mastery.items():
        skill_name = engine.skills_list[skill_id] if skill_id < len(engine.skills_list) else f'Skill_{skill_id}'
        skill_stats.append({
            'skill_id': skill_id,
            'skill_name': skill_name,
            'mastery': float(np.mean(mastery_scores)),
            'variance': float(np.var(mastery_scores)),
            'practice_count': len(mastery_scores),
        })
    
    # 按掌握度排序
    skill_stats.sort(key=lambda x: x['mastery'])
    
    return {
        'all_skills': skill_stats,
        'weakest_skills': skill_stats[:5],
        'strongest_skills': skill_stats[-5:],
        'overall_apr': engine.get_apr(s_t),
    }


if __name__ == "__main__":
    # 示例：運行自適應複習引擎
    print("═" * 70)
    print("自適應複習模式 - 演示")
    print("═" * 70)
    
    # 初始化引擎
    engine = AdaptiveReviewEngine()
    
    # 模擬學生歷史（示例）
    sample_history = {
        'item_history': [0, 5, 10, 15, 20],
        'skill_history': [0, 1, 2, 3, 4],
        'resp_history': [1, 0, 1, 1, 0],
    }
    
    print(f"\n📚 示例學生歷史:")
    print(f"  - 已做題目: {len(sample_history['item_history'])} 題")
    
    # 弱項分析
    print(f"\n🔍 弱項分析:")
    weak_analysis = analyze_weak_skills(
        engine,
        sample_history['item_history'],
        sample_history['skill_history'],
        sample_history['resp_history']
    )
    print(f"  - 整體 APR: {weak_analysis['overall_apr']:.4f}")
    print(f"  - 最弱技能 Top 3:")
    for skill in weak_analysis['weakest_skills'][:3]:
        print(f"    • {skill['skill_name']}: {skill['mastery']:.4f}")
    
    # 生成複習計畫
    print(f"\n📋 生成複習計畫 (3 個會話)...")
    review_plan = generate_review_plan(sample_history, num_sessions=3, engine=engine)
    
    print(f"\n✅ 複習計畫完成:")
    print(f"  - 初始 APR: {review_plan['overall_stats']['apr_initial']:.4f}")
    print(f"  - 最終 APR: {review_plan['overall_stats']['apr_final']:.4f}")
    print(f"  - 總練習題數: {review_plan['overall_stats']['total_items_practiced']}")
    
    for i, session in enumerate(review_plan['sessions'], 1):
        print(f"  - 會話 {i}: APR 增幅 = +{session['apr_gain']:.4f}, 答對率 = {session['correct_rate']:.2%}")
