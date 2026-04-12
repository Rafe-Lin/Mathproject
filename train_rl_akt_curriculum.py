"""
基於現有題庫 (212 題) 與已訓練 AKT 模型 (akt_curriculum.pth) 的強化學習訓練腳本。
改編自 RL_model_example.py，對接到 akt_inference.py。
"""

import sys, os
import numpy as np
import torch
import torch.nn as nn
import gymnasium as gym
from gymnasium import spaces
import pandas as pd
from collections import defaultdict
from scipy.stats import mannwhitneyu

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 匯入現有的 AKT 推論工具
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from akt_inference import AKTInference

# ==========================================
# 0. 全域設定
# ==========================================
MODEL_PATH = './models/akt_curriculum.pth'
DATA_PATH  = './synthesized_training_data.csv'

# 載入 AKT 推論引擎
inference = AKTInference(MODEL_PATH)

N_SKILLS  = inference.n_skills     # 17
N_ITEMS   = inference.n_items      # 212
BETA      = 0.65                   # 達標閾值
MAX_STEPS = 60                     # 每輪最大步數
TIMESTEPS = 500_000                # 訓練步數
N_EVAL    = 100                    # 評估輪數

FIGS_DIR = './figures/rl_akt_curriculum'
RES_DIR  = './results/rl_akt_curriculum'
MODELS_DIR = './models/rl_akt_curriculum'
os.makedirs(FIGS_DIR, exist_ok=True)
os.makedirs(RES_DIR,  exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

PPO_KWARGS = dict(
    learning_rate = 3e-4,
    n_steps       = 2048,
    batch_size    = 64,
    n_epochs      = 10,
    gamma         = 0.99,
    gae_lambda    = 0.95,
    ent_coef      = 0.01,
    clip_range    = 0.2,
    max_grad_norm = 0.5,
    verbose       = 0,
)

# 多目標獎勵權重
W_LEARN = 1.0
W_FRUST = 0.3
W_BORED = 0.2
W_DIVER = 0.4
W_EFFIC = 0.1

COLORS = {
    'Random'    : '#B4B2A9',
    'Greedy-ZPD': '#888780',
    'PPO-Best'  : '#1D9E75',
}
LABELS = {
    'Random'    : 'Random',
    'Greedy-ZPD': 'Greedy-ZPD',
    'PPO-Best'  : 'PPO (Multi-Obj + Item)',
}

# ==========================================
# 1. 資料工具
# ==========================================

def compute_skill_apr(s_t, problem_to_skill_id, n_skills):
    """計算全校技能平均掌握度"""
    skill_states = defaultdict(list)
    for pid, sid in problem_to_skill_id.items():
        if pid < len(s_t):
            skill_states[sid].append(s_t[pid])
    
    if not skill_states:
        return 0.5
        
    skill_means = [np.mean(vals) for vals in skill_states.values()]
    return float(np.mean(skill_means))

def build_student_pool(data_path, problem_to_id, skill_to_id, n_total=500, init_steps=5, seed=42):
    """從 CSV 建立學生初始狀態池"""
    df = pd.read_csv(data_path, encoding='utf-8')
    # 確保資料格式轉換正確
    df['item_id']  = df['problemId'].map(problem_to_id)
    df['skill_id'] = df['skill'].map(skill_to_id)
    df = df.dropna(subset=['item_id', 'skill_id'])
    
    rng = np.random.RandomState(seed)
    students = df['studentId'].unique()
    rng.shuffle(students)
    
    pool = []
    for sid in students:
        sdf = df[df['studentId'] == sid].sort_index()
        if len(sdf) < init_steps + 2:
            continue
        init = sdf.iloc[:init_steps]
        pool.append({
            'item_history' : init['item_id'].values.astype(int).tolist(),
            'skill_history': init['skill_id'].values.astype(int).tolist(),
            'resp_history' : init['correct'].values.astype(int).tolist(),
        })
        if len(pool) >= n_total:
            break
            
    split = int(len(pool) * 0.8)
    return pool[:split], pool[split:]

def build_item_maps(data_path, problem_to_id):
    """建立題目與屬性的對照關係"""
    df = pd.read_csv(data_path, encoding='utf-8')
    df['item_id'] = df['problemId'].map(problem_to_id)
    df = df.dropna(subset=['item_id'])
    df['item_id'] = df['item_id'].astype(int)
    
    item_difficulty = df.groupby('item_id')['correct'].mean().to_dict()
    return item_difficulty

def strat_max_fisher(s_t, visited, n_items):
    """Max-Fisher 策略：選擇不確定性最高的題目"""
    fi = s_t[:n_items] * (1.0 - s_t[:n_items])
    # 設置已做過的題目權重為極小
    for j in visited:
        if j < n_items:
            fi[j] = -1.0
    return int(np.argmax(fi))

# ==========================================
# 2. 環境：RL 訓練環境
# ==========================================

class AKTEnv(gym.Env):
    def __init__(self, inference, student_pool, item_difficulty, beta=BETA, max_steps=MAX_STEPS, seed=0):
        super().__init__()
        self.inference       = inference
        self.student_pool    = student_pool
        self.item_difficulty = item_difficulty
        self.n_items         = inference.n_items
        self.n_skills        = inference.n_skills
        self.beta            = beta
        self.max_steps       = max_steps
        self.rng             = np.random.RandomState(seed)
        
        # 動作空間：直接選擇 212 題中的一題
        self.action_space = spaces.Discrete(self.n_items)
        # 狀態空間：當前每題的預測答對率
        self.observation_space = spaces.Box(0.0, 1.0, shape=(self.n_items,), dtype=np.float32)

    def _get_apr(self):
        # 計算 Skill-level APR
        apr, _ = self.inference.get_skill_apr(self.item_history, self.skill_history, self.resp_history)
        return apr

    def _compute_reward(self, new_apr, p_correct, is_correct, item_id):
        d_t  = max(self.beta - self.current_apr, 1e-6)
        lg_t = new_apr - self.current_apr

        # 1. 學習增益
        r_learning = lg_t * self.n_skills / d_t

        # 2. 挫折感懲罰 (連續答錯)
        fails_capped = min(self.consecutive_fails, 5)
        r_frust = -(fails_capped ** 1.2) * 0.15

        # 3. 無聊感懲罰 (太簡單)
        r_bored = 0.0
        if is_correct == 1 and p_correct > 0.85:
            r_bored = -max(0.0, (p_correct - 0.85) * 1.0)

        # 4. 多樣性懲罰 (重複題或過度集中單一技能)
        r_diver = 0.0
        if item_id in self.visited_items:
            r_diver -= 2.0  # 強力禁止重複
        if self.consecutive_same_skill > 2:
            r_diver -= (self.consecutive_same_skill - 2) * 0.2

        # 5. 效率懲罰
        progress = self.step_count / self.max_steps
        r_effic  = -0.05 * (1 + progress)

        reward = (W_LEARN * r_learning + W_FRUST * r_frust +
                  W_BORED * r_bored   + W_DIVER * r_diver +
                  W_EFFIC * r_effic)

        if new_apr >= self.beta:
            reward += 3.0

        return float(reward)

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.rng = np.random.RandomState(seed)
        
        # 隨機選擇一位學生作為起始狀態
        student = self.student_pool[self.rng.randint(0, len(self.student_pool))]
        self.item_history  = list(student['item_history'])
        self.skill_history = list(student['skill_history'])
        self.resp_history  = list(student['resp_history'])
        
        self.s_t = self.inference.get_knowledge_state(self.item_history, self.skill_history, self.resp_history)
        self.current_apr = self._get_apr()
        
        self.step_count             = 0
        self.visited_items          = set(self.item_history)
        self.visited_skills         = list(self.skill_history)
        self.consecutive_fails      = 0
        self.consecutive_same_skill = 1
        self.last_skill             = self.skill_history[-1] if self.skill_history else -1
        self.total_correct          = 0
        
        return self.s_t.astype(np.float32), {}

    def step(self, action):
        self.step_count += 1
        item_id = int(action)
        
        # 如果模型選到做過的題目，Fallback 到 Max-Fisher (增加探索性)
        if item_id in self.visited_items:
            item_id = strat_max_fisher(self.s_t, self.visited_items, self.n_items)
            
        skill_id = self.inference.problem_to_skill_id.get(item_id, 0)
        p_correct = float(self.s_t[item_id]) if item_id < len(self.s_t) else 0.5
        is_correct = 1 if self.rng.rand() < p_correct else 0
        
        # 更新歷史
        self.item_history.append(item_id)
        self.skill_history.append(skill_id)
        self.resp_history.append(is_correct)
        self.visited_items.add(item_id)
        self.visited_skills.append(skill_id)
        self.total_correct += is_correct
        
        if is_correct == 0:
            self.consecutive_fails += 1
        else:
            self.consecutive_fails = 0
            
        if skill_id == self.last_skill:
            self.consecutive_same_skill += 1
        else:
            self.consecutive_same_skill = 1
            self.last_skill = skill_id
            
        # 更新狀態與計算獎勵
        self.s_t = self.inference.get_knowledge_state(self.item_history, self.skill_history, self.resp_history)
        new_apr = self._get_apr()
        reward = self._compute_reward(new_apr, p_correct, is_correct, item_id)
        
        terminated = bool(new_apr >= self.beta)
        truncated  = bool(self.step_count >= self.max_steps)
        self.current_apr = new_apr
        
        info = {
            'item_id': item_id,
            'skill_id': skill_id,
            'p_correct': p_correct,
            'is_correct': is_correct,
            'apr': new_apr,
            'correct_rate': self.total_correct / self.step_count
        }
        
        return self.s_t.astype(np.float32), reward, terminated, truncated, info

# ==========================================
# 3. Callback
# ==========================================

class ConvergenceCallback(BaseCallback):
    def __init__(self, eval_env, eval_freq=20_000, n_ep=20, verbose=1):
        super().__init__(verbose)
        self.eval_env = eval_env
        self.eval_freq = eval_freq
        self.n_ep = n_ep
        self.history = []

    def _on_step(self):
        if self.n_calls % self.eval_freq != 0:
            return True
        aprs = []
        succs = []
        for ep in range(self.n_ep):
            obs, _ = self.eval_env.reset(seed=ep)
            done = False
            curr_apr = 0
            for _ in range(MAX_STEPS):
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = self.eval_env.step(action)
                curr_apr = info['apr']
                if terminated or truncated:
                    break
            aprs.append(curr_apr)
            succs.append(1 if curr_apr >= BETA else 0)
        
        mean_apr = np.mean(aprs)
        sr = np.mean(succs)
        self.history.append({'timestep': self.n_calls, 'mean_apr': mean_apr, 'success_rate': sr})
        if self.verbose:
            print(f"Step {self.n_calls}: APR={mean_apr:.4f}, Success Rate={sr:.2f}")
        return True

# ==========================================
# 4. 訓練
# ==========================================

def train(train_pool, test_pool, item_difficulty, seed=0):
    env_kwargs = {
        'inference': inference,
        'item_difficulty': item_difficulty,
        'beta': BETA,
        'max_steps': MAX_STEPS
    }
    
    def make_env(pool, s):
        return Monitor(AKTEnv(student_pool=pool, seed=s, **env_kwargs))

    train_env = DummyVecEnv([lambda: make_env(train_pool, seed)])
    train_env = VecNormalize(train_env, norm_obs=False, norm_reward=True, clip_reward=10.0)
    
    eval_env = AKTEnv(student_pool=test_pool, seed=seed+1, **env_kwargs)
    cb = ConvergenceCallback(eval_env, eval_freq=10_000)

    model = PPO(
        "MlpPolicy", train_env, seed=seed,
        policy_kwargs=dict(net_arch=[512, 256], activation_fn=nn.ReLU),
        **PPO_KWARGS
    )
    
    print(f"開始訓練 RL 模型 (基於現有題庫)... 預計 {TIMESTEPS} steps")
    model.learn(total_timesteps=TIMESTEPS, callback=cb)
    
    model.save(f"{MODELS_DIR}/ppo_akt_curriculum")
    return model, cb.history

# ==========================================
# 5. 評估與繪圖
# ==========================================

def evaluate(model, env, n_episodes=100, strategy='model'):
    results = []
    for ep in range(n_episodes):
        obs, _ = env.reset(seed=ep+1000)
        done = False
        steps = 0
        while not done and steps < MAX_STEPS:
            if strategy == 'model':
                action, _ = model.predict(obs, deterministic=True)
            elif strategy == 'random':
                action = env.action_space.sample()
            elif strategy == 'greedy-zpd':
                action = strat_max_fisher(env.s_t, env.visited_items, env.n_items)
                
            obs, r, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            steps += 1
            
        results.append({
            'final_apr': info['apr'],
            'steps': steps,
            'success': 1 if info['apr'] >= BETA else 0,
            'correct_rate': info['correct_rate']
        })
    return results

def plot_results(history, all_results):
    df_hist = pd.DataFrame(history)
    if not df_hist.empty:
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.plot(df_hist['timestep'], df_hist['mean_apr'])
        plt.title('Training APR')
        plt.subplot(1, 2, 2)
        plt.plot(df_hist['timestep'], df_hist['success_rate'])
        plt.title('Success Rate')
        plt.savefig(f"{FIGS_DIR}/training_progress.png")
        plt.close()
    
    # 建立比較表
    summary = []
    for name, res in all_results.items():
        summary.append({
            'Strategy': name,
            'Mean APR': np.mean([r['final_apr'] for r in res]),
            'Success Rate': np.mean([r['success'] for r in res]),
            'Avg Steps': np.mean([r['steps'] for r in res])
        })
    df_sum = pd.DataFrame(summary)
    df_sum.to_csv(f"{RES_DIR}/summary_comparison.csv", index=False)
    print("\n比較結果：")
    print(df_sum)

# ==========================================
# 主程式
# ==========================================

def main():
    print(f"載入題庫與學生池資料...")
    train_pool, test_pool = build_student_pool(DATA_PATH, inference.problem_to_id, inference.skill_to_id)
    item_difficulty = build_item_maps(DATA_PATH, inference.problem_to_id)
    
    print(f"學生池大小: Train={len(train_pool)}, Test={len(test_pool)}")
    
    # 1. 訓練
    model, history = train(train_pool, test_pool, item_difficulty)
    
    # 2. 評估多種策略
    print("\n進行策略對比評估...")
    eval_env = AKTEnv(inference, test_pool, item_difficulty, seed=999)
    
    all_results = {}
    all_results['PPO-Best'] = evaluate(model, eval_env, strategy='model')
    all_results['Random'] = evaluate(model, eval_env, strategy='random')
    all_results['Greedy-ZPD'] = evaluate(model, eval_env, strategy='greedy-zpd')
    
    # 3. 視覺化
    plot_results(history, all_results)
    print(f"\n訓練與評估完成。")
    print(f"模型存於: {MODELS_DIR}/")
    print(f"圖表存於: {FIGS_DIR}/")
    print(f"統計存於: {RES_DIR}/")

if __name__ == "__main__":
    main()
