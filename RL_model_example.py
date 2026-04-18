"""
最佳方案：多目標獎勵函數 + Item-level 動作空間
結合：
  - reward_comparison.py 的多目標獎勵函數（MultiObj）
  - rl_experiment_v2.py 的 Item-level 動作空間 + 500k 訓練步數
  - train/test pool 分割（80/20）確保評估嚴謹性
  - 完整 7 項指標 + 統計顯著性檢定
  - 與 Random / Greedy-ZPD 基線比較
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from akt_v2 import AKT, AKTInference, load_model, SKILLS_LIST, DEVICE

# ==========================================
# 0. 全域設定
# ==========================================
N_SKILLS  = len(SKILLS_LIST)   # 24
BETA      = 0.65
MAX_STEPS = 60
TIMESTEPS = 500_000            # Item-level 動作空間需要較多步數收斂
N_EVAL    = 100

FIGS_DIR = './figures/best_model'
RES_DIR  = './results/best_model'
os.makedirs(FIGS_DIR, exist_ok=True)
os.makedirs(RES_DIR,  exist_ok=True)

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

def compute_skill_apr(s_t, skill_to_items, n_items):
    skill_aprs = []
    for sid, items in skill_to_items.items():
        valid = [j for j in items if j < n_items]
        if valid:
            skill_aprs.append(float(np.mean(s_t[valid])))
    return float(np.mean(skill_aprs)) if skill_aprs else 0.5


def build_student_pool(data_path, problem_to_id, skill_to_id,
                        n_total=500, init_steps=5, seed=42):
    df = pd.read_csv(data_path, low_memory=False)
    df = df[df['skill'].isin(SKILLS_LIST)].copy()
    df = df.dropna(subset=['problemId', 'skill', 'correct'])
    df['correct']  = df['correct'].astype(int).clip(0, 1)
    df['item_id']  = df['problemId'].map(problem_to_id)
    df['skill_id'] = df['skill'].map(skill_to_id)
    df = df.dropna(subset=['item_id', 'skill_id'])

    rng      = np.random.RandomState(seed)
    students = df['studentId'].unique()
    rng.shuffle(students)

    pool = []
    for sid in students:
        sdf = df[df['studentId'] == sid]
        if len(sdf) < init_steps + 2:
            continue
        init = sdf.iloc[:init_steps]
        pool.append({
            'item_history' : (init['item_id'].values.astype(int) + 1).tolist(),
            'skill_history': init['skill_id'].values.astype(int).tolist(),
            'resp_history' : init['correct'].values.astype(int).tolist(),
        })
        if len(pool) >= n_total:
            break

    split      = int(len(pool) * 0.8)
    train_pool = pool[:split]
    test_pool  = pool[split:]
    print(f"學生池: {len(pool)} 位 → train {len(train_pool)} / test {len(test_pool)}")
    return train_pool, test_pool


def build_item_maps(data_path, problem_to_id, skill_to_id):
    df = pd.read_csv(data_path, low_memory=False)
    df = df[df['skill'].isin(SKILLS_LIST)].copy()
    df = df.dropna(subset=['problemId', 'skill', 'correct'])
    df['correct']  = df['correct'].astype(int).clip(0, 1)
    df['item_id']  = df['problemId'].map(problem_to_id)
    df['skill_id'] = df['skill'].map(skill_to_id)
    df = df.dropna(subset=['item_id', 'skill_id'])
    df['item_id']  = df['item_id'].astype(int)
    df['skill_id'] = df['skill_id'].astype(int)

    item_to_skill  = dict(zip(df['item_id'], df['skill_id']))
    skill_to_items = defaultdict(list)
    for iid, sid in item_to_skill.items():
        if iid not in skill_to_items[sid]:
            skill_to_items[sid].append(iid)
    item_difficulty = df.groupby('item_id')['correct'].mean().to_dict()
    return item_to_skill, dict(skill_to_items), item_difficulty


def strat_max_fisher(s_t, visited, n_items):
    fi = s_t[:n_items] * (1.0 - s_t[:n_items])
    for j in visited:
        if j < n_items:
            fi[j] = -1.0
    return int(np.argmax(fi))


# ==========================================
# 2. 環境：多目標獎勵 + Item-level 動作空間
# ==========================================

class BestModelEnv(gym.Env):
    """
    最佳方案環境：
      動作空間：Item-level（|A| = n_items，直接選題目）
      獎勵函數：多目標（r_learn + r_frust + r_bored + r_diver + r_effic）
    """
    metadata = {'render_modes': []}

    def __init__(self, inference, student_pool, item_to_skill,
                 skill_to_items, item_difficulty, n_items,
                 beta=BETA, max_steps=MAX_STEPS, seed=0):
        super().__init__()
        self.inference       = inference
        self.student_pool    = student_pool
        self.item_to_skill   = item_to_skill
        self.skill_to_items  = skill_to_items
        self.item_difficulty = item_difficulty
        self.n_items         = n_items
        self.beta            = beta
        self.max_steps       = max_steps
        self.rng             = np.random.RandomState(seed)

        self.action_space      = spaces.Discrete(n_items)
        self.observation_space = spaces.Box(
            0.0, 1.0, shape=(n_items,), dtype=np.float32)

    def _get_apr(self):
        return compute_skill_apr(self.s_t, self.skill_to_items, self.n_items)

    def _compute_reward(self, new_apr, p_correct, is_correct, item_id):
        d_t  = max(self.beta - self.current_apr, 1e-6)
        lg_t = new_apr - self.current_apr

        # 學習增益（多目標核心）
        r_learning = lg_t * N_SKILLS / d_t

        # 挫折感懲罰：連續答錯越多次懲罰越重
        fails_capped = min(self.consecutive_fails, 5)
        r_frust = -(fails_capped ** 1.2) * 0.15

        # 無聊感懲罰：題目太簡單（預測答對率 > 85%）
        r_bored = 0.0
        if is_correct == 1 and p_correct > 0.85:
            r_bored = -max(0.0, (p_correct - 0.85) * 1.0)

        # 多樣性懲罰：重複題目或連續同知識點
        r_diver = 0.0
        if item_id in self.visited_items:
            r_diver -= 1.5
        if self.consecutive_same_skill > 2:
            r_diver -= (self.consecutive_same_skill - 2) * 0.2

        # 效率懲罰：漸進式步數懲罰
        progress = self.step_count / self.max_steps
        r_effic  = -0.05 * (1 + progress)

        reward = (W_LEARN * r_learning + W_FRUST * r_frust +
                  W_BORED * r_bored   + W_DIVER * r_diver +
                  W_EFFIC * r_effic)

        # 達標額外獎勵
        if new_apr >= self.beta:
            reward += 3.0

        return float(reward)

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.rng = np.random.RandomState(seed)

        student = self.student_pool[
            self.rng.randint(0, len(self.student_pool))]
        self.item_history  = list(student['item_history'])
        self.skill_history = list(student['skill_history'])
        self.resp_history  = list(student['resp_history'])

        self.s_t         = self.inference.get_knowledge_state(
            self.item_history, self.skill_history, self.resp_history)
        self.current_apr = self._get_apr()
        self.initial_apr = self.current_apr

        self.step_count             = 0
        self.visited_items          = set(i - 1 for i in self.item_history)
        self.visited_skills         = list(self.skill_history)
        self.consecutive_fails      = 0
        self.consecutive_same_skill = 1
        self.last_skill             = (self.skill_history[-1]
                                       if self.skill_history else -1)
        self.total_correct          = 0

        return self.s_t.astype(np.float32), {}

    def step(self, action):
        self.step_count += 1

        # Item-level 動作空間：直接選題，若已做過則 fallback Max-Fisher
        item_id = int(action)
        if item_id in self.visited_items:
            item_id = strat_max_fisher(self.s_t, self.visited_items, self.n_items)

        skill_id   = self.item_to_skill.get(item_id, 0)
        p_correct  = float(self.s_t[item_id]) if item_id < len(self.s_t) else 0.5
        is_correct = 1 if self.rng.rand() < p_correct else 0

        self.item_history.append(item_id + 1)
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

        self.s_t     = self.inference.get_knowledge_state(
            self.item_history, self.skill_history, self.resp_history)
        new_apr      = self._get_apr()
        reward       = self._compute_reward(new_apr, p_correct, is_correct, item_id)
        terminated   = bool(new_apr >= self.beta)
        truncated    = bool(self.step_count >= self.max_steps)
        self.current_apr = new_apr

        info = dict(
            item_id      = item_id,
            skill_id     = skill_id,
            p_correct    = p_correct,
            is_correct   = is_correct,
            apr          = new_apr,
            reward       = reward,
            correct_rate = self.total_correct / max(self.step_count, 1),
        )
        return self.s_t.astype(np.float32), reward, terminated, truncated, info


# ==========================================
# 3. Callback
# ==========================================

class ConvergenceCallback(BaseCallback):
    def __init__(self, eval_env, eval_freq=20_000, n_ep=20, verbose=1):
        super().__init__(verbose)
        self.eval_env  = eval_env
        self.eval_freq = eval_freq
        self.n_ep      = n_ep
        self.history   = []

    def _on_step(self):
        if self.n_calls % self.eval_freq != 0:
            return True
        env   = self.eval_env
        aprs, succs = [], []
        for ep in range(self.n_ep):
            obs, _ = env.reset(seed=ep)
            apr, ok = env.current_apr, False
            for _ in range(MAX_STEPS):
                act, _ = self.model.predict(obs, deterministic=True)
                obs, _, terminated, truncated, info = env.step(act)
                apr = info['apr']
                if apr >= BETA: ok = True
                if terminated or truncated: break
            aprs.append(apr); succs.append(int(ok))
        self.history.append(dict(
            timestep     = self.n_calls,
            mean_apr     = float(np.mean(aprs)),
            success_rate = float(np.mean(succs)),
        ))
        if self.verbose:
            print(f"  t={self.n_calls:>7d} | APR={np.mean(aprs):.4f} "
                  f"| SR={np.mean(succs):.3f}")
        return True


# ==========================================
# 4. 訓練
# ==========================================

def train(env_kw, seed=0):
    train_env = DummyVecEnv([
        lambda: Monitor(BestModelEnv(**{**env_kw, 'seed': seed}))
    ])
    train_env = VecNormalize(
        train_env, norm_obs=False, norm_reward=True, clip_reward=10.0)

    eval_env = BestModelEnv(**{**env_kw, 'seed': seed + 1})
    cb       = ConvergenceCallback(eval_env, eval_freq=20_000,
                                    n_ep=20, verbose=1)

    model = PPO(
        "MlpPolicy", train_env, seed=seed,
        policy_kwargs=dict(net_arch=[512, 256], activation_fn=nn.ReLU),
        **PPO_KWARGS
    )
    print(f"\n訓練 PPO (Multi-Obj + Item-level) | {TIMESTEPS:,} steps")
    model.learn(total_timesteps=TIMESTEPS, callback=cb, progress_bar=False)

    os.makedirs('./models/best_model', exist_ok=True)
    model.save('./models/best_model/ppo_best_seed0')
    train_env.close()
    return model, cb.history


# ==========================================
# 5. 評估（7 項指標）
# ==========================================

def evaluate(model_or_strategy, env, n_episodes=N_EVAL, seed=0):
    results, paths = [], []

    for ep in range(n_episodes):
        obs, _ = env.reset(seed=seed + ep)
        total_r, steps, success, n_fails = 0.0, 0, False, 0
        path = []

        for _ in range(MAX_STEPS):
            if isinstance(model_or_strategy, str):
                if model_or_strategy == 'random':
                    avail  = list(set(range(env.n_items)) - env.visited_items)
                    action = np.random.choice(avail) if avail else 0
                else:  # greedy-zpd
                    action = strat_max_fisher(
                        env.s_t, env.visited_items, env.n_items)
            else:
                action, _ = model_or_strategy.predict(obs, deterministic=True)
                action     = int(action)

            obs, r, terminated, truncated, info = env.step(action)
            total_r += r; steps += 1
            path.append(info['item_id'])
            if info['is_correct'] == 0: n_fails += 1
            if info['apr'] >= BETA: success = True
            if terminated or truncated: break

        paths.append(path)
        results.append(dict(
            final_apr        = info['apr'],
            steps            = steps,
            success          = int(success),
            total_reward     = total_r,
            n_fails          = n_fails,
            n_skills         = len(set(env.visited_skills)),
            correct_rate     = info.get('correct_rate', 0),
            steps_to_mastery = steps if success else float('nan'),
        ))

    return _agg(results, paths)


def _agg(results, paths):
    keys = ['final_apr','steps','success','total_reward',
            'n_fails','n_skills','correct_rate']
    out  = {}
    for k in keys:
        vals = [r[k] for r in results]
        out[f'{k}_mean'] = float(np.mean(vals))
        out[f'{k}_std']  = float(np.std(vals))
        out[f'{k}_all']  = vals

    stm = [r['steps_to_mastery'] for r in results
           if not np.isnan(r['steps_to_mastery'])]
    out['steps_to_mastery_mean'] = float(np.mean(stm)) if stm else float('nan')
    out['steps_to_mastery_std']  = float(np.std(stm))  if stm else float('nan')
    out['steps_to_mastery_all']  = stm
    out['div'] = _compute_div(paths)
    return out


def _compute_div(paths):
    N = len(paths)
    if N < 2: return 0.0
    total, count = 0.0, 0
    for i in range(N):
        pi = set(paths[i]); li = max(len(paths[i]), 1)
        for j in range(N):
            if i != j:
                total += 1.0 - len(pi & set(paths[j])) / li
                count += 1
    return total / count if count > 0 else 0.0


# ==========================================
# 6. 統計檢定
# ==========================================

def stat_test(res_a, res_b, metric='final_apr'):
    a = res_a.get(f'{metric}_all', [])
    b = res_b.get(f'{metric}_all', [])
    if len(a) < 2 or len(b) < 2:
        return {'p': 1.0, 'stars': 'ns', 'dir': '?'}
    _, p = mannwhitneyu(a, b, alternative='two-sided')
    return {
        'p'    : float(p),
        'stars': '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns',
        'dir'  : 'PPO>Base' if np.mean(a) > np.mean(b) else 'Base>PPO',
    }


# ==========================================
# 7. 視覺化
# ==========================================

def plot_all(all_results, history):
    valid   = ['Random', 'Greedy-ZPD', 'PPO-Best']
    colors  = [COLORS[s] for s in valid]
    labels  = [LABELS[s]  for s in valid]
    x       = np.arange(len(valid))

    plt.rcParams.update({
        'font.family'    : 'DejaVu Sans',
        'font.size'      : 11,
        'axes.titlesize' : 13,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid'      : True,
        'grid.alpha'     : 0.25,
        'grid.linestyle' : '--',
        'figure.dpi'     : 150,
        'savefig.dpi'    : 200,
    })

    # ── Fig 1：訓練收斂曲線 ──────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    df_hist = pd.DataFrame(history)
    for ax, col, ylabel, title in [
        (axes[0], 'mean_apr',     'Mean Skill-APR', 'APR Convergence'),
        (axes[1], 'success_rate', 'Success Rate',   'Success Rate Convergence'),
    ]:
        ax.plot(df_hist['timestep'], df_hist[col],
                color='#1D9E75', linewidth=2.2, label='PPO (Multi-Obj + Item)')
        ax.axhline(y=BETA, color='#E24B4A', linestyle='--',
                   linewidth=1.3, label=f'β={BETA}')
        ax.set_xlabel('Training Timesteps')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(fontsize=9)
        if 'apr' in col: ax.set_ylim(0.3, 0.85)
        else:            ax.set_ylim(0, 1.05)
    fig.suptitle('PPO (Multi-Obj + Item-level) Training Convergence',
                 fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(f'{FIGS_DIR}/fig1_convergence.png')
    plt.close(fig)

    # ── Fig 2：多指標長條圖 ──────────────────────────────
    metrics_cfg = [
        ('final_apr_mean',        'final_apr_std',  'Skill-APR',     (0.3, 0.85)),
        ('success_mean',          None,             'Success Rate',  (0.0, 1.05)),
        ('steps_to_mastery_mean', None,             'Steps (ok)',    (0, None)),
        ('correct_rate_mean',     None,             'Correct Rate',  (0.0, 1.05)),
        ('n_fails_mean',          None,             'Frustrations',  (0, None)),
        ('div',                   None,             'DIV',           (0, 1.05)),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    axes = axes.flatten()

    for idx, (key, std_key, title, ylim) in enumerate(metrics_cfg):
        ax   = axes[idx]
        vals = [all_results[s].get(key, float('nan')) for s in valid]
        errs = ([all_results[s].get(std_key, 0) for s in valid]
                if std_key else None)

        bars = ax.bar(x, vals, color=colors, width=0.55,
                      yerr=errs, capsize=4,
                      error_kw={'linewidth': 1.2})
        for bar, v in zip(bars, vals):
            if not np.isnan(v):
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 0.008,
                        f'{v:.3f}', ha='center', va='bottom', fontsize=9)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=10, ha='right', fontsize=9.5)
        ax.set_title(title, fontweight='normal')
        if ylim[0] is not None: ax.set_ylim(bottom=ylim[0])
        if ylim[1] is not None: ax.set_ylim(top=ylim[1])
        if 'apr' in key:
            ax.axhline(y=BETA, color='#E24B4A', linestyle='--',
                       linewidth=1.2, label=f'β={BETA}')
            ax.legend(fontsize=8)

    fig.suptitle('PPO (Multi-Obj + Item-level) vs Baselines',
                 fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(f'{FIGS_DIR}/fig2_metrics.png')
    plt.close(fig)

    # ── Fig 3：APR 分布 Violin ───────────────────────────
    apr_data = [all_results[s]['final_apr_all'] for s in valid
                if 'final_apr_all' in all_results[s]]
    if apr_data:
        fig, ax = plt.subplots(figsize=(8, 5))
        parts = ax.violinplot(apr_data, positions=range(len(valid)),
                              showmeans=True, showmedians=True, widths=0.6)
        for pc, color in zip(parts['bodies'], colors):
            pc.set_facecolor(color); pc.set_alpha(0.7)
        parts['cmedians'].set_color('white')
        parts['cmedians'].set_linewidth(2)
        for i, (s, data) in enumerate(zip(valid, apr_data)):
            m, sd = np.mean(data), np.std(data)
            ax.text(i, max(data)+0.01, f'{m:.3f}±{sd:.3f}',
                    ha='center', va='bottom', fontsize=9,
                    color=colors[i], fontweight='bold')
        ax.axhline(y=BETA, color='#E24B4A', linestyle='--',
                   linewidth=1.3, label=f'β={BETA}')
        ax.set_xticks(range(len(valid)))
        ax.set_xticklabels(labels, rotation=10, ha='right')
        ax.set_ylabel('Final Skill-APR')
        ax.set_title('APR Distribution: PPO (Multi-Obj + Item) vs Baselines')
        ax.legend(fontsize=9)
        ax.set_ylim(0.2, 1.0)
        fig.tight_layout()
        fig.savefig(f'{FIGS_DIR}/fig3_violin.png')
        plt.close(fig)

    print(f"圖表已儲存至 {FIGS_DIR}/")


# ==========================================
# 8. 主程式
# ==========================================

def main():
    print("載入 AKT v2（凍結）...")
    akt_model, inference, ckpt = load_model('./models/akt_best.pth')
    for p in akt_model.parameters():
        p.requires_grad = False
    akt_model.eval()

    n_items       = ckpt['n_items']
    problem_to_id = ckpt['problem_to_id']
    skill_to_id   = ckpt['skill_to_id']
    print(f"n_items={n_items}  N_SKILLS={N_SKILLS}  "
          f"BETA={BETA}  MAX_STEPS={MAX_STEPS}  TIMESTEPS={TIMESTEPS:,}")

    DATA_PATH = '/home/s3102792026/assistments_full.csv'

    train_pool, test_pool = build_student_pool(
        DATA_PATH, problem_to_id, skill_to_id, n_total=500)
    item_to_skill, skill_to_items, item_difficulty = build_item_maps(
        DATA_PATH, problem_to_id, skill_to_id)

    # 共用環境參數
    env_kw_train = dict(
        inference=inference, student_pool=train_pool,
        item_to_skill=item_to_skill, skill_to_items=skill_to_items,
        item_difficulty=item_difficulty, n_items=n_items,
    )
    env_kw_test = {**env_kw_train, 'student_pool': test_pool}

    # ── 基線評估（test_pool）──────────────────────────────
    print("\n基線評估（test_pool）...")
    all_results = {}
    base_env = BestModelEnv(**{**env_kw_test, 'seed': 0})
    all_results['Random']     = evaluate('random',  base_env, seed=0)
    all_results['Greedy-ZPD'] = evaluate('greedy-zpd', base_env, seed=0)

    for name, res in all_results.items():
        stm = res['steps_to_mastery_mean']
        print(f"  {name:<14} APR={res['final_apr_mean']:.4f}  "
              f"SR={res['success_mean']:.3f}  "
              f"Steps(ok)={'N/A' if np.isnan(stm) else f'{stm:.1f}'}  "
              f"DIV={res['div']:.4f}")

    # ── 訓練最佳方案 PPO ─────────────────────────────────
    model, history = train(env_kw_train, seed=0)

    # ── 評估最佳方案（test_pool）─────────────────────────
    print("\n評估 PPO (Multi-Obj + Item-level)（test_pool）...")
    eval_env = BestModelEnv(**{**env_kw_test, 'seed': 999})
    res_ppo  = evaluate(model, eval_env, seed=1000)
    all_results['PPO-Best'] = res_ppo

    stm = res_ppo['steps_to_mastery_mean']
    print(f"\n[最佳方案結果]")
    print(f"  Skill-APR:      {res_ppo['final_apr_mean']:.4f} "
          f"± {res_ppo['final_apr_std']:.4f}")
    print(f"  Success Rate:   {res_ppo['success_mean']:.3f}")
    print(f"  Correct Rate:   {res_ppo['correct_rate_mean']:.3f}")
    print(f"  Steps (ok):     "
          f"{'N/A' if np.isnan(stm) else f'{stm:.1f}'}")
    print(f"  Frustrations:   {res_ppo['n_fails_mean']:.2f}")
    print(f"  Skills Covered: {res_ppo['n_skills_mean']:.2f}")
    print(f"  DIV:            {res_ppo['div']:.4f}")

    # ── 統計顯著性 ────────────────────────────────────────
    print("\n統計顯著性（Mann-Whitney U，PPO vs 基線）：")
    for metric_name, metric_key in [
        ('Skill-APR',    'final_apr'),
        ('Success Rate', 'success'),
        ('Correct Rate', 'correct_rate'),
        ('Frustrations', 'n_fails'),
        ('DIV',          'div'),
    ]:
        for base in ['Random', 'Greedy-ZPD']:
            t = stat_test(all_results['PPO-Best'], all_results[base],
                          metric_key)
            print(f"  {metric_name:<14} vs {base:<12} "
                  f"p={t['p']:.4f} {t['stars']:3s} ({t['dir']})")

    # ── 結果表 ────────────────────────────────────────────
    print("\n" + "─"*75)
    print(f"{'Strategy':<22} {'APR':>7} {'SR':>7} {'Steps(ok)':>10} "
          f"{'Frust':>7} {'Correct':>8} {'DIV':>7}")
    print("─"*75)
    for name in ['Random', 'Greedy-ZPD', 'PPO-Best']:
        r   = all_results[name]
        stm = r['steps_to_mastery_mean']
        print(f"{LABELS[name]:<22} "
              f"{r['final_apr_mean']:>7.4f} "
              f"{r['success_mean']:>7.3f} "
              f"{stm:>10.1f} "
              f"{r['n_fails_mean']:>7.2f} "
              f"{r['correct_rate_mean']:>8.3f} "
              f"{r['div']:>7.4f}")
    print("─"*75)

    # ── 儲存結果 ─────────────────────────────────────────
    pd.DataFrame(history).to_csv(
        f'{RES_DIR}/convergence.csv', index=False)

    summary = []
    for name, res in all_results.items():
        stm = res['steps_to_mastery_mean']
        summary.append({
            'strategy'        : LABELS[name],
            'final_apr'       : round(res['final_apr_mean'], 4),
            'final_apr_std'   : round(res['final_apr_std'],  4),
            'success_rate'    : round(res['success_mean'],   4),
            'correct_rate'    : round(res['correct_rate_mean'], 4),
            'steps_to_mastery': round(stm, 2) if not np.isnan(stm) else None,
            'n_fails'         : round(res['n_fails_mean'],   3),
            'n_skills'        : round(res['n_skills_mean'],  2),
            'div'             : round(res['div'],            4),
        })
        ep_df = pd.DataFrame({
            k.replace('_all', ''): v
            for k, v in res.items() if k.endswith('_all')
        })
        ep_df.to_csv(
            f"{RES_DIR}/episodes_{name.replace('-','_')}.csv",
            index=False)

    pd.DataFrame(summary).to_csv(f'{RES_DIR}/summary.csv', index=False)

    # ── 繪圖 ─────────────────────────────────────────────
    plot_all(all_results, history)

    print(f"\n完成。結果存於 {RES_DIR}/，圖表存於 {FIGS_DIR}/")
    return all_results, history


if __name__ == "__main__":
    results, history = main()