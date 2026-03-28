# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import os
import pickle
import traceback
from pathlib import Path
from typing import Any, Iterable

from .agent_skill_schema import AGENT_SKILLS, resolve_agent_skill
from .schema import CatalogEntry, validate_ppo_strategy


LOGGER = logging.getLogger("adaptive_phase2_policy")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PHASE2_MODEL_PATH = PROJECT_ROOT / "models" / "adaptive" / "phase2_policy.pt"
MODEL_PATH_ENV_VARS = ("ADAPTIVE_PPO_MODEL_PATH", "PPO_MODEL_PATH")
CONFIG_MODEL_PATH_KEYS = ("ADAPTIVE_PPO_MODEL_PATH", "PHASE2_POLICY_MODEL_PATH", "PPO_MODEL_PATH")

# Single source of truth for skill label ordering across training/inference.
SKILL_LABELS = list(AGENT_SKILLS)
SKILL_TO_IDX = {label: i for i, label in enumerate(SKILL_LABELS)}
IDX_TO_SKILL = {i: label for i, label in enumerate(SKILL_LABELS)}
EXPECTED_STATE_VECTOR_LEN = 8
ROUTE_ACTIONS = ["stay", "remediate", "return"]
ROUTE_TO_IDX = {label: i for i, label in enumerate(ROUTE_ACTIONS)}
IDX_TO_ROUTE = {i: label for i, label in enumerate(ROUTE_ACTIONS)}
MODE_MAINLINE = "mainline"
MODE_REMEDIATION = "remediation"

_PHASE2_POLICY_MODEL: Any = None
_PHASE2_POLICY_MODEL_PATH: str | None = None
_PHASE2_POLICY_MODEL_LOAD_FAILED = False
_LAST_PPO_ERROR: dict[str, Any] = {
    "type": None,
    "message": None,
    "traceback": None,
    "context": {},
}
_LAST_ROUTE_POLICY_DEBUG: dict[str, Any] = {
    "raw_logits": None,
    "biased_logits": None,
    "masked_logits": None,
    "raw_action": None,
    "raw_action_idx": None,
    "final_action": None,
    "final_action_idx": None,
    "remediate_bias_applied": False,
    "remediate_bias_value": 0.0,
    "bias_reason": "",
}


def choose_strategy(current_apr: float, frustration_index: int, step_number: int) -> int:
    """
    v1.1 PoC PPO stub.
    Strategy codes are fixed to the paper-aligned mapping:
    0 = Max-Fisher
    1 = ZPD
    2 = Diversity
    3 = Review
    """
    if frustration_index >= 2:
        return 3
    if current_apr < 0.45:
        return 1
    if step_number > 0 and step_number % 4 == 0:
        return 2
    return 0


def choose_next_family(
    entries: list[CatalogEntry],
    visited_family_ids: Iterable[str] | None,
    strategy: int,
    last_family_id: str | None = None,
) -> CatalogEntry:
    """
    Choose the next family with deterministic behavior for M2 API testing.
    """
    validate_ppo_strategy(strategy)
    if not entries:
        raise ValueError("entries cannot be empty")

    visited = {item.strip() for item in (visited_family_ids or []) if str(item).strip()}
    ordered = sorted(entries, key=lambda entry: (entry.skill_id, entry.family_id))

    if strategy == 3 and last_family_id:
        for entry in ordered:
            if entry.family_id == last_family_id:
                return entry

    unvisited = [entry for entry in ordered if entry.family_id not in visited]
    if strategy == 2 and unvisited:
        return unvisited[-1]
    if unvisited:
        return unvisited[0]

    if last_family_id:
        for idx, entry in enumerate(ordered):
            if entry.family_id == last_family_id:
                return ordered[(idx + 1) % len(ordered)]

    return ordered[0]


def _warn(msg: str) -> None:
    print(msg, flush=True)
    LOGGER.warning(msg)


def _info(msg: str) -> None:
    print(msg, flush=True)
    LOGGER.info(msg)


def _set_last_ppo_error(
    *,
    error_type: str | None,
    error_message: str | None,
    tb: str | None,
    context: dict[str, Any] | None = None,
) -> None:
    global _LAST_PPO_ERROR
    _LAST_PPO_ERROR = {
        "type": error_type,
        "message": error_message,
        "traceback": tb,
        "context": dict(context or {}),
    }


