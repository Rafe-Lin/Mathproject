"""
===================================================================
AKT (Attentive Knowledge Tracing) — 修正版 v2
參考: Ghosh et al., KDD 2020 + ALPN paper (arXiv:2305.04475)

【v2 主要變更】
- SKILLS_LIST 從 15 個改為 24 個「甜蜜點」知識點
  選取標準：題目數 7–30 道 + 互動數 ≥ 3000 筆 + 答對率 0.2–0.6
  效果：每個 skill 題目數從平均 75 道降至平均 18 道，
        AKT 的知識遷移效應更集中，每步 APR 提升從 0.001 增加至 0.01–0.03
- 修正 train() 函式的 Early Stopping 結構
- checkpoint 加入 skills_list 欄位供 RL 環境讀取
- ReduceLROnPlateau 取代 CosineAnnealingLR
- weight_decay 提高至 1e-4
===================================================================
"""

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
import os
from sklearn.metrics import roc_auc_score

# ==========================================
# 0. 全域設定
# ==========================================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── 核心修改：換成 24 個甜蜜點知識點 ──────────────────────
# 選取標準：
#   題目數  7–30 道  → 遷移效應集中，每步 APR 變化明顯
#   互動數  ≥ 3000 筆 → 資料夠多，AKT 能學到穩定的作答模式
#   答對率  0.2–0.6  → 題目有區分度，不太難也不太簡單
SKILLS_LIST = [
    "pythagorean-theorem",                       # 18題, 22104筆, 答對率0.242
    "perimeter",                                 # 12題, 11269筆, 答對率0.342
    "supplementary-angles",                      # 20題, 11258筆, 答對率0.265
    "venn-diagram",                              # 12題,  9341筆, 答對率0.303
    "linear-area-volume-conversion",             # 29題,  9137筆, 答對率0.311
    "least-common-multiple",                     # 15題,  8780筆, 答對率0.326
    "sum-of-interior-angles-triangle",           # 30題,  8425筆, 答對率0.362
    "fraction-multiplication",                   # 23題,  7650筆, 答對率0.398
    "fractions",                                 # 21題,  6674筆, 答對率0.314
    "division",                                  # 21題,  6276筆, 答對率0.486
    "number-line",                               # 11題,  6174筆, 答對率0.432
    "percents",                                  # 20題,  6138筆, 答對率0.450
    "fraction-division",                         # 20題,  5687筆, 答對率0.376
    "equation-concept",                          # 21題,  5661筆, 答對率0.409
    "transformations-rotations",                 # 19題,  5385筆, 答對率0.346
    "transversals",                              #  9題,  5292筆, 答對率0.266
    "making-sense-of-expressions-and-equations", # 18題,  4548筆, 答對率0.425
    "p-patterns-relations-algebra",              # 18題,  4130筆, 答對率0.357
    "rate",                                      # 17題,  3920筆, 答對率0.364
    "circle-graph",                              # 21題,  3862筆, 答對率0.415
    "exponents",                                 # 25題,  3614筆, 答對率0.484
    "ordering-numbers",                          # 25題,  3583筆, 答對率0.595
    "isosceles-triangle",                        #  7題,  3580筆, 答對率0.325
    "rate-with-distance-and-time",               # 15題,  3005筆, 答對率0.443
]
N_SKILLS = len(SKILLS_LIST)   # 24

MAX_SEQ_LEN = 50
BATCH_SIZE  = 64
EMBED_DIM   = 128
N_HEADS     = 8
DROPOUT     = 0.2    # 適度提高防止過擬合
EPOCHS      = 30
LR          = 1e-3
PATIENCE    = 5      # Early Stopping patience


