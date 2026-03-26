# -*- coding: utf-8 -*-
from __future__ import annotations

import pickle
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .ppo_adapter import SKILL_LABELS, SKILL_TO_IDX


STATE_DIM = 8
ACTION_DIM = len(SKILL_LABELS)


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass
class StudentSimulator:
    mastery_by_skill: dict[str, float]
    frustration_index: float = 0.0
    fail_streak: float = 0.0
    same_skill_streak: float = 0.0
    last_is_correct: float = 1.0
    last_skill_idx: int = -1

    @classmethod
    def random(cls, rng: random.Random) -> "StudentSimulator":
        mastery = {skill: _clip01(rng.uniform(0.25, 0.75)) for skill in SKILL_LABELS}
        return cls(mastery_by_skill=mastery)

    def build_state_vector(self) -> list[float]:
        return [
            float(self.mastery_by_skill.get("integer_arithmetic", 0.45)),
            float(self.mastery_by_skill.get("fraction_arithmetic", 0.45)),
            float(self.mastery_by_skill.get("radical_arithmetic", 0.45)),
            float(self.mastery_by_skill.get("polynomial_arithmetic", 0.45)),
            float(self.frustration_index),
            float(self.fail_streak),
            float(self.same_skill_streak),
            float(self.last_is_correct),
        ]

    def step(self, action_idx: int, rng: random.Random) -> tuple[bool, float]:
        skill = SKILL_LABELS[action_idx]
        old_mastery = float(self.mastery_by_skill.get(skill, 0.45))
        success_prob = _clip01(0.15 + 0.75 * old_mastery - 0.12 * self.frustration_index)
        is_correct = rng.random() < success_prob

        if is_correct:
            mastery_delta = rng.uniform(0.02, 0.06)
            self.mastery_by_skill[skill] = _clip01(old_mastery + mastery_delta)
            self.frustration_index = max(0.0, self.frustration_index - 0.5)
            self.fail_streak = 0.0
            self.last_is_correct = 1.0
        else:
            mastery_delta = -rng.uniform(0.005, 0.02)
            self.mastery_by_skill[skill] = _clip01(old_mastery + mastery_delta)
            self.frustration_index = min(3.0, self.frustration_index + 1.0)
            self.fail_streak = min(5.0, self.fail_streak + 1.0)
            self.last_is_correct = 0.0

        if self.last_skill_idx == action_idx:
            self.same_skill_streak = min(5.0, self.same_skill_streak + 1.0)
        else:
            self.same_skill_streak = 1.0
            self.last_skill_idx = action_idx

        mastery_improvement = self.mastery_by_skill[skill] - old_mastery
        reward = (
            3.0 * mastery_improvement
            - 0.20 * self.frustration_index
            - 0.08 * max(0.0, self.same_skill_streak - 1.0)
        )
        return is_correct, float(reward)


class AdaptiveSkillPolicyEnv:
    """
    Minimal gym-like env:
    - reset() -> state_vector(list[float], len=8)
    - step(action_idx) -> (next_state, reward, done, info)
    """

    def __init__(self, max_steps: int = 15, seed: int = 42):
        self.max_steps = int(max_steps)
        self.rng = random.Random(seed)
        self.student: StudentSimulator | None = None
        self.current_step = 0

    def reset(self) -> list[float]:
        self.current_step = 0
        self.student = StudentSimulator.random(self.rng)
        return self.student.build_state_vector()

    def step(self, action_idx: int) -> tuple[list[float], float, bool, dict[str, Any]]:
        if self.student is None:
            raise RuntimeError("Environment not initialized; call reset() first.")
        if not (0 <= int(action_idx) < ACTION_DIM):
            raise ValueError(f"action_idx must be in [0, {ACTION_DIM - 1}]")

        self.current_step += 1
        is_correct, reward = self.student.step(int(action_idx), self.rng)
        next_state = self.student.build_state_vector()
        done = self.current_step >= self.max_steps
        info = {"is_correct": is_correct, "step": self.current_step}
        return next_state, float(reward), bool(done), info


def teacher_policy_action(state_vector: list[float]) -> int:
    mastery = state_vector[:4]
    same_skill_streak = state_vector[6]
    fail_streak = state_vector[5]
    weakest_idx = min(range(4), key=lambda idx: mastery[idx])
    if same_skill_streak >= 3 and fail_streak >= 2:
        return (weakest_idx + 1) % 4
    return weakest_idx