def get_last_ppo_error() -> dict[str, Any]:
    return dict(_LAST_PPO_ERROR)


def get_last_route_policy_debug() -> dict[str, Any]:
    return dict(_LAST_ROUTE_POLICY_DEBUG)


def _clear_last_ppo_error() -> None:
    _set_last_ppo_error(error_type=None, error_message=None, tb=None, context={})


def _set_last_route_policy_debug(values: dict[str, Any] | None = None) -> None:
    global _LAST_ROUTE_POLICY_DEBUG
    defaults = {
        "raw_logits": None,
        "biased_logits": None,
        "masked_logits": None,
        "raw_action": None,
        "raw_action_idx": None,
        "final_action": None,
        "final_action_idx": None,
        "remediate_bias_applied": False,
        "remediate_bias_value": 0.0,
        "bias_reason": "",
    }
    if values:
        defaults.update(values)
    _LAST_ROUTE_POLICY_DEBUG = defaults


def _summarize_output(value: Any, max_len: int = 240) -> str:
    try:
        text = repr(value)
    except Exception:
        text = f"<unreprable:{type(value).__name__}>"
    if len(text) > max_len:
        return text[:max_len] + "...(truncated)"
    return text


def _resolve_model_path(model_path: str | None = None) -> tuple[Path, str, str]:
    source = "default"
    raw = model_path
    if not raw:
        for env_name in MODEL_PATH_ENV_VARS:
            env_val = str(os.getenv(env_name, "") or "").strip()
            if env_val:
                raw = env_val
                source = f"env:{env_name}"
                break
    if not raw:
        try:
            from core import adaptive_config as cfg  # type: ignore

            for key in CONFIG_MODEL_PATH_KEYS:
                cfg_val = str(getattr(cfg, key, "") or "").strip()
                if cfg_val:
                    raw = cfg_val
                    source = f"config:{key}"
                    break
        except Exception:
            pass
    if not raw:
        raw = str(DEFAULT_PHASE2_MODEL_PATH)
        source = "default"

    candidate = Path(raw).expanduser()
    if candidate.is_absolute():
        return candidate, source, raw

    cwd_candidate = (Path.cwd() / candidate).resolve()
    project_candidate = (PROJECT_ROOT / candidate).resolve()
    if cwd_candidate.exists():
        return cwd_candidate, source, raw
    if project_candidate.exists():
        return project_candidate, source, raw
    return cwd_candidate, source, raw


