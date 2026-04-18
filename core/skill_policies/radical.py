# -*- coding: utf-8 -*-

POLICIES = [
    {
        "policy_id": "radical-core",
        "family": "radical",
        "skill_ids": [
            "jh_數學2上_FourOperationsOfRadicals",
        ],
        "aliases": [
            "Radicals",
            "jh_數學2上_根號運算",
        ],
        "apply_fraction_eval_patch": False,
        "enable_fraction_display": False,
        "force_fraction_answer": False,
        "fallback_fraction_style": False,
        # ── Orchestrator flags ─────────────────────────────────────────────
        # Radical expressions use \sqrt{} and \frac{} LaTeX which the integer-
        # oriented Complexity Mirror misreads as bracket / division segments.
        # Setting this flag disables the structural-profile iso-guard entirely
        # for this skill; the DomainFunctionHelper engine guarantees correctness.
        "skip_complexity_mirror": True,
        # ── Radical Complexity Mirror (replacement) ────────────────────────
        # Instead of the generic num/op mirror, the radical skill uses a
        # domain-specific DNA check that compares rad_count and
        # simplifiable_count between the OCR input and the generated question.
        # rationalize_count is tracked for logging but not enforced strictly.
        "use_radical_complexity_mirror": True,
        "radical_mirror_fields": ["rad_count", "simplifiable_count"],
    }
]