def generate_imitation_dataset(
    num_episodes: int = 300,
    horizon: int = 12,
    seed: int = 42,
) -> list[dict[str, Any]]:
    env = AdaptiveSkillPolicyEnv(max_steps=horizon, seed=seed)
    rows: list[dict[str, Any]] = []
    for _ in range(int(num_episodes)):
        state = env.reset()
        done = False
        while not done:
            action_idx = teacher_policy_action(state)
            next_state, reward, done, info = env.step(action_idx)
            rows.append(
                {
                    "state": list(state),
                    "action_idx": int(action_idx),
                    "action_label": SKILL_LABELS[action_idx],
                    "reward": float(reward),
                    "next_state": list(next_state),
                    "done": bool(done),
                    "is_correct": bool(info.get("is_correct", False)),
                }
            )
            state = next_state
    return rows


class SkillPolicyNet:
    """
    Minimal NumPy MLP policy:
    input(8) -> hidden(32) -> logits(4)
    """

    def __init__(self, state_dim: int = STATE_DIM, action_dim: int = ACTION_DIM, hidden_dim: int = 32, seed: int = 42):
        rng = np.random.default_rng(seed)
        self.W1 = (rng.standard_normal((state_dim, hidden_dim)) * 0.10).astype(np.float32)
        self.b1 = np.zeros((hidden_dim,), dtype=np.float32)
        self.W2 = (rng.standard_normal((hidden_dim, action_dim)) * 0.10).astype(np.float32)
        self.b2 = np.zeros((action_dim,), dtype=np.float32)
        self.skill_labels = list(SKILL_LABELS)
        self.skill_to_idx = dict(SKILL_TO_IDX)
        self.state_dim = int(state_dim)
        self.action_dim = int(action_dim)
        self.hidden_dim = int(hidden_dim)
        self.metadata: dict[str, Any] = {}

    def _forward(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        h_pre = x @ self.W1 + self.b1
        h = np.maximum(h_pre, 0.0)
        logits = h @ self.W2 + self.b2
        return h, logits

    def predict_logits(self, state_vector: list[float]) -> list[float]:
        x = np.asarray(state_vector, dtype=np.float32).reshape(1, -1)
        _, logits = self._forward(x)
        return logits[0].astype(float).tolist()


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits, axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.sum(exp, axis=1, keepdims=True)


def train_policy_from_imitation(
    dataset: list[dict[str, Any]],
    epochs: int = 25,
    batch_size: int = 64,
    lr: float = 1e-2,
    seed: int = 42,
) -> tuple[SkillPolicyNet, dict[str, float]]:
    model = SkillPolicyNet(seed=seed)
    X = np.asarray([row["state"] for row in dataset], dtype=np.float32)
    y = np.asarray([row["action_idx"] for row in dataset], dtype=np.int64)

    rng = np.random.default_rng(seed)
    n = X.shape[0]
    for _ in range(int(epochs)):
        indices = rng.permutation(n)
        for start in range(0, n, int(batch_size)):
            batch_idx = indices[start : start + int(batch_size)]
            xb = X[batch_idx]
            yb = y[batch_idx]

            h, logits = model._forward(xb)
            probs = _softmax(logits)

            grad_logits = probs
            grad_logits[np.arange(len(yb)), yb] -= 1.0
            grad_logits /= max(1, len(yb))

            grad_W2 = h.T @ grad_logits
            grad_b2 = np.sum(grad_logits, axis=0)

            grad_h = grad_logits @ model.W2.T
            grad_h[h <= 0.0] = 0.0
            grad_W1 = xb.T @ grad_h
            grad_b1 = np.sum(grad_h, axis=0)

            model.W2 -= lr * grad_W2
            model.b2 -= lr * grad_b2
            model.W1 -= lr * grad_W1
            model.b1 -= lr * grad_b1

    _, logits_full = model._forward(X)
    preds = np.argmax(logits_full, axis=1)
    accuracy = float(np.mean(preds == y))

    metrics = {"imitation_accuracy": accuracy, "dataset_size": float(len(dataset))}
    return model, metrics


def save_policy_checkpoint(
    model: SkillPolicyNet,
    checkpoint_path: str | Path,
    metadata: dict[str, Any] | None = None,
) -> Path:
    output_path = Path(checkpoint_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.metadata = dict(metadata or {})
    with open(output_path, "wb") as fp:
        pickle.dump(model, fp)
    return output_path