def load_phase2_policy_model(model_path: str | None = None) -> Any:
    """
    Lazy-load PPO policy model. Returns model object or None.
    Never raises to caller.
    """
    global _PHASE2_POLICY_MODEL, _PHASE2_POLICY_MODEL_PATH, _PHASE2_POLICY_MODEL_LOAD_FAILED

    candidate, source, raw = _resolve_model_path(model_path)
    resolved = str(candidate)
    _info(
        "[adaptive_phase2_policy] load request "
        f"resolved_model_path={resolved} model_path_source={source} raw_model_path={raw} cwd={Path.cwd()}"
    )
    if _PHASE2_POLICY_MODEL is not None and _PHASE2_POLICY_MODEL_PATH == resolved:
        _info("[adaptive_phase2_policy] model cache hit loaded=True")
        _clear_last_ppo_error()
        return _PHASE2_POLICY_MODEL
    if _PHASE2_POLICY_MODEL_LOAD_FAILED and _PHASE2_POLICY_MODEL_PATH == resolved:
        _warn("[adaptive_phase2_policy] model cache hit load_failed=True; rechecking filesystem before retry")

    _PHASE2_POLICY_MODEL_PATH = resolved
    exists = candidate.exists()
    file_size = candidate.stat().st_size if exists and candidate.is_file() else None
    _info(f"[adaptive_phase2_policy] load path check path_exists={exists} file_size={file_size}")
    if not exists:
        _warn(f"[adaptive_phase2_policy][ERROR] model file not found: {candidate}")
        _warn("[adaptive_phase2_policy] no checkpoint found; fallback to heuristic")
        _PHASE2_POLICY_MODEL_LOAD_FAILED = True
        _set_last_ppo_error(
            error_type="FileNotFoundError",
            error_message=f"no checkpoint found: {candidate}",
            tb=None,
            context={
                "model_path": str(candidate),
                "model_path_source": source,
                "cwd": str(Path.cwd()),
                "path_exists": exists,
                "file_size": file_size,
            },
        )
        _info("[adaptive_phase2_policy] model_loaded=False")
        return None

    try:
        model: Any = None
        used_strategy: str | None = None
        last_exc: Exception | None = None
        last_tb: str | None = None

        for strategy in ("torch.jit.load", "torch.load", "joblib.load", "pickle.load"):
            _info(f"[adaptive_phase2_policy] load_strategy={strategy}")
            try:
                if strategy == "torch.jit.load":
                    import torch  # type: ignore

                    model = torch.jit.load(str(candidate), map_location="cpu")
                    if hasattr(model, "eval"):
                        model.eval()
                elif strategy == "torch.load":
                    import torch  # type: ignore

                    model = torch.load(str(candidate), map_location="cpu")
                    if hasattr(model, "eval"):
                        model.eval()
                elif strategy == "joblib.load":
                    import joblib  # type: ignore

                    model = joblib.load(str(candidate))
                elif strategy == "pickle.load":
                    with open(candidate, "rb") as fp:
                        model = pickle.load(fp)
                else:
                    continue
                used_strategy = strategy
                break
            except Exception as exc:
                last_exc = exc
                last_tb = traceback.format_exc()
                _warn(
                    "[adaptive_phase2_policy] load strategy failed "
                    f"strategy={strategy} exception_type={type(exc).__name__} "
                    f"exception_message={exc} traceback={last_tb}"
                )

        if model is None:
            _PHASE2_POLICY_MODEL_LOAD_FAILED = True
            _PHASE2_POLICY_MODEL = None
            _warn("[adaptive_phase2_policy][ERROR] model load failed for all strategies")
            _warn("[adaptive_phase2_policy] no checkpoint found or format mismatch; fallback to heuristic")
            _set_last_ppo_error(
                error_type=(type(last_exc).__name__ if last_exc else "RuntimeError"),
                error_message=(str(last_exc) if last_exc else "model_unavailable_after_load"),
                tb=last_tb,
                context={
                    "model_path": str(candidate),
                    "model_path_source": source,
                    "cwd": str(Path.cwd()),
                    "path_exists": exists,
                    "file_size": file_size,
                },
            )
            _info("[adaptive_phase2_policy] model_loaded=False")
            return None

        if model is None:
            _warn("[adaptive_phase2_policy][ERROR] loaded object is None")
            _set_last_ppo_error(
                error_type="RuntimeError",
                error_message="loaded_object_none",
                tb=None,
                context={"model_path": str(candidate), "strategy": used_strategy},
            )
            _info("[adaptive_phase2_policy] model_loaded=False")
            return None

        _PHASE2_POLICY_MODEL = model
        _PHASE2_POLICY_MODEL_LOAD_FAILED = False
        _info(
            "[adaptive_phase2_policy] PPO model loaded "
            f"strategy={used_strategy} object_type={type(model).__name__} "
            f"object_summary={_summarize_output(model)}"
        )
        _clear_last_ppo_error()
        _info("[adaptive_phase2_policy] model_loaded=True")
        return _PHASE2_POLICY_MODEL
    except Exception as exc:
        tb = traceback.format_exc()
        _warn(
            "[adaptive_phase2_policy] PPO model load failed "
            f"type={type(exc).__name__} message={exc} traceback={tb}"
        )
        _PHASE2_POLICY_MODEL_LOAD_FAILED = True
        _PHASE2_POLICY_MODEL = None
        _set_last_ppo_error(
            error_type=type(exc).__name__,
            error_message=str(exc),
            tb=tb,
            context={
                "model_path": str(candidate),
                "model_path_source": source,
                "cwd": str(Path.cwd()),
                "path_exists": exists,
                "file_size": file_size,
            },
        )
        _info("[adaptive_phase2_policy] model_loaded=False")
        return None