# ==========================================
# 1. 資料前處理
# ==========================================
def preprocess_data(file_path: str):
    """
    回傳:
        user_groups   : list of (item_ids, skill_ids, corrects)
        n_items       : 題目總數（預期約 430–500 道）
        n_skills      : 24
        problem_to_id : {problemId -> 0-indexed id}
        skill_to_id   : {skill_name -> 0-indexed id}
    """
    print(f"讀取資料並篩選 {N_SKILLS} 個知識點...")
    df = pd.read_csv(file_path, low_memory=False)

    # 篩選目標 skill
    df = df[df['skill'].isin(SKILLS_LIST)].copy()
    df = df.dropna(subset=['problemId', 'skill', 'correct'])
    df['correct'] = df['correct'].astype(int).clip(0, 1)

    # ID 映射
    skill_to_id     = {s: i for i, s in enumerate(SKILLS_LIST)}
    unique_problems = df['problemId'].unique()
    problem_to_id   = {p: i for i, p in enumerate(unique_problems)}

    df['skill_id'] = df['skill'].map(skill_to_id)
    df['item_id']  = df['problemId'].map(problem_to_id)

    n_items = len(unique_problems)
    print(f"題目總數(|A|): {n_items}  技能數: {N_SKILLS}  樣本數: {len(df):,}")

    # 每個 skill 的題目數統計
    print("\n各知識點題目數:")
    for s in SKILLS_LIST:
        cnt = df[df['skill'] == s]['problemId'].nunique()
        interactions = (df['skill'] == s).sum()
        print(f"  {s:<45}: {cnt:3d} 題  {interactions:6,} 筆")

    # 按學生分組
    user_groups = (
        df.groupby('studentId')
          .apply(lambda x: (
              x['item_id'].values.astype(np.int64),
              x['skill_id'].values.astype(np.int64),
              x['correct'].values.astype(np.int64)
          ))
          .values
    )

    print(f"\n學生總數: {len(user_groups):,}")
    return user_groups, n_items, N_SKILLS, problem_to_id, skill_to_id


# ==========================================
# 2. Dataset
# ==========================================
class AKTDataset(Dataset):
    def __init__(self, groups, max_len: int):
        self.samples = []
        for items, skills, corrects in groups:
            if len(items) < 2:
                continue
            for i in range(0, len(items), max_len):
                chunk_items   = items[i:i + max_len]
                chunk_skills  = skills[i:i + max_len]
                chunk_correct = corrects[i:i + max_len]
                if len(chunk_items) < 2:
                    continue
                self.samples.append({
                    'items'   : chunk_items,
                    'skills'  : chunk_skills,
                    'corrects': chunk_correct,
                })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        return (
            torch.tensor(s['items'],    dtype=torch.long),
            torch.tensor(s['skills'],   dtype=torch.long),
            torch.tensor(s['corrects'], dtype=torch.long),
        )


def collate_fn(batch):
    items, skills, corrects = zip(*batch)
    items_pad    = pad_sequence(items,    batch_first=True, padding_value=0)
    skills_pad   = pad_sequence(skills,   batch_first=True, padding_value=0)
    corrects_pad = pad_sequence(corrects, batch_first=True, padding_value=-1)
    return items_pad, skills_pad, corrects_pad


# ==========================================
# 3. AKT 架構 — 三階段
# ==========================================

