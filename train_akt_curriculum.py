"""
═════════════════════════════════════════════════════════════════
AKT (Attentive Knowledge Tracing) 訓練腳本
基於合成訓練數據和題庫進行訓練，目標 AUC > 0.75
═════════════════════════════════════════════════════════════════
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
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt

# ==========================================
# 0. 全域設定
# ==========================================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用設備：{DEVICE}\n")

# 訓練參數
MAX_SEQ_LEN = 50
BATCH_SIZE = 64
EMBED_DIM = 128
N_HEADS = 8
DROPOUT = 0.2
EPOCHS = 50
LR = 1e-3
PATIENCE = 8
WEIGHT_DECAY = 1e-4


# ==========================================
# 1. 資料前處理
# ==========================================
def preprocess_data(csv_path: str = './synthesized_training_data.csv'):
    """
    讀取合成的訓練數據，回傳：
        user_groups   : list of (item_ids, skill_ids, corrects)
        n_items       : 題目總數（約 200+）
        n_skills      : 技能數
        problem_to_id : {problemId -> 0-indexed id}
        skill_to_id   : {skill_name -> 0-indexed id}
        skills_list   : 技能名稱列表
    """
    print(f"讀取訓練數據：{csv_path}...")
    df = pd.read_csv(csv_path)
    
    print(f"資料行數：{len(df):,}")
    print(f"列名：{df.columns.tolist()}\n")

    # 數據驗證
    df = df.dropna(subset=['problemId', 'skill', 'correct'])
    df['correct'] = df['correct'].astype(int).clip(0, 1)

    # 建立ID映射
    unique_skills = sorted(df['skill'].unique())
    unique_problems = sorted(df['problemId'].unique())

    skill_to_id = {s: i for i, s in enumerate(unique_skills)}
    problem_to_id = {p: i for i, p in enumerate(unique_problems)}

    df['skill_id'] = df['skill'].map(skill_to_id)
    df['item_id'] = df['problemId'].map(problem_to_id)

    n_skills = len(unique_skills)
    n_items = len(unique_problems)

    print(f"技能數：{n_skills}")
    print(f"題目數：{n_items}")
    print(f"學生數：{df['studentId'].nunique():,}")
    print(f"互動總數：{len(df):,}\n")

    # 各技能的統計
    print("各技能統計：")
    for skill_id, skill_name in enumerate(unique_skills):
        skill_data = df[df['skill_id'] == skill_id]
        count = len(skill_data)
        acc = skill_data['correct'].mean()
        n_problems = skill_data['problemId'].nunique()
        print(f"  [{skill_id:2d}] {skill_name:<50} "
              f"#{n_problems:3d}題 {count:5,}筆 {acc:.1%}正確率")

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

    print(f"\n每個學生平均作答數：{len(df) / df['studentId'].nunique():.1f} 題")
    return user_groups, n_items, n_skills, problem_to_id, skill_to_id, unique_skills


# ==========================================
# 2. Dataset & DataLoader
# ==========================================
class AKTDataset(Dataset):
    def __init__(self, groups, max_len: int):
        self.samples = []
        for items, skills, corrects in groups:
            if len(items) < 2:
                continue
            # 分段處理長序列
            for i in range(0, len(items), max_len):
                chunk_items = items[i:i + max_len]
                chunk_skills = skills[i:i + max_len]
                chunk_correct = corrects[i:i + max_len]
                if len(chunk_items) < 2:
                    continue
                self.samples.append({
                    'items': chunk_items,
                    'skills': chunk_skills,
                    'corrects': chunk_correct,
                })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        return (
            torch.tensor(s['items'], dtype=torch.long),
            torch.tensor(s['skills'], dtype=torch.long),
            torch.tensor(s['corrects'], dtype=torch.long),
        )


def collate_fn(batch):
    items, skills, corrects = zip(*batch)
    items_pad = pad_sequence(items, batch_first=True, padding_value=0)
    skills_pad = pad_sequence(skills, batch_first=True, padding_value=0)
    corrects_pad = pad_sequence(corrects, batch_first=True, padding_value=-1)
    return items_pad, skills_pad, corrects_pad


# ==========================================
# 3. AKT 架構（三階段）
# ==========================================
class MonotonicAttention(nn.Module):
    """AKT 的 Scaled Dot-Product Attention + 因果遮罩."""
    def __init__(self, embed_dim: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % n_heads == 0
        self.n_heads = n_heads
        self.d_k = embed_dim // n_heads
        self.scale = self.d_k ** -0.5

        self.W_q = nn.Linear(embed_dim, embed_dim)
        self.W_k = nn.Linear(embed_dim, embed_dim)
        self.W_v = nn.Linear(embed_dim, embed_dim)
        self.out = nn.Linear(embed_dim, embed_dim)
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
        out = torch.matmul(attn, V)
        out = out.transpose(1, 2).contiguous().view(B, T_q, -1)
        out = self.out(out)
        return self.norm(out + query)


class FFN(nn.Module):
    """Position-wise Feed-Forward Network."""
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
    Attentive Knowledge Tracing — 三階段架構
    Stage 1: Exercise Encoder   (item + skill → causal self-attn)
    Stage 2: Knowledge Encoder  (item + skill + response → causal self-attn)
    Stage 3: Knowledge Retriever (cross-attn)
    """
    def __init__(self, n_items: int, n_skills: int, embed_dim: int,
                 n_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.n_items = n_items
        self.embed_dim = embed_dim

        self.item_emb = nn.Embedding(n_items + 1, embed_dim, padding_idx=0)
        self.skill_emb = nn.Embedding(n_skills + 1, embed_dim, padding_idx=0)
        self.resp_emb = nn.Embedding(2 * n_skills + 1, embed_dim, padding_idx=0)

        self.ex_self_attn = MonotonicAttention(embed_dim, n_heads, dropout)
        self.ex_ffn = FFN(embed_dim, dropout)

        self.kn_self_attn = MonotonicAttention(embed_dim, n_heads, dropout)
        self.kn_ffn = FFN(embed_dim, dropout)

        self.retriever = MonotonicAttention(embed_dim, n_heads, dropout)
        self.ret_ffn = FFN(embed_dim, dropout)

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
        """(skill_id, correct) → single interaction index"""
        n_s = self.skill_emb.num_embeddings - 1
        skill_1idx = skill_seq.clamp(min=0) + 1
        idx = torch.where(resp_seq == 1, skill_1idx + n_s, skill_1idx)
        idx = torch.where(resp_seq < 0, torch.zeros_like(idx), idx)
        return idx

    def forward(self, item_seq, skill_seq, resp_seq):
        """
        item_seq  : (B, T)  0-indexed, 0=padding
        skill_seq : (B, T)  0-indexed, 0=padding
        resp_seq  : (B, T)  0/1, -1=padding

        Return:
            logits_all : (B, T, n_items)
            hidden     : (B, T, D)
        """
        # Stage 1: Exercise Encoder
        ex_emb = self.item_emb(item_seq) + self.skill_emb(skill_seq + 1)
        ex_ctx = self.ex_self_attn(ex_emb, ex_emb, ex_emb, causal=True)
        ex_ctx = self.ex_ffn(ex_ctx)

        # Stage 2: Knowledge Encoder
        inter_idx = self._make_interaction_idx(skill_seq, resp_seq)
        kn_emb = (self.item_emb(item_seq)
                  + self.skill_emb(skill_seq + 1)
                  + self.resp_emb(inter_idx))
        kn_ctx = self.kn_self_attn(kn_emb, kn_emb, kn_emb, causal=True)
        kn_ctx = self.kn_ffn(kn_ctx)

        # Stage 3: Knowledge Retriever
        B, T, D = kn_ctx.shape
        kn_shifted = torch.cat([
            torch.zeros(B, 1, D, device=kn_ctx.device),
            kn_ctx[:, :-1, :]
        ], dim=1)

        hidden = self.retriever(ex_ctx, kn_shifted, kn_shifted, causal=True)
        hidden = self.ret_ffn(hidden)
        logits_all = self.output_layer(hidden)
        return logits_all, hidden


# ==========================================
# 4. 訓練循環
# ==========================================
def train(data_path: str = './synthesized_training_data.csv'):
    # 準備數據
    user_groups, n_items, n_skills, problem_to_id, skill_to_id, skills_list = \
        preprocess_data(data_path)

    # 訓練 / 驗證分割 (9:1)
    np.random.seed(42)
    np.random.shuffle(user_groups)
    split = int(len(user_groups) * 0.9)
    train_groups = user_groups[:split]
    val_groups = user_groups[split:]

    train_ds = AKTDataset(train_groups, MAX_SEQ_LEN)
    val_ds = AKTDataset(val_groups, MAX_SEQ_LEN)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE,
                              shuffle=True, collate_fn=collate_fn,
                              num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE,
                            shuffle=False, collate_fn=collate_fn,
                            num_workers=0)

    print(f"訓練樣本：{len(train_ds):,}  驗證樣本：{len(val_ds):,}\n")

    # 模型初始化
    model = AKT(
        n_items=n_items,
        n_skills=n_skills,
        embed_dim=EMBED_DIM,
        n_heads=N_HEADS,
        dropout=DROPOUT,
    ).to(DEVICE)

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"模型參數量：{total_params:,}\n")

    # 優化器和調度器
    optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5,
        patience=4, min_lr=1e-5
    )

    # 訓練迴圈
    print("開始訓練 AKT (三階段架構)...\n")
    best_auc = 0.0
    no_improve_count = 0
    os.makedirs('./models', exist_ok=True)
    
    train_losses = []
    train_aucs = []
    val_aucs = []

    for epoch in range(EPOCHS):
        # ------ Training ------
        model.train()
        total_loss = 0.0
        n_batches = 0
        all_train_preds = []
        all_train_labels = []

        for items, skills, labels in train_loader:
            items = items.to(DEVICE)
            skills = skills.to(DEVICE)
            labels = labels.to(DEVICE)

            # Shift right
            resp_in = torch.cat([
                torch.full((labels.size(0), 1), -1, device=DEVICE, dtype=torch.long),
                labels[:, :-1]
            ], dim=1)

            logits_all, _ = model(items, skills, resp_in)

            # 取當前題目的 logit
            item_idx = items.unsqueeze(-1)
            logits = logits_all.gather(-1, item_idx).squeeze(-1)

            mask = (labels != -1)
            loss = F.binary_cross_entropy_with_logits(
                logits[mask], labels[mask].float()
            )

            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            n_batches += 1

            with torch.no_grad():
                all_train_preds.extend(torch.sigmoid(logits[mask]).cpu().numpy())
                all_train_labels.extend(labels[mask].cpu().numpy())

        avg_loss = total_loss / n_batches
        train_auc = roc_auc_score(all_train_labels, all_train_preds)
        train_losses.append(avg_loss)
        train_aucs.append(train_auc)

        # ------ Validation ------
        model.eval()
        all_preds = []
        all_val_labels = []

        with torch.no_grad():
            for items, skills, labels in val_loader:
                items = items.to(DEVICE)
                skills = skills.to(DEVICE)
                labels = labels.to(DEVICE)

                resp_in = torch.cat([
                    torch.full((labels.size(0), 1), -1, device=DEVICE, dtype=torch.long),
                    labels[:, :-1]
                ], dim=1)

                logits_all, _ = model(items, skills, resp_in)
                item_idx = items.unsqueeze(-1)
                logits = logits_all.gather(-1, item_idx).squeeze(-1)

                mask = (labels != -1)
                all_preds.extend(torch.sigmoid(logits[mask]).cpu().numpy())
                all_val_labels.extend(labels[mask].cpu().numpy())

        val_auc = roc_auc_score(all_val_labels, all_preds)
        val_aucs.append(val_auc)
        scheduler.step(val_auc)

        print(f"Epoch {epoch+1:2d}/{EPOCHS} | "
              f"Loss: {avg_loss:.4f} | "
              f"Train AUC: {train_auc:.4f} | "
              f"Val AUC: {val_auc:.4f}")

        # Early Stopping + 儲存最佳模型
        if val_auc > best_auc:
            best_auc = val_auc
            no_improve_count = 0
            torch.save({
                'epoch': epoch,
                'model_state': model.state_dict(),
                'n_items': n_items,
                'n_skills': n_skills,
                'problem_to_id': problem_to_id,
                'skill_to_id': skill_to_id,
                'skills_list': skills_list,
                'embed_dim': EMBED_DIM,
                'n_heads': N_HEADS,
                'best_auc': best_auc,
            }, './models/akt_curriculum.pth')
            print(f"  → 新的最佳 Val AUC: {best_auc:.4f}，已儲存")
        else:
            no_improve_count += 1
            if no_improve_count >= PATIENCE:
                print(f"\nEarly Stopping：連續 {PATIENCE} 個 epoch 無提升。")
                break

    # 載入最佳權重
    ckpt = torch.load('./models/akt_curriculum.pth',
                      map_location=DEVICE, weights_only=False)
    model.load_state_dict(ckpt['model_state'])
    print(f"\n訓練完成。最佳 Val AUC: {best_auc:.4f}")

    # 繪製訓練曲線
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Train Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('訓練損失')
    plt.grid()
    
    plt.subplot(1, 2, 2)
    plt.plot(train_aucs, label='Train AUC', marker='o')
    plt.plot(val_aucs, label='Val AUC', marker='s')
    plt.axhline(y=0.75, color='r', linestyle='--', label='Target (0.75)')
    plt.xlabel('Epoch')
    plt.ylabel('AUC')
    plt.legend()
    plt.title('AKT ROC-AUC 曲線')
    plt.grid()
    plt.tight_layout()
    plt.savefig('./training_curves.png', dpi=100)
    print("訓練曲線已儲存到 ./training_curves.png")

    return model, n_items, n_skills, problem_to_id, skill_to_id, skills_list


# ==========================================
# 主程式
# ==========================================
if __name__ == "__main__":
    model, n_items, n_skills, p2id, s2id, skills_list = train()
    print(f"\n✓ 模型已訓練完成並儲存到 ./models/akt_curriculum.pth")