def _to_float_list(values: Any) -> list[float] | None:
    if values is None:
        return None
    try:
        if hasattr(values, "detach"):
            values = values.detach()
        if hasattr(values, "cpu"):
            values = values.cpu()
        if hasattr(values, "numpy"):
            values = values.numpy()
        if isinstance(values, list):
            if values and isinstance(values[0], list):
                values = values[0]
            return [float(x) for x in values]
        if hasattr(values, "tolist"):
            out = values.tolist()
            if out and isinstance(out[0], list):
                out = out[0]
            return [float(x) for x in out]
    except Exception:
        return None
    return None


def _run_model_get_logits(model: Any, state_vector: list[float]) -> list[float] | None:
    if model is None:
        return None
    try:
        if hasattr(model, "predict_logits"):
            raw = model.predict_logits(state_vector)
            logits = _to_float_list(raw)
            if logits is None:
                _warn(
                    "[adaptive_phase2_policy] model output not logits-compatible "
                    f"output_type={type(raw).__name__} output_summary={_summarize_output(raw)}"
                )
            return logits
        if hasattr(model, "predict"):
            predicted = model.predict([state_vector])
            logits = _to_float_list(predicted)
            if logits is not None:
                return logits
            _warn(
                "[adaptive_phase2_policy] model.predict output not logits-compatible "
                f"output_type={type(predicted).__name__} output_summary={_summarize_output(predicted)}"
            )
        if callable(model):
            out = model(state_vector)
            logits = _to_float_list(out)
            if logits is not None:
                return logits
            _warn(
                "[adaptive_phase2_policy] callable model output not logits-compatible "
                f"output_type={type(out).__name__} output_summary={_summarize_output(out)}"
            )
        try:
            import torch  # type: ignore

            with torch.no_grad():
                inp = torch.tensor([state_vector], dtype=torch.float32)
                out = model(inp)
            logits = _to_float_list(out)
            if logits is None:
                _warn(
                    "[adaptive_phase2_policy] torch forward output not logits-compatible "
                    f"output_type={type(out).__name__} output_summary={_summarize_output(out)}"
                )
            return logits
        except Exception as exc:
            tb = traceback.format_exc()
            _warn(
                "[adaptive_phase2_policy] torch forward inference failed "
                f"type={type(exc).__name__} message={exc} traceback={tb}"
            )
            return None
    except Exception as exc:
        tb = traceback.format_exc()
        _warn(
            "[adaptive_phase2_policy] model inference failed "
            f"type={type(exc).__name__} message={exc} traceback={tb}"
        )
        return None


def _normalize_allowed_agent_skills(allowed_agent_skills: list[str] | None) -> list[str]:
    allowed = [str(x).strip() for x in (allowed_agent_skills or []) if str(x).strip()]
    if not allowed:
        _warn("[adaptive_phase2_policy] allowed_agent_skills is empty; fallback to full SKILL_LABELS")
        return list(SKILL_LABELS)
    return allowed