class MonotonicAttention(nn.Module):
    """
    論文 AKT 的 Attention 核心。
    Scaled Dot-Product Attention + 因果遮罩。
    支援 cross-attention（Q 與 KV 來自不同序列）。
    """
    def __init__(self, embed_dim: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % n_heads == 0
        self.n_heads = n_heads
        self.d_k     = embed_dim // n_heads
        self.scale   = self.d_k ** -0.5

        self.W_q  = nn.Linear(embed_dim, embed_dim)
        self.W_k  = nn.Linear(embed_dim, embed_dim)
        self.W_v  = nn.Linear(embed_dim, embed_dim)
        self.out  = nn.Linear(embed_dim, embed_dim)
        self.drop = nn.Dropout(dropout)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, query, key, value, causal: bool = True):
        B, T_q, _ = query.shape
        _, T_k, _ = key.shape

        Q = self.W_q(query).view(B, T_q, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(B, T_k, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(B, T_k, self.n_heads, self.d_k).transpose(1, 2)

        attn = torch.matmul(Q, K.transpose(-2, -1)) * self.scale

        if causal:
            mask = torch.triu(
                torch.ones(T_q, T_k, device=query.device, dtype=torch.bool),
                diagonal=1
            )
            attn = attn.masked_fill(mask.unsqueeze(0).unsqueeze(0), float('-inf'))

        attn = self.drop(F.softmax(attn, dim=-1))
        out  = torch.matmul(attn, V)
        out  = out.transpose(1, 2).contiguous().view(B, T_q, -1)
        out  = self.out(out)
        return self.norm(out + query)


class FFN(nn.Module):
    """Position-wise Feed-Forward Network with residual."""
    def __init__(self, embed_dim: int, dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim * 4, embed_dim),
            nn.Dropout(dropout),
        )
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x):
        return self.norm(x + self.net(x))


