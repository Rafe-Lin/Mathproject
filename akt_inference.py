"""
═════════════════════════════════════════════════════════════════
AKT 推論工具 - 用於知識狀態評估和學習指標計算
═════════════════════════════════════════════════════════════════
"""

import os
import torch
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

_DEVICE_NAME = os.getenv("AKT_INFER_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
DEVICE = torch.device(_DEVICE_NAME)
MAX_SEQ_LEN = 50


class AKTInference:
    """
    AKT 推論引擎：用於評估學生知識狀態和能力
    
    核心指標：
    - Knowledge State (sₜ): n_items 維的答對機率向量
    - Item-level APR: 平均每題的答對機率
    - Skill-level APR: 每個技能的掌握度平均值（對小題目集更敏感）
    - Mastery Status: 是否掌握該技能（閾值 > 0.7）
    """
    
    def __init__(self, checkpoint_path: str = './models/akt_curriculum.pth'):
        """
        Args:
            checkpoint_path: AKT 模型的 checkpoint 路徑
        """
        self.ckpt = torch.load(checkpoint_path, map_location=DEVICE, 
                               weights_only=False)
        
        # 重建模型（必須使用與訓練相同的模型結構）
        from train_akt_curriculum import AKT
        self.model = AKT(
            n_items=self.ckpt['n_items'],
            n_skills=self.ckpt['n_skills'],
            embed_dim=self.ckpt['embed_dim'],
            n_heads=self.ckpt['n_heads'],
        ).to(DEVICE)
        
        self.model.load_state_dict(self.ckpt['model_state'])
        self.model.eval()
        
        # 儲存元數據
        self.n_items = self.ckpt['n_items']
        self.n_skills = self.ckpt['n_skills']
        self.skill_to_id = self.ckpt['skill_to_id']
        self.problem_to_id = self.ckpt['problem_to_id']
        self.skills_list = self.ckpt['skills_list']
        
        # 建立反向映射（從 problem_id 到 skill_id）
        self.problem_to_skill_id = {}
        with open('./synthesized_training_data.csv', encoding='utf-8') as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    problem_id = int(parts[1])
                    skill_name = parts[2]
                    if skill_name in self.skill_to_id:
                        skill_id = self.skill_to_id[skill_name]
                        self.problem_to_skill_id[problem_id] = skill_id
        
        print(f"[OK] AKT 推論引擎已載入")
        print(f"  模型版本 AUC：{self.ckpt['best_auc']:.4f}")
        print(f"  技能數：{self.n_skills}，題目數：{self.n_items}\n")

    @torch.no_grad()
    def get_knowledge_state(self, item_history: List[int], 
                           skill_history: List[int],
                           resp_history: List[int]) -> np.ndarray:
        """
        計算當前知識狀態 sₜ（每題的答對機率）
        
        Args:
            item_history: 問題 ID 序列（0-indexed）
            skill_history: 技能 ID 序列（0-indexed）
            resp_history: 正確性序列（0/1）
        
        Returns:
            sₜ: shape (n_items,)，值在 (0, 1)，代表每題的答對機率
        """
        if len(item_history) == 0:
            return np.full(self.n_items, 0.5)

        # 取最近 MAX_SEQ_LEN 步
        item_h = item_history[-MAX_SEQ_LEN:]
        skill_h = skill_history[-MAX_SEQ_LEN:]
        resp_h = resp_history[-MAX_SEQ_LEN:]
        resp_in = [-1] + resp_h[:-1]

        item_t = torch.tensor([item_h], dtype=torch.long).to(DEVICE)
        skill_t = torch.tensor([skill_h], dtype=torch.long).to(DEVICE)
        resp_t = torch.tensor([resp_in], dtype=torch.long).to(DEVICE)

        logits_all, _ = self.model(item_t, skill_t, resp_t)
        last_logits = logits_all[0, -1, :]
        return torch.sigmoid(last_logits).cpu().numpy()

    def get_item_apr(self, item_history: List[int], 
                     skill_history: List[int],
                     resp_history: List[int]) -> float:
        """
        Item-level APR：所有題目答對機率的平均值
        對應論文 Eq.(4)
        
        Returns:
            float in [0, 1]
        """
        s_t = self.get_knowledge_state(item_history, skill_history, resp_history)
        return float(np.mean(s_t))

    def get_skill_apr(self, item_history: List[int],
                      skill_history: List[int],
                      resp_history: List[int]) -> Tuple[float, Dict]:
        """
        Skill-level APR：17個技能掌握度的平均值
        每個技能的掌握度 = 該技能下該題目的答對機率的平均
        
        Returns:
            overall_apr: 全域技能掌握度
            skill_aprs_dict: {skill_name -> skill_apr}
        """
        s_t = self.get_knowledge_state(item_history, skill_history, resp_history)
        skill_aprs = {}
        
        for sid in range(self.n_skills):
            # 找出所有屬於該技能的題目
            skill_problems = [
                pid for pid, skill_id in self.problem_to_skill_id.items()
                if skill_id == sid and pid < self.n_items
            ]
            
            if skill_problems:
                skill_aprs[self.skills_list[sid]] = float(
                    np.mean([s_t[pid] for pid in skill_problems])
                )
            else:
                skill_aprs[self.skills_list[sid]] = 0.5

        overall_apr = float(np.mean(list(skill_aprs.values())))
        return overall_apr, skill_aprs

    def get_skill_mastery(self, item_history: List[int],
                          skill_history: List[int],
                          resp_history: List[int],
                          threshold: float = 0.7) -> Dict[str, bool]:
        """
        判斷學生是否已掌握各技能（閾值：APR > 0.7）
        
        Returns:
            {skill_name -> is_mastered (bool)}
        """
        _, skill_aprs = self.get_skill_apr(item_history, skill_history, resp_history)
        return {skill: apr >= threshold for skill, apr in skill_aprs.items()}

    def get_assessment_report(self, item_history: List[int],
                              skill_history: List[int],
                              resp_history: List[int]) -> Dict:
        """
        生成完整的學生能力評估報告
        
        Returns:
            {
                'item_apr': float,
                'skill_apr': float,
                'skill_aprs': {skill_name -> float},
                'skill_mastery': {skill_name -> bool},
                'accuracy': float (歷史正確率),
                'total_attempts': int,
                'recommendations': [str]  # 學習建議
            }
        """
        item_apr = self.get_item_apr(item_history, skill_history, resp_history)
        skill_apr, skill_aprs = self.get_skill_apr(item_history, skill_history, 
                                                    resp_history)
        skill_mastery = self.get_skill_mastery(item_history, skill_history, 
                                               resp_history)
        
        accuracy = np.mean(resp_history) if resp_history else 0.0
        total_attempts = len(resp_history)
        
        # 生成建議
        recommendations = []
        unmastered = [s for s, m in skill_mastery.items() if not m]
        mastered = [s for s, m in skill_mastery.items() if m]
        
        if unmastered:
            lowest_skill = min(unmastered, key=lambda s: skill_aprs[s])
            recommendations.append(
                f"重點補強：{lowest_skill} (APR: {skill_aprs[lowest_skill]:.1%})"
            )
        
        if accuracy < 0.4:
            recommendations.append("建議降低難度，加強基礎概念")
        elif accuracy > 0.9:
            recommendations.append("考慮提升難度，挑戰更難題目")
        
        if len(mastered) > 0:
            recommendations.append(
                f"已掌握：{', '.join(mastered[:3])}" + 
                (f" 等 {len(mastered)} 個技能" if len(mastered) > 3 else "")
            )
        
        return {
            'item_apr': item_apr,
            'skill_apr': skill_apr,
            'skill_aprs': skill_aprs,
            'skill_mastery': skill_mastery,
            'accuracy': accuracy,
            'total_attempts': total_attempts,
            'recommendations': recommendations,
        }

    def print_report(self, report: Dict):
        """美化打印評估報告."""
        from datetime import datetime
        
        print("\n" + "="*70)
        print(f"AKT 學生能力評估報告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*70)
        
        print(f"\n【整體能力指標】")
        print(f"  Item-level APR (平均答對率)：{report['item_apr']:.1%}")
        print(f"  Skill-level APR (技能掌握度)：{report['skill_apr']:.1%}")
        print(f"  歷史正確率：{report['accuracy']:.1%}")
        print(f"  總作答數：{report['total_attempts']} 題")
        
        print(f"\n【各技能掌握度】")
        skill_aprs = sorted(report['skill_aprs'].items(), 
                           key=lambda x: x[1], reverse=True)
        for skill, apr in skill_aprs:
            status = "[OK] 掌握" if report['skill_mastery'][skill] else "[X] 待加強"
            print(f"  {skill:<50} {apr:6.1%}  [{status}]")
        
        print(f"\n【學習建議】")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print("="*70 + "\n")


# =============================================
# 使用示例
# =============================================
if __name__ == "__main__":
    print("AKT 推論工具示例\n")
    
    try:
        inference = AKTInference('./models/akt_curriculum.pth')
        
        # 模擬學生的作答序列
        # 假設學生做了 15 題，涉及 5 個技能
        demo_items = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
        demo_skills = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]
        demo_responses = [1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0]
        
        print("模擬學生序列：")
        print(f"  作答題目：{demo_items}")
        print(f"  涉及技能：{demo_skills}")
        print(f"  作答結果：{demo_responses}")
        
        # 計算知識狀態
        s_t = inference.get_knowledge_state(demo_items, demo_skills, demo_responses)
        print(f"\n知識狀態 (前 10 題答對機率)：{s_t[:10].round(3)}")
        
        # 計算指標
        item_apr = inference.get_item_apr(demo_items, demo_skills, demo_responses)
        skill_apr, skill_aprs = inference.get_skill_apr(demo_items, demo_skills, 
                                                        demo_responses)
        
        print(f"Item-level APR：{item_apr:.1%}")
        print(f"Skill-level APR：{skill_apr:.1%}")
        
        # 生成完整報告
        report = inference.get_assessment_report(demo_items, demo_skills, 
                                                 demo_responses)
        inference.print_report(report)
        
    except FileNotFoundError as e:
        print(f"[X] 錯誤：{e}")
        print("請先執行 train_akt_curriculum.py 訓練模型")