def select_agent_skill_with_ppo(
    agent_state: dict[str, Any],
    allowed_agent_skills: list[str] | None,
    model: Any = None,
) -> tuple[str | None, list[float] | None, int | None, str]:
    """
    returns:
      selected_agent_skill: str | None
      policy_logits: list[float] | None
      action_idx: int | None
      decision_source: str
    """
    allowed = _normalize_allowed_agent_skills(allowed_agent_skills)
    _clear_last_ppo_error()
    try:
        state_vector = [float(x) for x in (agent_state.get("state_vector") or [])]
    except Exception as exc:
        tb = traceback.format_exc()
        _set_last_ppo_error(
            error_type=type(exc).__name__,
            error_message=str(exc),
            tb=tb,
            context={"state_vector_raw": agent_state.get("state_vector")},
        )
        _warn(
            "[adaptive_phase2_policy] state_vector parse failed "
            f"type={type(exc).__name__} message={exc} traceback={tb}"
        )
        return None, None, None, "ppo_error"
    _info(
        "[adaptive_phase2_policy] inference context "
        f"model_path={_PHASE2_POLICY_MODEL_PATH or str(DEFAULT_PHASE2_MODEL_PATH)} "
        f"state_vector={state_vector} "
        f"state_dim={len(state_vector)} "
        f"state_types={[type(x).__name__ for x in state_vector]} "
        f"allowed_agent_skills={allowed} "
        f"SKILL_LABELS={SKILL_LABELS} "
        f"SKILL_TO_IDX={SKILL_TO_IDX} "
        f"IDX_TO_SKILL={IDX_TO_SKILL}"
    )
    if not state_vector:
        _set_last_ppo_error(
            error_type="ValueError",
            error_message="empty state_vector",
            tb=None,
            context={"state_vector": state_vector},
        )
        return None, None, None, "ppo_error"
    if len(state_vector) != EXPECTED_STATE_VECTOR_LEN:
        _warn(
            "[adaptive_phase2_policy][ERROR] invalid_state_vector_length "
            f"expected_state_dim={EXPECTED_STATE_VECTOR_LEN} actual_state_dim={len(state_vector)} "
            f"state_vector={state_vector}"
        )
        _set_last_ppo_error(
            error_type="ValueError",
            error_message="invalid_state_vector_length",
            tb=None,
            context={
                "expected_state_dim": EXPECTED_STATE_VECTOR_LEN,
                "actual_state_dim": len(state_vector),
                "state_vector": state_vector,
            },
        )
        return None, None, None, "ppo_error"

    if model is None:
        model = load_phase2_policy_model()
    _info(f"[adaptive_phase2_policy] model_loaded={model is not None}")
    if model is None:
        last = get_last_ppo_error()
        if not last.get("type"):
            _set_last_ppo_error(
                error_type="RuntimeError",
                error_message="model_unavailable_after_load",
                tb=None,
                context={"model_path": _PHASE2_POLICY_MODEL_PATH or str(DEFAULT_PHASE2_MODEL_PATH)},
            )
        return None, None, None, "ppo_error"

    raw_logits = _run_model_get_logits(model, state_vector)
    if not raw_logits or len(raw_logits) < len(SKILL_LABELS):
        _warn(
            "[adaptive_phase2_policy] PPO inference failed: invalid logits "
            f"logits={_summarize_output(raw_logits)}"
        )
        _set_last_ppo_error(
            error_type="ValueError",
            error_message="invalid_logits",
            tb=None,
            context={
                "logits_type": type(raw_logits).__name__,
                "logits_summary": _summarize_output(raw_logits),
                "required_dim": len(SKILL_LABELS),
            },
        )
        return None, None, None, "ppo_error"

    raw_logits = [float(raw_logits[SKILL_TO_IDX[label]]) for label in SKILL_LABELS]
    masked_logits = []
    for idx in range(len(SKILL_LABELS)):
        skill = IDX_TO_SKILL[idx]
        if skill in allowed:
            masked_logits.append(raw_logits[idx])
        else:
            masked_logits.append(float("-1e18"))

    if not any(skill in allowed for skill in SKILL_LABELS):
        _warn(
            "[adaptive_phase2_policy][WARNING] no legal action after mask "
            f"allowed_agent_skills={allowed}"
        )
        _set_last_ppo_error(
            error_type="ValueError",
            error_message="no_legal_action_after_mask",
            tb=None,
            context={"allowed_agent_skills": allowed},
        )
        return None, raw_logits, None, "ppo_error"

    action_idx = max(range(len(masked_logits)), key=lambda i: masked_logits[i])
    if action_idx not in IDX_TO_SKILL:
        _warn(f"[adaptive_phase2_policy][ERROR] action_idx out of range: {action_idx}")
        _set_last_ppo_error(
            error_type="IndexError",
            error_message=f"invalid_action_idx:{action_idx}",
            tb=None,
            context={"action_idx": action_idx, "idx_to_skill": IDX_TO_SKILL},
        )
        return None, raw_logits, action_idx, "ppo_error"
    selected = IDX_TO_SKILL[action_idx]

    _info(
        f"[adaptive_phase2_policy] inference raw_policy_logits={raw_logits} "
        f"masked_policy_logits={masked_logits} action_idx={action_idx} "
        f"selected_agent_skill={selected} allowed_agent_skills={allowed}"
    )
    if selected not in allowed:
        _warn(
            f"[adaptive_phase2_policy][ERROR] selected_agent_skill not allowed: "
            f"selected={selected} allowed={allowed}"
        )
        _set_last_ppo_error(
            error_type="ValueError",
            error_message="selected_skill_not_allowed",
            tb=None,
            context={"selected": selected, "allowed": allowed},
        )
        return None, raw_logits, action_idx, "ppo_error"

    _clear_last_ppo_error()
    return selected, raw_logits, action_idx, "ppo"