class AKT(nn.Module):
    """
    Attentive Knowledge Tracing — 完整三階段架構

    階段 1 — Exercise Encoder   : item_emb + skill_emb → causal self-attn
    階段 2 — Knowledge Encoder  : item_emb + skill_emb + resp_emb → causal self-attn
    階段 3 — Knowledge Retriever: cross-attn（Query=exercise, Key/V=knowledge）

    輸出:
        logits_all : (B, T, n_items)  對全部題目的預測 logits
        hidden     : (B, T, D)        供 RL 環境使用的隱藏狀態
    """
    def __init__(self, n_items: int, n_skills: int, embed_dim: int,
                 n_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.n_items   = n_items
        self.embed_dim = embed_dim

        self.item_emb  = nn.Embedding(n_items + 1,      embed_dim, padding_idx=0)
        self.skill_emb = nn.Embedding(n_skills + 1,     embed_dim, padding_idx=0)
        self.resp_emb  = nn.Embedding(2 * n_skills + 1, embed_dim, padding_idx=0)

        self.ex_self_attn = MonotonicAttention(embed_dim, n_heads, dropout)
        self.ex_ffn       = FFN(embed_dim, dropout)

        self.kn_self_attn = MonotonicAttention(embed_dim, n_heads, dropout)
        self.kn_ffn       = FFN(embed_dim, dropout)

        self.retriever = MonotonicAttention(embed_dim, n_heads, dropout)
        self.ret_ffn   = FFN(embed_dim, dropout)

        # 兩層輸出層：防止 output_layer 直接過擬合到特定題目
        self.output_layer = nn.Sequential(
            nn.Linear(embed_dim, embed_dim // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim // 2, n_items),
        )
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    def _make_interaction_idx(self, skill_seq, resp_seq):
        """
        (skill_id, correct) → 單一 interaction index
          correct=1 : skill_1idx + n_skills
          correct=0 : skill_1idx
          padding   : 0
        """
        n_s        = self.skill_emb.num_embeddings - 1
        skill_1idx = skill_seq.clamp(min=0) + 1
        idx        = torch.where(resp_seq == 1, skill_1idx + n_s, skill_1idx)
        idx        = torch.where(resp_seq < 0,  torch.zeros_like(idx), idx)
        return idx

    def forward(self, item_seq, skill_seq, resp_seq):
        """
        item_seq  : (B, T)  1-indexed, 0=padding
        skill_seq : (B, T)  0-indexed
        resp_seq  : (B, T)  0/1, -1=padding

        回傳:
            logits_all : (B, T, n_items)
            hidden     : (B, T, D)
        """
        # 階段 1: Exercise Encoder
        ex_emb = self.item_emb(item_seq) + self.skill_emb(skill_seq + 1)
        ex_ctx = self.ex_self_attn(ex_emb, ex_emb, ex_emb, causal=True)
        ex_ctx = self.ex_ffn(ex_ctx)

        # 階段 2: Knowledge Encoder
        inter_idx = self._make_interaction_idx(skill_seq, resp_seq)
        kn_emb    = (self.item_emb(item_seq)
                     + self.skill_emb(skill_seq + 1)
                     + self.resp_emb(inter_idx))
        kn_ctx    = self.kn_self_attn(kn_emb, kn_emb, kn_emb, causal=True)
        kn_ctx    = self.kn_ffn(kn_ctx)

        # 階段 3: Knowledge Retriever（shift right 確保不洩漏未來資訊）
        B, T, D    = kn_ctx.shape
        kn_shifted = torch.cat([
            torch.zeros(B, 1, D, device=kn_ctx.device),
            kn_ctx[:, :-1, :]
        ], dim=1)

        hidden     = self.retriever(ex_ctx, kn_shifted, kn_shifted, causal=True)
        hidden     = self.ret_ffn(hidden)
        logits_all = self.output_layer(hidden)   # (B, T, n_items)
        return logits_all, hidden


# ==========================================
# 4. 訓練流程
# ==========================================
def train(data_path: str = './assistments_2017.csv'):
    # 4.1 資料準備
    user_groups, n_items, n_skills, problem_to_id, skill_to_id = \
        preprocess_data(data_path)

    # Train / Val 分割 (9:1)
    np.random.seed(42)
    np.random.shuffle(user_groups)
    split        = int(len(user_groups) * 0.9)
    train_groups = user_groups[:split]
    val_groups   = user_groups[split:]

    train_ds = AKTDataset(train_groups, MAX_SEQ_LEN)
    val_ds   = AKTDataset(val_groups,   MAX_SEQ_LEN)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE,
                              shuffle=True,  collate_fn=collate_fn,
                              num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE,
                              shuffle=False, collate_fn=collate_fn,
                              num_workers=0)

    print(f"\nTrain samples: {len(train_ds):,}  Val samples: {len(val_ds):,}")

    # 4.2 模型初始化
    model = AKT(
        n_items   = n_items,
        n_skills  = n_skills,
        embed_dim = EMBED_DIM,
        n_heads   = N_HEADS,
        dropout   = DROPOUT,
    ).to(DEVICE)

    total_params = sum(p.numel() for p in model.parameters()
                       if p.requires_grad)
    print(f"模型參數量: {total_params:,}\n")

    # weight_decay 提高至 1e-4，防止 output_layer 過擬合
    optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)

    # ReduceLROnPlateau：只在 Val AUC 不再改善時才降 LR
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5,
        patience=3, min_lr=1e-5, verbose=True
    )

    # 4.3 訓練迴圈（含 Early Stopping）
    print("開始訓練 AKT (三階段架構，24 個知識點)...")
    best_auc         = 0.0
    no_improve_count = 0
    os.makedirs('./models', exist_ok=True)

    for epoch in range(EPOCHS):

        # ── Training ──────────────────────────────────────
        model.train()
        total_loss       = 0.0
        n_batches        = 0
        all_train_preds  = []
        all_train_labels = []

        for items, skills, labels in train_loader:
            items  = items.to(DEVICE)
            skills = skills.to(DEVICE)
            labels = labels.to(DEVICE)

            # shift right：時間步 t 的 resp_in 是 t-1 的對錯
            resp_in = torch.cat([
                torch.full((labels.size(0), 1), -1,
                           device=DEVICE, dtype=torch.long),
                labels[:, :-1]
            ], dim=1)

            logits_all, _ = model(items, skills, resp_in)

            # 取當前題目對應的 logit
            item_idx = (items - 1).clamp(min=0).unsqueeze(-1)
            logits   = logits_all.gather(-1, item_idx).squeeze(-1)

            mask = (labels != -1)
            loss = F.binary_cross_entropy_with_logits(
                logits[mask], labels[mask].float()
            )

            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            n_batches  += 1

            with torch.no_grad():
                all_train_preds.extend(
                    torch.sigmoid(logits[mask]).cpu().numpy())
                all_train_labels.extend(labels[mask].cpu().numpy())

        avg_loss  = total_loss / n_batches
        train_auc = roc_auc_score(all_train_labels, all_train_preds)

        # ── Validation ────────────────────────────────────
        model.eval()
        all_preds, all_val_labels = [], []

        with torch.no_grad():
            for items, skills, labels in val_loader:
                items  = items.to(DEVICE)
                skills = skills.to(DEVICE)
                labels = labels.to(DEVICE)

                resp_in = torch.cat([
                    torch.full((labels.size(0), 1), -1,
                               device=DEVICE, dtype=torch.long),
                    labels[:, :-1]
                ], dim=1)

                logits_all, _ = model(items, skills, resp_in)
                item_idx      = (items - 1).clamp(min=0).unsqueeze(-1)
                logits        = logits_all.gather(-1, item_idx).squeeze(-1)

                mask = (labels != -1)
                all_preds.extend(
                    torch.sigmoid(logits[mask]).cpu().numpy())
                all_val_labels.extend(labels[mask].cpu().numpy())

        val_auc = roc_auc_score(all_val_labels, all_preds)
        scheduler.step(val_auc)

        print(f"Epoch {epoch+1:2d}/{EPOCHS} | "
              f"Loss: {avg_loss:.4f} | "
              f"Train AUC: {train_auc:.4f} | "
              f"Val AUC: {val_auc:.4f}")

        # Early Stopping + 儲存最佳模型
        if val_auc > best_auc:
            best_auc         = val_auc
            no_improve_count = 0
            torch.save({
                'epoch'         : epoch,
                'model_state'   : model.state_dict(),
                'n_items'       : n_items,
                'n_skills'      : n_skills,
                'problem_to_id' : problem_to_id,
                'skill_to_id'   : skill_to_id,
                'skills_list'   : SKILLS_LIST,   # ← 新增：供 RL 環境讀取
                'embed_dim'     : EMBED_DIM,
                'n_heads'       : N_HEADS,
                'best_auc'      : best_auc,
            }, './models/akt_best.pth')
            print(f"  → 新的最佳 Val AUC: {best_auc:.4f}，已儲存")
        else:
            no_improve_count += 1
            print(f"  → 無提升，patience {no_improve_count}/{PATIENCE}")
            if no_improve_count >= PATIENCE:
                print(f"\nEarly Stopping：連續 {PATIENCE} 個 epoch 無提升，"
                      f"停止訓練。")
                break

    # 載入最佳權重
    ckpt = torch.load('./models/akt_best.pth',
                      map_location=DEVICE, weights_only=False)
    model.load_state_dict(ckpt['model_state'])
    print(f"\n訓練完成。最佳 Val AUC: {best_auc:.4f}（已載入最佳權重）")
    return model, n_items, n_skills, problem_to_id, skill_to_id


