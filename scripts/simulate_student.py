import csv
import os
import random
import statistics

# ====================
# 1) 常數區
# ====================
RANDOM_SEED = 42
N_PER_TYPE = 100
MAX_STEPS = 30
TARGET_MASTERY = 0.85

MASTERY_UPDATE = {
    "correct": 0.15,
    "minor_error": -0.02,
    "major_error": -0.05,
}

STRATEGIES = ["AB1_Baseline", "AB2_RuleBased", "AB3_PPO_Dynamic"]
STUDENT_TYPES = ["Careless", "Weak", "Average"]


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value into [low, high]."""
    return max(low, min(high, value))


# ====================
# 2) SimulatedStudent 類別
# ====================
class SimulatedStudent:
    """A lightweight cognitive student model for one episode."""

    def __init__(self, student_type: str, initial_mastery: float = 0.35) -> None:
        self.student_type = student_type
        self.base_accuracy = self._get_base_accuracy(student_type)
        self.current_accuracy = self.base_accuracy
        self.mastery = clamp(initial_mastery, 0.0, 1.0)
        self.fail_streak = 0
        self.remediation_count = 0
        self.unnecessary_remediations = 0
        self.reached_mastery_step: int | None = None

    def _get_base_accuracy(self, student_type: str) -> float:
        if student_type == "Careless":
            return 0.80
        if student_type == "Weak":
            return 0.30
        if student_type == "Average":
            return 0.60
        raise ValueError(f"Unknown student_type: {student_type}")

    def _get_minor_error_probability(self) -> float:
        if self.student_type == "Careless":
            return 0.90
        if self.student_type == "Weak":
            return 0.20
        if self.student_type == "Average":
            return 0.50
        raise ValueError(f"Unknown student_type: {self.student_type}")

    def _get_remediation_gain(self) -> float:
        if self.student_type == "Careless":
            return 0.02
        if self.student_type == "Weak":
            return 0.12
        if self.student_type == "Average":
            return 0.20
        raise ValueError(f"Unknown student_type: {self.student_type}")

    def answer_question(self) -> dict[str, bool | str]:
        """
        Simulate one question answer.
        Returns:
            {"is_correct": bool, "error_type": "correct"|"minor_error"|"major_error"}
        """
        if random.random() < self.current_accuracy:
            self.fail_streak = 0
            return {"is_correct": True, "error_type": "correct"}

        self.fail_streak += 1
        is_minor = random.random() < self._get_minor_error_probability()
        error_type = "minor_error" if is_minor else "major_error"
        return {"is_correct": False, "error_type": error_type}

    def apply_remediation(self) -> None:
        """Apply one remediation gain to current accuracy."""
        gain = self._get_remediation_gain()
        self.current_accuracy = clamp(self.current_accuracy + gain, 0.0, 0.95)
        self.remediation_count += 1

    def reset_episode_state(self) -> None:
        """Reset counters if caller wants to reuse one object."""
        self.current_accuracy = self.base_accuracy
        self.mastery = 0.35
        self.fail_streak = 0
        self.remediation_count = 0
        self.unnecessary_remediations = 0
        self.reached_mastery_step = None


def update_mastery(student: SimulatedStudent, error_type: str) -> None:
    """Update mastery based on answer result and clamp to [0, 1]."""
    delta = MASTERY_UPDATE[error_type]
    student.mastery = clamp(student.mastery + delta, 0.0, 1.0)


def maybe_mark_reached_mastery(student: SimulatedStudent, total_steps: int) -> None:
    """Set first step when mastery reaches target."""
    if student.reached_mastery_step is None and student.mastery >= TARGET_MASTERY:
        student.reached_mastery_step = total_steps


# ====================
# 3) 三種策略函式 / 邏輯
# ====================
def run_ab1_baseline(student: SimulatedStudent) -> int:
    """AB1: mainline only, no remediation."""
    total_steps = 0
    while total_steps < MAX_STEPS and student.mastery < TARGET_MASTERY:
        result = student.answer_question()
        total_steps += 1
        update_mastery(student, str(result["error_type"]))
        maybe_mark_reached_mastery(student, total_steps)
    return total_steps


def run_ab2_rule_based(student: SimulatedStudent) -> int:
    """AB2: any wrong answer triggers 3-step remediation."""
    total_steps = 0
    remediation_steps = 3

    while total_steps < MAX_STEPS and student.mastery < TARGET_MASTERY:
        result = student.answer_question()
        error_type = str(result["error_type"])
        total_steps += 1
        update_mastery(student, error_type)
        maybe_mark_reached_mastery(student, total_steps)

        if student.mastery >= TARGET_MASTERY or total_steps >= MAX_STEPS:
            break

        if not bool(result["is_correct"]):
            if error_type == "minor_error" and student.mastery > 0.6:
                student.unnecessary_remediations += 1

            remaining = MAX_STEPS - total_steps
            consumed = min(remediation_steps, remaining)
            total_steps += consumed
            if consumed == remediation_steps:
                student.apply_remediation()

    return total_steps


def run_ab3_ppo_dynamic(student: SimulatedStudent) -> int:
    """AB3: dynamic remediation trigger with 2-step remediation."""
    total_steps = 0
    remediation_steps = 2

    while total_steps < MAX_STEPS and student.mastery < TARGET_MASTERY:
        result = student.answer_question()
        error_type = str(result["error_type"])
        total_steps += 1
        update_mastery(student, error_type)
        maybe_mark_reached_mastery(student, total_steps)

        if student.mastery >= TARGET_MASTERY or total_steps >= MAX_STEPS:
            break

        if not bool(result["is_correct"]):
            trigger = (student.fail_streak >= 2) or (
                student.mastery < 0.5 and error_type == "major_error"
            )
            if trigger:
                if error_type == "minor_error" and student.mastery > 0.6:
                    student.unnecessary_remediations += 1

                remaining = MAX_STEPS - total_steps
                consumed = min(remediation_steps, remaining)
                total_steps += consumed
                if consumed == remediation_steps:
                    student.apply_remediation()

    return total_steps


# ====================
# 4) 單次 episode 模擬函式
# ====================
def simulate_episode(student_type: str, strategy_name: str) -> dict[str, int | float | str | None]:
    """Run one episode for a student type under one strategy."""
    student = SimulatedStudent(student_type=student_type, initial_mastery=0.35)

    if strategy_name == "AB1_Baseline":
        total_steps = run_ab1_baseline(student)
    elif strategy_name == "AB2_RuleBased":
        total_steps = run_ab2_rule_based(student)
    elif strategy_name == "AB3_PPO_Dynamic":
        total_steps = run_ab3_ppo_dynamic(student)
    else:
        raise ValueError(f"Unknown strategy_name: {strategy_name}")

    success = 1 if student.mastery >= TARGET_MASTERY else 0
    return {
        "strategy": strategy_name,
        "student_type": student_type,
        "success": success,
        "total_steps": total_steps,
        "final_mastery": round(student.mastery, 4),
        "reached_mastery_step": student.reached_mastery_step,
        "remediation_count": student.remediation_count,
        "unnecessary_remediations": student.unnecessary_remediations,
        "final_accuracy": round(student.current_accuracy, 4),
    }


# ====================
# 5) 批次實驗函式
# ====================
def run_batch_experiments() -> list[dict[str, int | float | str | None]]:
    """Run all strategy x student_type episodes."""
    episodes: list[dict[str, int | float | str | None]] = []
    for strategy in STRATEGIES:
        for student_type in STUDENT_TYPES:
            for _ in range(N_PER_TYPE):
                episodes.append(simulate_episode(student_type, strategy))
    return episodes


def build_strategy_summary(
    episodes: list[dict[str, int | float | str | None]]
) -> list[dict[str, float | str]]:
    """Aggregate overall metrics by strategy."""
    rows: list[dict[str, float | str]] = []
    for strategy in STRATEGIES:
        subset = [e for e in episodes if e["strategy"] == strategy]
        success_rate = statistics.mean(float(e["success"]) for e in subset) * 100.0
        avg_steps = statistics.mean(float(e["total_steps"]) for e in subset)
        avg_unnecessary = statistics.mean(
            float(e["unnecessary_remediations"]) for e in subset
        )
        avg_mastery = statistics.mean(float(e["final_mastery"]) for e in subset)
        rows.append(
            {
                "Strategy": strategy,
                "Success Rate": success_rate,
                "Avg Steps": avg_steps,
                "Avg Unnecessary Remediations": avg_unnecessary,
                "Avg Final Mastery": avg_mastery,
            }
        )
    return rows


def build_strategy_student_summary(
    episodes: list[dict[str, int | float | str | None]]
) -> list[dict[str, float | str]]:
    """Aggregate metrics by strategy and student type."""
    rows: list[dict[str, float | str]] = []
    for strategy in STRATEGIES:
        for student_type in STUDENT_TYPES:
            subset = [
                e
                for e in episodes
                if e["strategy"] == strategy and e["student_type"] == student_type
            ]
            success_rate = statistics.mean(float(e["success"]) for e in subset) * 100.0
            avg_steps = statistics.mean(float(e["total_steps"]) for e in subset)
            avg_unnecessary = statistics.mean(
                float(e["unnecessary_remediations"]) for e in subset
            )
            avg_mastery = statistics.mean(float(e["final_mastery"]) for e in subset)
            rows.append(
                {
                    "Strategy": strategy,
                    "Student Type": student_type,
                    "Success Rate": success_rate,
                    "Avg Steps": avg_steps,
                    "Avg Unnecessary Remediations": avg_unnecessary,
                    "Avg Final Mastery": avg_mastery,
                }
            )
    return rows


# ====================
# 6) ASCII 統計表輸出函式
# ====================
def format_cell(header: str, value: float | str) -> str:
    """Format output by column type."""
    if header == "Success Rate":
        return f"{float(value):.2f}%"
    if header.startswith("Avg"):
        return f"{float(value):.2f}"
    return str(value)


def print_ascii_table(title: str, headers: list[str], rows: list[dict[str, float | str]]) -> None:
    """Print a clean aligned ASCII table."""
    rendered_rows: list[list[str]] = []
    for row in rows:
        rendered_rows.append([format_cell(h, row[h]) for h in headers])

    widths = []
    for idx, header in enumerate(headers):
        col_values = [r[idx] for r in rendered_rows]
        max_len = max([len(header)] + [len(v) for v in col_values])
        widths.append(max_len)

    def build_separator() -> str:
        return "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def build_row(cells: list[str]) -> str:
        pieces = []
        for i, cell in enumerate(cells):
            pieces.append(f" {cell.ljust(widths[i])} ")
        return "|" + "|".join(pieces) + "|"

    print(f"\n{title}")
    print(build_separator())
    print(build_row(headers))
    print(build_separator())
    for line in rendered_rows:
        print(build_row(line))
    print(build_separator())


# ====================
# 7) CSV 輸出函式
# ====================
def write_episode_csv(episodes: list[dict[str, int | float | str | None]]) -> str:
    """Write raw episode records to reports CSV."""
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(reports_dir, "ablation_simulation_results.csv")

    fieldnames = [
        "strategy",
        "student_type",
        "success",
        "total_steps",
        "final_mastery",
        "reached_mastery_step",
        "remediation_count",
        "unnecessary_remediations",
        "final_accuracy",
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for episode in episodes:
            row = dict(episode)
            if row["reached_mastery_step"] is None:
                row["reached_mastery_step"] = ""
            writer.writerow(row)

    return output_path


# ====================
# 8) main()
# ====================
def main() -> None:
    """Run full ablation simulation workflow."""
    random.seed(RANDOM_SEED)

    episodes = run_batch_experiments()
    strategy_summary = build_strategy_summary(episodes)
    strategy_student_summary = build_strategy_student_summary(episodes)

    print(f"Total episodes: {len(episodes)}")
    print_ascii_table(
        title="Table 1: Overall Strategy Comparison",
        headers=[
            "Strategy",
            "Success Rate",
            "Avg Steps",
            "Avg Unnecessary Remediations",
            "Avg Final Mastery",
        ],
        rows=strategy_summary,
    )
    print_ascii_table(
        title="Table 2: Strategy x Student Type Comparison",
        headers=[
            "Strategy",
            "Student Type",
            "Success Rate",
            "Avg Steps",
            "Avg Unnecessary Remediations",
            "Avg Final Mastery",
        ],
        rows=strategy_student_summary,
    )

    output_path = write_episode_csv(episodes)
    print("\nSimulation completed.")
    print(f"Output CSV: {output_path}")
    print(f"RANDOM_SEED: {RANDOM_SEED}")
    print(f"N_PER_TYPE: {N_PER_TYPE}")
    print(f"MAX_STEPS: {MAX_STEPS}")
    print(f"TARGET_MASTERY: {TARGET_MASTERY}")


if __name__ == "__main__":
    main()