def _route_vector(route_state: dict[str, Any]) -> list[float]:
    affect = dict(route_state.get("affect") or {})
    diag = dict(route_state.get("diagnostic_signal") or {})
    ctx = dict(route_state.get("routing_context") or {})
    return [
        float(affect.get("frustration", 0.0)),
        min(1.0, float(affect.get("fail_streak", 0.0)) / 5.0),
        min(1.0, float(affect.get("same_skill_streak", 0.0)) / 8.0),
        float(diag.get("diagnosis_confidence", 0.0)),
        float(diag.get("retrieval_confidence", 0.0)),
        float(diag.get("rescue_recommended", 0.0)),
        float(ctx.get("in_remediation", 0.0)),
        min(1.0, float(ctx.get("remediation_step_count", 0.0)) / 4.0),
    ]


def _mask_route_logits(raw_logits: list[float], action_mask: dict[str, bool]) -> list[float]:
    masked: list[float] = []
    for action in ROUTE_ACTIONS:
        idx = ROUTE_TO_IDX[action]
        if action_mask.get(action, False):
            masked.append(float(raw_logits[idx]))
        else:
            masked.append(float("-1e18"))
    return masked


def _compute_remediate_bias(route_state: dict[str, Any], action_mask: dict[str, bool]) -> tuple[bool, float, str]:
    if not bool(action_mask.get("remediate", False)):
        return False, 0.0, "remediate_not_allowed"
    diag = dict(route_state.get("diagnostic_signal") or {})
    ctx = dict(route_state.get("routing_context") or {})
    affect = dict(route_state.get("affect") or {})
    current_mode = str(ctx.get("current_mode") or MODE_MAINLINE).strip().lower()
    in_remediation = bool(ctx.get("in_remediation", 0))
    remediation_review_ready = bool(ctx.get("remediation_review_ready", 0))
    cross_skill_trigger = bool(ctx.get("cross_skill_trigger", 0))
    diagnosis_confidence = float(diag.get("diagnosis_confidence", 0.0) or 0.0)
    suggested_prereq_skill = str(diag.get("suggested_prereq_skill") or "").strip()
    fail_streak = int(affect.get("fail_streak", 0) or 0)
    frustration = float(affect.get("frustration", 0.0) or 0.0)
    consecutive_wrong_on_family = int(ctx.get("consecutive_wrong_on_family", 0) or 0)
    rescue_recommended = int(diag.get("rescue_recommended", 0) or 0)

    if current_mode != MODE_MAINLINE or in_remediation:
        return False, 0.0, "not_mainline_mode"
    if not remediation_review_ready:
        return False, 0.0, "review_not_ready"
    if not cross_skill_trigger:
        return False, 0.0, "cross_skill_not_triggered"
    if diagnosis_confidence < 0.8:
        return False, 0.0, "low_diagnosis_confidence"
    if not suggested_prereq_skill:
        return False, 0.0, "missing_prereq_skill"

    risk_signal = (
        fail_streak >= 2
        or frustration >= 0.65
        or consecutive_wrong_on_family >= 2
        or rescue_recommended >= 1
    )
    if not risk_signal:
        return False, 0.0, "risk_signal_not_met"

    bias = 0.32
    if consecutive_wrong_on_family >= 3:
        bias += 0.12
    if fail_streak >= 3:
        bias += 0.10
    if frustration >= 0.8:
        bias += 0.08
    bias = min(0.75, max(0.0, bias))
    return True, float(bias), "mainline_review_ready_cross_skill_high_confidence"