# ==========================================
# 5. 推論工具：計算 sₜ 與 APR
# ==========================================
class AKTInference:
    """
    供 RL 環境使用的 AKT 推論包裝器。

    get_knowledge_state() → sₜ (n_items 維，每元素代表答對機率)
    get_apr()             → float（所有題目答對機率的平均值）
    get_skill_apr()       → float（24 個 skill 掌握率的平均值，
                                   對小 n_items 更敏感）
    """
    def __init__(self, model: AKT, n_items: int,
                 skill_to_items: dict = None, device=DEVICE):
        self.model          = model.eval()
        self.n_items        = n_items
        self.skill_to_items = skill_to_items   # 供 get_skill_apr 使用
        self.device         = device

    @torch.no_grad()
    def get_knowledge_state(self, item_history, skill_history,
                             resp_history) -> np.ndarray:
        """回傳 sₜ: shape (n_items,)，值域 (0, 1)"""
        if len(item_history) == 0:
            return np.full(self.n_items, 0.5)

        item_h  = item_history[-MAX_SEQ_LEN:]
        skill_h = skill_history[-MAX_SEQ_LEN:]
        resp_h  = resp_history[-MAX_SEQ_LEN:]
        resp_in = [-1] + resp_h[:-1]

        item_t  = torch.tensor([item_h],  dtype=torch.long).to(self.device)
        skill_t = torch.tensor([skill_h], dtype=torch.long).to(self.device)
        resp_t  = torch.tensor([resp_in], dtype=torch.long).to(self.device)

        logits_all, _ = self.model(item_t, skill_t, resp_t)
        last_logits   = logits_all[0, -1, :]
        return torch.sigmoid(last_logits).cpu().numpy()

    def get_apr(self, item_history, skill_history, resp_history) -> float:
        """Item-level APR：mean(sₜ)，對應論文 Eq.(4)"""
        s_t = self.get_knowledge_state(item_history, skill_history,
                                        resp_history)
        return float(np.mean(s_t))

    def get_skill_apr(self, item_history, skill_history,
                       resp_history) -> float:
        """
        Skill-level APR：24 個 skill 掌握率的平均值。
        每個 skill 的掌握率 = 該 skill 下所有題目的平均 sₜ[j]。
        在 n_items 較小時，每步變化比 item-level APR 更敏感。
        """
        if self.skill_to_items is None:
            return self.get_apr(item_history, skill_history, resp_history)

        s_t        = self.get_knowledge_state(item_history, skill_history,
                                               resp_history)
        skill_aprs = []
        for sid, items in self.skill_to_items.items():
            valid = [j for j in items if j < self.n_items]
            if valid:
                skill_aprs.append(float(np.mean(s_t[valid])))
        return float(np.mean(skill_aprs)) if skill_aprs else 0.5