def select_route_action_with_ppo(
    route_state: dict[str, Any],
    action_mask: dict[str, bool],
    model: Any = None,
) -> tuple[str | None, list[float] | None, int | None, str]:
    try:
        _set_last_route_policy_debug()
        if not any(bool(action_mask.get(a, False)) for a in ROUTE_ACTIONS):
            _warn("[adaptive_phase2_policy][WARNING] route action mask has no legal action")
            return None, None, None, "ppo_error"
        route_vector = _route_vector(route_state)
        if model is None:
            model = load_phase2_policy_model()
        if model is None:
            return None, None, None, "ppo_error"

        raw_logits: list[float] | None = None
        if hasattr(model, "predict_route_logits"):
            raw = model.predict_route_logits(route_vector)
            raw_logits = _to_float_list(raw)
        elif hasattr(model, "predict_logits"):
            raw = model.predict_logits(route_vector)
            skill_logits = _to_float_list(raw)
            if skill_logits and len(skill_logits) >= 3:
                raw_logits = [skill_logits[0], skill_logits[1], skill_logits[2]]
        elif callable(model):
            out = model(route_vector)
            raw_logits = _to_float_list(out)
            if raw_logits and len(raw_logits) > 3:
                raw_logits = raw_logits[:3]

        if not raw_logits or len(raw_logits) < 3:
            _warn("[adaptive_phase2_policy] route inference failed: invalid route logits")
            return None, None, None, "ppo_error"

        raw_logits = [float(x) for x in raw_logits[:3]]
        raw_masked_logits = _mask_route_logits(raw_logits, action_mask)
        raw_action_idx = max(range(len(raw_masked_logits)), key=lambda i: raw_masked_logits[i])
        raw_action = IDX_TO_ROUTE.get(raw_action_idx)

        remediate_bias_applied, remediate_bias_value, bias_reason = _compute_remediate_bias(route_state, action_mask)
        biased_logits = list(raw_logits)
        if remediate_bias_applied:
            biased_logits[ROUTE_TO_IDX["remediate"]] = float(biased_logits[ROUTE_TO_IDX["remediate"]] + remediate_bias_value)

        masked_logits = _mask_route_logits(biased_logits, action_mask)
        action_idx = max(range(len(masked_logits)), key=lambda i: masked_logits[i])
        if action_idx not in IDX_TO_ROUTE:
            _warn(f"[adaptive_phase2_policy][ERROR] route action_idx out of range: {action_idx}")
            _set_last_route_policy_debug(
                {
                    "raw_logits": raw_logits,
                    "biased_logits": biased_logits,
                    "masked_logits": masked_logits,
                    "raw_action": raw_action,
                    "raw_action_idx": raw_action_idx,
                    "final_action": None,
                    "final_action_idx": action_idx,
                    "remediate_bias_applied": remediate_bias_applied,
                    "remediate_bias_value": remediate_bias_value,
                    "bias_reason": bias_reason,
                }
            )
            return None, raw_logits, action_idx, "ppo_error"
        action = IDX_TO_ROUTE[action_idx]
        if not action_mask.get(action, False):
            _warn(
                "[adaptive_phase2_policy][ERROR] route action selected but masked "
                f"action={action} mask={action_mask}"
            )
            _set_last_route_policy_debug(
                {
                    "raw_logits": raw_logits,
                    "biased_logits": biased_logits,
                    "masked_logits": masked_logits,
                    "raw_action": raw_action,
                    "raw_action_idx": raw_action_idx,
                    "final_action": action,
                    "final_action_idx": action_idx,
                    "remediate_bias_applied": remediate_bias_applied,
                    "remediate_bias_value": remediate_bias_value,
                    "bias_reason": bias_reason,
                }
            )
            return None, raw_logits, action_idx, "ppo_error"
        _set_last_route_policy_debug(
            {
                "raw_logits": raw_logits,
                "biased_logits": biased_logits,
                "masked_logits": masked_logits,
                "raw_action": raw_action,
                "raw_action_idx": raw_action_idx,
                "final_action": action,
                "final_action_idx": action_idx,
                "remediate_bias_applied": remediate_bias_applied,
                "remediate_bias_value": remediate_bias_value,
                "bias_reason": bias_reason,
            }
        )
        _info(
            "[adaptive_phase2_policy] route inference "
            f"raw_logits={raw_logits} biased_logits={biased_logits} masked_logits={masked_logits} "
            f"raw_action={raw_action} action_idx={action_idx} action={action} action_mask={action_mask} "
            f"remediate_bias_applied={remediate_bias_applied} remediate_bias_value={remediate_bias_value:.3f} "
            f"bias_reason={bias_reason}"
        )
        return action, raw_logits, action_idx, "ppo"
    except Exception as exc:
        _warn(
            "[adaptive_phase2_policy] route inference exception "
            f"type={type(exc).__name__} message={exc} traceback={traceback.format_exc()}"
        )
        _set_last_route_policy_debug()
        return None, None, None, "ppo_error"


def select_route_action_heuristic(
    route_state: dict[str, Any],
    action_mask: dict[str, bool],
) -> tuple[str, dict[str, Any]]:
    ctx = dict(route_state.get("routing_context") or {})
    in_remediation = bool(ctx.get("in_remediation", 0))
    rem_steps = int(ctx.get("remediation_step_count", 0) or 0)
    diag = dict(route_state.get("diagnostic_signal") or {})
    rescue_recommended = int(diag.get("rescue_recommended", 0) or 0)

    if in_remediation and action_mask.get("return", False) and rem_steps >= 2:
        return "return", {"mode": "heuristic_return"}
    if in_remediation:
        return "stay", {"mode": "heuristic_stay_remediation"}
    if rescue_recommended and action_mask.get("remediate", False):
        return "remediate", {"mode": "heuristic_remediate"}
    return "stay", {"mode": "heuristic_stay"}


def map_route_action_by_mode(action: str | None, *, current_mode: str) -> str:
    """
    Interpret raw route action in a mode-safe way:
    - mainline: allow stay/remediate, suppress return
    - remediation: allow stay/return, suppress remediate
    """
    mode = str(current_mode or MODE_MAINLINE).strip().lower()
    normalized = str(action or "stay").strip().lower()
    if normalized not in {"stay", "remediate", "return"}:
        normalized = "stay"
    if mode == MODE_MAINLINE:
        if normalized == "return":
            return "stay"
        return "remediate" if normalized == "remediate" else "stay"
    if mode == MODE_REMEDIATION:
        if normalized == "remediate":
            return "stay"
        return "return" if normalized == "return" else "stay"
    return "stay"


def select_agent_skill_heuristic(
    agent_state: dict[str, Any],
    allowed_agent_skills: list[str] | None,
) -> tuple[str | None, dict[str, Any]]:
    """
    Heuristic fallback policy:
    - choose weakest mastery skill first
    - avoid too many consecutive picks for same skill
    - when frustration is high, bias toward remedial pick
    """
    allowed = _normalize_allowed_agent_skills(allowed_agent_skills)
    mastery_by_skill = dict(agent_state.get("mastery_by_skill") or {})
    if not mastery_by_skill:
        mastery_by_skill = {skill: 0.45 for skill in SKILL_LABELS}
    for skill in SKILL_LABELS:
        mastery_by_skill.setdefault(skill, 0.45)

    frustration_index = int(agent_state.get("frustration_index", 0) or 0)
    same_skill_streak = int(agent_state.get("same_skill_streak", 0) or 0)
    system_skill_id = str(agent_state.get("system_skill_id", "") or "").strip()
    current_agent_skill = resolve_agent_skill(system_skill_id)

    ranked = sorted(
        [skill for skill in SKILL_LABELS if skill in allowed],
        key=lambda skill: (float(mastery_by_skill.get(skill, 0.45)), skill),
    )
    if not ranked:
        ranked = list(SKILL_LABELS)
    selected = ranked[0]
    mode = "weakest_mastery"

    if same_skill_streak >= 3 and current_agent_skill == selected and len(ranked) > 1:
        selected = ranked[1]
        mode = "anti_same_skill_streak"

    if frustration_index >= 2:
        mode = "remedial_bias_" + mode

    return selected, {
        "selection_mode": mode,
        "frustration_index": frustration_index,
        "same_skill_streak": same_skill_streak,
        "current_agent_skill": current_agent_skill,
        "ranked_skills": ranked,
        "mastery_by_skill": mastery_by_skill,
        "selected_agent_skill": selected,
        "allowed_agent_skills": allowed,
    }


# Backward-compatible alias for existing callers.
def select_agent_skill(agent_state: dict) -> tuple[str | None, dict[str, Any]]:
    return select_agent_skill_heuristic(agent_state, list(SKILL_LABELS))