# ==========================================
# 6. 載入已訓練模型
# ==========================================
def load_model(checkpoint_path: str = './models/akt_best.pth'):
    """
    載入已訓練的 AKT 模型，回傳 (model, AKTInference, metadata)
    metadata 包含 skills_list，供 RL 環境同步使用。
    """
    ckpt  = torch.load(checkpoint_path, map_location=DEVICE,
                        weights_only=False)
    model = AKT(
        n_items   = ckpt['n_items'],
        n_skills  = ckpt['n_skills'],
        embed_dim = ckpt['embed_dim'],
        n_heads   = ckpt['n_heads'],
    ).to(DEVICE)
    model.load_state_dict(ckpt['model_state'])
    model.eval()

    inference = AKTInference(model, n_items=ckpt['n_items'])
    print(f"模型載入成功。"
          f"n_items={ckpt['n_items']}, "
          f"n_skills={ckpt['n_skills']}, "
          f"最佳 AUC={ckpt['best_auc']:.4f}")

    # 向下相容：舊版 checkpoint 沒有 skills_list
    if 'skills_list' not in ckpt:
        ckpt['skills_list'] = SKILLS_LIST

    return model, inference, ckpt


# ==========================================
# 主程式
# ==========================================
if __name__ == "__main__":
    DATA_PATH = '/content/drive/MyDrive/assistments_2017.csv'

    model, n_items, n_skills, p2id, s2id = train(DATA_PATH)

    inference = AKTInference(model, n_items=n_items)

    # 示範推論
    demo_items  = [1, 5, 12]
    demo_skills = [0, 3, 7]
    demo_resps  = [1, 0, 1]

    s_t = inference.get_knowledge_state(demo_items, demo_skills, demo_resps)
    apr = inference.get_apr(demo_items, demo_skills, demo_resps)
    print(f"\n示範學生知識狀態（前 10 題）: {s_t[:10].round(3)}")
    print(f"示範學生 Item-APR: {apr:.4f}")
