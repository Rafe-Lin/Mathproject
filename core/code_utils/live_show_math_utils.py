# -*- coding: utf-8 -*-
"""Live Show math utilities."""

import re


def _normalize_math_text(text):
    if not text:
        return ""
    normalized = str(text)
    replacements = {
        "\u00d7": "*",
        "\\times": "*",
        "\u00f7": "/",
        "\\div": "/",
        "（": "(",
        "）": ")",
        "［": "[",
        "］": "]",
        "｛": "{",
        "｝": "}",
        "－": "-",
        "＋": "+",
        "｜": "|",
    }
    for src, dst in replacements.items():
        normalized = normalized.replace(src, dst)

    frac_pattern = r"\\frac\s*\{\s*([+-]?\d+)\s*\}\s*\{\s*([+-]?\d+)\s*\}"
    normalized = re.sub(frac_pattern, r"(\1/\2)", normalized)

    def _mixed_to_improper(match):
        sign_token = match.group('sign') or ''
        whole = int(match.group('whole'))
        num = int(match.group('num'))
        den = int(match.group('den'))
        if den == 0:
            return match.group(0)
        improper_num = whole * den + num
        return f"{sign_token}({improper_num}/{den})"

    mixed_pattern = r"(?<!\d)(?P<sign>[+-]?)\s*(?P<whole>\d+)\s+(?P<num>\d+)\s*/\s*(?P<den>\d+)(?!\d)"
    normalized = re.sub(mixed_pattern, _mixed_to_improper, normalized)

    mixed_compact_pattern = r"(?<![\d\)])(?P<sign>[+-]?)\s*(?P<whole>\d+)\s*\(\s*(?P<num>\d+)\s*/\s*(?P<den>\d+)\s*\)"
    normalized = re.sub(mixed_compact_pattern, _mixed_to_improper, normalized)
    return normalized


def _scan_number_spans(compact_expr):
    spans = []
    i = 0
    while i < len(compact_expr):
        ch = compact_expr[i]
        if ch.isdigit():
            j = i
            while j < len(compact_expr) and compact_expr[j].isdigit():
                j += 1
            if j < len(compact_expr) and compact_expr[j] == '.':
                k = j + 1
                while k < len(compact_expr) and compact_expr[k].isdigit():
                    k += 1
                if k > j + 1:
                    j = k
            spans.append((i, j, False))
            i = j
            continue

        if ch == '-' and i + 1 < len(compact_expr) and compact_expr[i + 1].isdigit():
            prev = compact_expr[i - 1] if i > 0 else ''
            unary = (i == 0 or prev in '([{|+*/')
            if unary:
                j = i + 1
                while j < len(compact_expr) and compact_expr[j].isdigit():
                    j += 1
                if j < len(compact_expr) and compact_expr[j] == '.':
                    k = j + 1
                    while k < len(compact_expr) and compact_expr[k].isdigit():
                        k += 1
                    if k > j + 1:
                        j = k
                spans.append((i, j, True))
                i = j
                continue
        i += 1
    return spans


def _count_binary_ops(compact_expr):
    sequence = []
    prev = ""
    for idx, ch in enumerate(compact_expr):
        if ch not in "+-*/":
            prev = ch
            continue

        is_unary_minus = ch == "-" and (idx == 0 or prev in "([{|+-*/")
        if is_unary_minus:
            prev = ch
            continue

        if ch == "+":
            sequence.append("plus")
        elif ch == "-":
            sequence.append("minus")
        elif ch == "*":
            sequence.append("times")
        elif ch == "/":
            sequence.append("divide")
        prev = ch
    counts = {
        "plus": sequence.count("plus"),
        "minus": sequence.count("minus"),
        "times": sequence.count("times"),
        "divide": sequence.count("divide"),
    }
    return sequence, counts


def _extract_enclosed_segments(compact_expr, left_ch, right_ch):
    segments = []
    stack = []
    for i, ch in enumerate(compact_expr):
        if ch == left_ch:
            stack.append(i)
        elif ch == right_ch and stack:
            start = stack.pop()
            if len(stack) == 0:
                segments.append(compact_expr[start + 1:i])
    return segments


def _extract_abs_segments(compact_expr):
    segments = []
    opens = []
    for i, ch in enumerate(compact_expr):
        if ch == '|':
            if opens:
                start = opens.pop()
                segments.append(compact_expr[start + 1:i])
            else:
                opens.append(i)
    return segments


def _segment_stats(segment_expr):
    seq, counts = _count_binary_ops(segment_expr)
    number_spans = _scan_number_spans(segment_expr)
    return {
        "numbers": len(number_spans),
        "ops": len(seq),
        "plus": counts["plus"],
        "minus": counts["minus"],
        "times": counts["times"],
        "divide": counts["divide"],
    }


def _build_structural_profile(text):
    norm = _normalize_math_text(text)
    compact = "".join(norm.split())
    sequence, counts = _count_binary_ops(compact)
    number_spans = _scan_number_spans(compact)

    bracket_segments = _extract_enclosed_segments(compact, '[', ']')
    brace_segments = _extract_enclosed_segments(compact, '{', '}')
    all_bracket_segments = bracket_segments + brace_segments

    abs_segments = _extract_abs_segments(compact)

    bracket_stats = [_segment_stats(seg) for seg in all_bracket_segments]
    abs_stats = [_segment_stats(seg) for seg in abs_segments]

    return {
        "normalized": compact,
        "operator_sequence": sequence,
        "operator_count": len(sequence),
        "counts": counts,
        "number_count": len(number_spans),
        "bracket_count": len(all_bracket_segments),
        "abs_count": len(abs_segments),
        "bracket_stats": bracket_stats,
        "abs_stats": abs_stats,
        "has_abs": len(abs_segments) > 0,
        "has_square_brackets": len(all_bracket_segments) > 0,
        "has_parentheses": "(" in compact and ")" in compact,
        "has_parenthesized_negative": "(-" in compact,
        "has_braces": len(brace_segments) > 0,
    }


def _extract_operator_fingerprint(text):
    return _build_structural_profile(text)


def _build_isomorphic_constraints(source_text, json_spec=None):
    fp = _build_structural_profile(source_text)
    seq_text = " -> ".join(fp["operator_sequence"]) if fp["operator_sequence"] else "none"
    forbidden_ops = [
        op
        for op in ("plus", "minus", "times", "divide")
        if fp["counts"].get(op, 0) == 0
    ]

    lines = [
        "Follow the original expression structure exactly.",
        f"1) Keep number token count = {fp['number_count']}.",
        f"2) Keep binary operator count = {fp['operator_count']}.",
        f"3) Keep operator order = {seq_text}.",
        (
            "4) Keep operator counts: "
            f"+={fp['counts']['plus']}, "
            f"-={fp['counts']['minus']}, "
            f"*={fp['counts']['times']}, "
            f"/={fp['counts']['divide']}."
        ),
    ]

    if fp["has_square_brackets"]:
        lines.append(f"5) Keep bracket segment count = {fp['bracket_count']}.")
    else:
        lines.append("5) Do not introduce extra bracket segments.")

    if fp["has_abs"]:
        lines.append(f"6) Keep absolute-value segment count = {fp['abs_count']}.")
    else:
        lines.append("6) Do not introduce absolute-value segments.")

    if fp["has_parenthesized_negative"]:
        lines.append("7) Keep parenthesized negative numbers, e.g. (-7).")
    else:
        lines.append("7) Avoid adding unnecessary parenthesized negatives.")

    if forbidden_ops:
        lines.append(f"8) Forbidden operators in final form: {', '.join(forbidden_ops)}.")

    if json_spec and isinstance(json_spec, dict):
        structure = json_spec.get("structure") or ""
        if structure:
            lines.append(f"9) Preferred structure hint: {structure}.")

    return "\n".join(lines), fp


def _select_liveshow_structure_template(fp):
    if fp.get("has_abs"):
        template_id = "T3_ABS_MIXED"
        template_text = (
            "Template T3 (absolute value form): A op1 B | op2 C op3 D\n"
            "- Preserve absolute-value blocks.\n"
            "- Keep operator sequence consistent with source.\n"
            "- Keep negative numbers parenthesized when needed."
        )
        return template_id, template_text

    if fp.get("has_square_brackets"):
        template_id = "T2_BRACKETED_NESTED"
        template_text = (
            "Template T2 (bracketed form): [ ... ] op [ ... ]\n"
            "- Preserve bracket nesting structure.\n"
            "- Keep operator sequence consistent with source.\n"
            "- Avoid introducing extra terms."
        )
        return template_id, template_text

    template_id = "T1_LINEAR_MIXED"
    template_text = (
        "Template T1 (linear mixed form): A op1 B op2 C ...\n"
        "- Preserve operator sequence and operator counts.\n"
        "- Keep number token count aligned with source.\n"
        "- Avoid drifting to a different family."
    )
    return template_id, template_text


def _extract_math_expr_from_question(question_text):
    if not question_text:
        return ""

    def _clean_candidate(expr):
        if expr is None:
            return ""
        out = str(expr).strip()
        out = out.strip('$').strip()
        out = re.sub(r'[。．\.?？]+$', '', out).strip()
        out = re.sub(r'^(?:計算|請計算|求|Compute|Evaluate)\s*', '', out, flags=re.IGNORECASE).strip()
        out = re.sub(r'\s*(?:的值|等於多少|是多少|值為何)\s*$', '', out).strip()
        if '=' in out:
            out = out.split('=', 1)[0].strip()
        if out and out[0] in '+*/':
            out = out[1:].strip()
        return out

    text = str(question_text).strip()
    m = re.search(r'\$(.*?)\$', text)
    if m:
        return _clean_candidate(m.group(1))

    m2 = re.search(r'(?:計算|請計算|求)\s*(.+?)\s*(?:的值|等於多少|是多少)?\s*[。．\.?？]?$', text)
    if m2:
        return _clean_candidate(m2.group(1))

    return _clean_candidate(text)


def _to_eval_expression_template(expr):
    temp = re.sub(r'\{v(\d+)\}', r'__V\1__', expr or "")

    norm = _normalize_math_text(temp)
    compact = "".join(norm.split())

    compact = compact.replace('\\left', '').replace('\\right', '').replace('\\text', '')
    compact = compact.replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")")

    out = []
    abs_open = False
    for ch in compact:
        if ch == '|':
            if not abs_open:
                out.append('abs(')
                abs_open = True
            else:
                out.append(')')
                abs_open = False
        else:
            out.append(ch)

    if abs_open:
        out.append(')')

    final_expr = "".join(out)
    final_expr = final_expr.strip().strip('$').strip()
    final_expr = re.sub(r'[。．\.?？]+$', '', final_expr).strip()
    if '=' in final_expr:
        final_expr = final_expr.split('=', 1)[0].strip()
    if final_expr and final_expr[0] in '+*/':
        final_expr = final_expr[1:].strip()

    atom = r'(?:__V\d+__|-?\d+)'
    frac_pat = rf'(?<![\w\)])({atom})/({atom})(?![\w\(])'
    for _ in range(8):
        final_expr, n = re.subn(frac_pat, r'(\1/\2)', final_expr)
        if n == 0:
            break

    final_expr = re.sub(r'__V(\d+)__', r'{v\1}', final_expr)
    return final_expr


def _recompute_correct_answer_from_question(question_text):
    from fractions import Fraction

    expr = _extract_math_expr_from_question(question_text)
    if not expr:
        return None

    eval_expr = _to_eval_expression_template(expr)
    if re.fullmatch(r"[0-9+\-*/().aabs]+", eval_expr):
        try:
            val = eval(eval_expr, {"__builtins__": {}}, {"abs": abs})
        except Exception:
            val = None
        if val is not None:
            try:
                fval = Fraction(val).limit_denominator()
            except Exception:
                try:
                    fval = Fraction(str(val)).limit_denominator()
                except Exception:
                    fval = None
            if fval is not None:
                if fval.denominator == 1:
                    return str(fval.numerator)
                return f"{fval.numerator}/{fval.denominator}"

    # Radical add/sub fallback: supports forms like
    # \sqrt{12}+\sqrt{18}-\sqrt{27}+\sqrt{50}
    # with optional integer coefficients before \sqrt{...}.
    src = re.sub(r"\s+", "", str(expr or ""))
    # Some fallback paths persist escaped LaTeX (e.g. "\\\\sqrt{8}").
    # Normalize repeated backslashes so parser sees canonical commands.
    src = re.sub(r"\\{2,}", r"\\", src)
    if (r"\sqrt{" in src) and (r"\times" not in src) and (r"\div" not in src):
        term_re = re.compile(r"([+\-]?)(\d*)\\sqrt\{(\d+)\}")
        pos = 0
        terms: dict[int, int] = {}
        parse_ok = True
        while pos < len(src):
            m = term_re.match(src, pos)
            if not m:
                parse_ok = False
                break
            sign = -1 if m.group(1) == "-" else 1
            c_raw = m.group(2)
            coeff = int(c_raw) if c_raw else 1
            rad = int(m.group(3))

            # simplify coeff*sqrt(rad)
            out = 1
            inner = rad
            i = 2
            while i * i <= inner:
                sq = i * i
                while inner % sq == 0:
                    out *= i
                    inner //= sq
                i += 1
            coeff_final = sign * coeff * out
            rad_final = inner
            terms[rad_final] = terms.get(rad_final, 0) + coeff_final
            pos = m.end()

        if parse_ok and pos == len(src):
            items = [(r, c) for r, c in sorted(terms.items()) if c != 0]
            if not items:
                return "0"

            parts: list[str] = []
            for idx, (r, c) in enumerate(items):
                neg = c < 0
                abs_c = abs(c)
                if r == 1:
                    body = str(abs_c)
                elif abs_c == 1:
                    body = rf"\sqrt{{{r}}}"
                else:
                    body = rf"{abs_c}\sqrt{{{r}}}"
                if idx == 0:
                    parts.append(("-" if neg else "") + body)
                else:
                    parts.append((" - " if neg else " + ") + body)
            return "".join(parts)

    # Sympy fallback for more complex radical forms, including:
    # - \sqrt{1\frac{9}{16}} style mixed fractions inside radicals
    # - \frac with radical expressions
    try:
        import sympy as sp

        src2 = re.sub(r"\s+", "", str(expr or ""))
        src2 = re.sub(r"\\{2,}", r"\\", src2)

        def _mixed_latex_to_rational(match):
            sign = match.group(1) or ""
            whole = int(match.group(2))
            num = int(match.group(3))
            den = int(match.group(4))
            if den == 0:
                return match.group(0)
            imp = whole * den + num
            return f"{sign}(({imp})/({den}))"

        src2 = re.sub(
            r"([+\-]?)\s*(\d+)\\frac\{(\d+)\}\{(\d+)\}",
            _mixed_latex_to_rational,
            src2,
        )
        src2 = re.sub(
            r"\\frac\{([^{}]+)\}\{([^{}]+)\}",
            r"((\1)/(\2))",
            src2,
        )

        def _replace_sqrt_braces(s: str) -> str:
            out = []
            i = 0
            n = len(s)
            while i < n:
                if s.startswith(r"\sqrt{", i):
                    j = i + 6
                    depth = 1
                    while j < n and depth > 0:
                        if s[j] == "{":
                            depth += 1
                        elif s[j] == "}":
                            depth -= 1
                        j += 1
                    if depth != 0:
                        return s
                    inner = s[i + 6 : j - 1]
                    out.append("sqrt(" + inner + ")")
                    i = j
                else:
                    out.append(s[i])
                    i += 1
            return "".join(out)

        src2 = _replace_sqrt_braces(src2)
        src2 = src2.replace("{", "(").replace("}", ")")
        src2 = src2.replace(r"\times", "*").replace(r"\div", "/")

        val = sp.simplify(sp.sympify(src2, locals={"sqrt": sp.sqrt}))
        if val.is_Rational:
            p, q = int(val.p), int(val.q)
            if q == 1:
                return str(p)
            return f"{p}/{q}"
        out = sp.latex(val)
        out = out.replace(r"\left", "").replace(r"\right", "")
        return out
    except Exception:
        return None


def _is_expression_isomorphic(expected_fp, generated_expr):
    if not generated_expr:
        return False
    # Empty fingerprint = bypass mode (radical orchestrator, OCR-less path, etc.)
    # All fields default to None; comparing None against real values always returns
    # False ??treating an empty dict as "no constraints" is the correct semantic.
    if not expected_fp:
        return True
    got_fp = _build_structural_profile(generated_expr)
    if got_fp.get("operator_sequence") != expected_fp.get("operator_sequence"):
        return False
    if got_fp.get("number_count") != expected_fp.get("number_count"):
        return False
    if got_fp.get("counts") != expected_fp.get("counts"):
        return False
    if got_fp.get("has_abs") != expected_fp.get("has_abs"):
        return False
    if got_fp.get("has_square_brackets") != expected_fp.get("has_square_brackets"):
        return False
    if got_fp.get("abs_count") != expected_fp.get("abs_count"):
        return False
    if got_fp.get("bracket_count") != expected_fp.get("bracket_count"):
        return False
    if got_fp.get("bracket_stats") != expected_fp.get("bracket_stats"):
        return False
    if got_fp.get("abs_stats") != expected_fp.get("abs_stats"):
        return False
    return True


def _profile_diff_summary(expected_fp, generated_expr):
    got_fp = _build_structural_profile(generated_expr or "")
    diffs = []

    if got_fp.get("operator_sequence") != expected_fp.get("operator_sequence"):
        diffs.append(f"operator_sequence: expected={expected_fp.get('operator_sequence')} got={got_fp.get('operator_sequence')}")
    if got_fp.get("number_count") != expected_fp.get("number_count"):
        diffs.append(f"number_count: expected={expected_fp.get('number_count')} got={got_fp.get('number_count')}")
    if got_fp.get("counts") != expected_fp.get("counts"):
        diffs.append(f"op_counts: expected={expected_fp.get('counts')} got={got_fp.get('counts')}")
    if got_fp.get("bracket_count") != expected_fp.get("bracket_count"):
        diffs.append(f"bracket_count: expected={expected_fp.get('bracket_count')} got={got_fp.get('bracket_count')}")
    if got_fp.get("abs_count") != expected_fp.get("abs_count"):
        diffs.append(f"abs_count: expected={expected_fp.get('abs_count')} got={got_fp.get('abs_count')}")
    if got_fp.get("bracket_stats") != expected_fp.get("bracket_stats"):
        diffs.append("bracket_stats mismatch")
    if got_fp.get("abs_stats") != expected_fp.get("abs_stats"):
        diffs.append("abs_stats mismatch")

    return diffs


# ===========================================================================
# Radical Math DNA ??specialised profiler for jh_?詨飛2銝FourOperationsOfRadicals
# ===========================================================================

def _has_square_factor(n: int) -> bool:
    """Return True if integer n contains a perfect-square factor > 1.

    A radicand is *simplifiable* when it is not in its simplest radical form,
    e.g. 12 = 4?3 ????2 = 2??.  Prime radicands (2, 3, 5, 7, ?? are already
    in simplest form and return False.
    """
    if not isinstance(n, int) or n < 4:
        return False
    i = 2
    while i * i <= n:
        if n % (i * i) == 0:
            return True
        i += 1
    return False


def _strip_all_frac_commands(text: str) -> str:
    """Remove every top-level \\frac{..}{..} (and \\dfrac) from *text* for sqrt-outside-frac checks."""
    s = str(text or "").replace(r"\dfrac{", r"\frac{")
    out: list[str] = []
    i, n = 0, len(s)
    while i < n:
        if s.startswith(r"\frac{", i):
            j = i + 6
            depth = 1
            while j < n and depth:
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    depth -= 1
                j += 1
            while j < n and s[j] in " \t\n":
                j += 1
            if j >= n or s[j] != "{":
                out.append(s[i])
                i += 1
                continue
            j += 1
            depth = 1
            while j < n and depth:
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    depth -= 1
                j += 1
            i = j
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def _iter_frac_num_den_strings(text: str):
    """Yield (numerator_str, denominator_str) for each \\frac{}{} / \\dfrac{}{}."""
    normalised = str(text or "").replace(r"\dfrac{", r"\frac{")
    i = 0
    while True:
        pos = normalised.find(r"\frac{", i)
        if pos == -1:
            break
        j = pos + 6
        depth = 1
        start_num = j
        while j < len(normalised) and depth > 0:
            if normalised[j] == "{":
                depth += 1
            elif normalised[j] == "}":
                depth -= 1
            j += 1
        num_str = normalised[start_num : j - 1]
        while j < len(normalised) and normalised[j] in " \t\n":
            j += 1
        if j >= len(normalised) or normalised[j] != "{":
            i = pos + 1
            continue
        j += 1
        start_den = j
        depth = 1
        while j < len(normalised) and depth > 0:
            if normalised[j] == "{":
                depth += 1
            elif normalised[j] == "}":
                depth -= 1
            j += 1
        den_str = normalised[start_den : j - 1]
        yield num_str, den_str
        i = pos + 1

def _has_binary_add_sub(expr: str) -> bool:
    """Detect binary + / - operators and ignore unary signs."""
    s = re.sub(r"\s+", "", str(expr or ""))
    if not s:
        return False
    for i, ch in enumerate(s):
        if ch not in "+-":
            continue
        prev = s[i - 1] if i > 0 else ""
        if i == 0 or prev in "({[*/^_+-":
            continue
        return True
    return False

def classify_radical_style(expr: str) -> str:
    """
    Deterministic 8th-grade radical *display* class for OCR / generated LaTeX.

    Returns one of:
      - simple_radical: \\sqrt with square-free integer radicands only; no fraction+sqrt skeleton.
      - simplifiable_radical: at least one integer radicand has a square factor > 1.
      - fraction_radical: \\frac present and \\sqrt appears inside a numerator or denominator
        (and no separate plain-radical strand that makes the item truly *mixed*).
      - mixed: plain \\sqrt strand coexists with a fraction?adical strand (detectable).
    """
    text = str(expr or "")
    if not text.strip():
        return "mixed"

    radicands: list[int] = []
    for m in re.finditer(r"\\sqrt(?:\{(\d+)\}|(\d+))", text):
        try:
            raw = m.group(1) or m.group(2)
            radicands.append(int(raw))
        except ValueError:
            continue

    has_sqrt = bool(radicands) or r"\sqrt" in text
    pairs = list(_iter_frac_num_den_strings(text))
    has_frac = bool(pairs)
    sqrt_in_frac = any(r"\sqrt" in n or r"\sqrt" in d for n, d in pairs)

    has_simplifiable = any(_has_square_factor(n) for n in radicands if n >= 2)

    sqrt_outside_frac_blocks = r"\sqrt" in _strip_all_frac_commands(text)

    # True mixed: sqrt inside a \\frac numerator/denominator AND another \\sqrt outside those blocks.
    if sqrt_in_frac and sqrt_outside_frac_blocks:
        return "mixed"

    # e.g. \\frac{3}{5}\\times5\\sqrt{2} (sqrt not inside \\frac braces).
    if has_frac and has_sqrt and not sqrt_in_frac:
        rem = _strip_all_frac_commands(text)
        rem_core = re.sub(r"\$+", "", rem)
        if _has_binary_add_sub(rem_core):
            return "mixed"
        return "fraction_radical"

    if has_frac and sqrt_in_frac:
        return "fraction_radical"

    # Pure radical division (no add/sub) is treated as fraction-radical family.
    if has_sqrt and (r"\div" in text) and (not _has_binary_add_sub(text)):
        return "fraction_radical"

    if has_sqrt and (_has_binary_add_sub(text) or r"\times" in text or r"\div" in text):
        return "mixed"

    if has_simplifiable:
        return "simplifiable_radical"

    if has_sqrt:
        return "simple_radical"

    return "mixed"


def radical_hard_style_preserved(input_style: str | None, output_style: str) -> tuple[bool, str]:
    """Hard teaching constraint: output class must match input class (mixed matches mixed only)."""
    if input_style is None:
        return True, ""
    out = (output_style or "").strip() or "mixed"
    inp = input_style
    if inp == "mixed":
        if out != "mixed":
            return False, f"input=mixed requires output=mixed, got {out}"
        return True, ""
    if out != inp:
        return False, f"style drift {inp}->{out}"
    return True, ""


def _frac_denominators(text: str) -> list:
    """Return a list of denominator strings from all \\frac{}{} / \\dfrac{}{} in *text*.

    Uses brace-depth tracking so nested LaTeX constructs are handled correctly.
    """
    # Normalise \dfrac ??\frac so a single pass suffices.
    normalised = text.replace(r'\dfrac{', r'\frac{')
    denoms: list = []
    i = 0
    while i < len(normalised):
        pos = normalised.find(r'\frac{', i)
        if pos == -1:
            break
        j = pos + 6  # step past '\frac{'
        # Walk over the numerator brace
        depth = 1
        while j < len(normalised) and depth > 0:
            if normalised[j] == '{':
                depth += 1
            elif normalised[j] == '}':
                depth -= 1
            j += 1
        # Skip optional whitespace between } and {
        while j < len(normalised) and normalised[j] in ' \t\n':
            j += 1
        if j >= len(normalised) or normalised[j] != '{':
            i = pos + 1
            continue
        j += 1  # step past opening '{' of denominator
        denom_start = j
        depth = 1
        while j < len(normalised) and depth > 0:
            if normalised[j] == '{':
                depth += 1
            elif normalised[j] == '}':
                depth -= 1
            j += 1
        denoms.append(normalised[denom_start: j - 1])
        i = pos + 1
    return denoms


def _build_radical_profile(ocr_text: str) -> dict:
    """Extract the *Radical Math DNA* fingerprint: base structural stats + radical counts.

    Combines base operator fingerprint (nums, ops, brackets) with radical-specific
    stats (rad_total, rad_simplified, rad_simplifiable) for the Complexity Mirror UI.
    """
    import re
    text = str(ocr_text or "")

    # 1. Get base structural stats (nums, ops, brackets)
    base_fp = _extract_operator_fingerprint(text)

    # 2. Count total radicals
    rad_total = text.count(r"\sqrt") + text.count("√")

    # 3. Count every integer radicand that still contains a square factor.
    rad_simplifiable = 0
    for m in re.finditer(r"\\sqrt(?:\{(\d+)\}|(\d+))", text):
        raw = m.group(1) or m.group(2)
        try:
            if _has_square_factor(int(raw)):
                rad_simplifiable += 1
        except ValueError:
            continue

    # 4. Calculate simplified radicals
    rad_simplified = max(0, rad_total - rad_simplifiable)

    # 5. Rationalize count (frac/dfrac whose denominator holds \sqrt) for logging
    denoms = _frac_denominators(text)
    rationalize_count = sum(1 for d in denoms if r'\sqrt' in d or '\\sqrt' in d)

    # 6. Merge and return (include backward-compat aliases for _is_radical_isomorphic)
    base_fp.update({
        "rad_total": rad_total,
        "rad_simplified": rad_simplified,
        "rad_simplifiable": rad_simplifiable,
        "rad_count": rad_total,
        "simplifiable_count": rad_simplifiable,
        "rationalize_count": rationalize_count,
    })
    return base_fp


def _is_radical_isomorphic(target_rp: dict, generated_text: str) -> bool:
    """Return True when *generated_text* matches the *target_rp* radical profile.

    Strict fields: rad_count, simplifiable_count.
    rationalize_count is intentionally advisory (not checked here) to avoid
    over-constraining patterns whose denominator style can vary.
    """
    if not generated_text:
        return False
    gen_rp = _build_radical_profile(generated_text)
    if gen_rp['rad_count'] != target_rp.get('rad_count', -1):
        return False
    if gen_rp['simplifiable_count'] != target_rp.get('simplifiable_count', -1):
        return False
    return True


def _radical_profile_diff(target_rp: dict, generated_text: str) -> list:
    """Return human-readable diff strings for every mismatched radical profile field."""
    gen_rp = _build_radical_profile(generated_text or '')
    diffs = []
    for field in ('rad_count', 'simplifiable_count', 'rationalize_count'):
        exp = target_rp.get(field)
        got = gen_rp.get(field)
        if exp is not None and exp != got:
            diffs.append(f"{field}: expected={exp} got={got}")
    return diffs


def _max_bracket_depth(text: str) -> int:
    depth = 0
    max_depth = 0
    for ch in str(text or ""):
        if ch in "([{":
            depth += 1
            if depth > max_depth:
                max_depth = depth
        elif ch in ")]}":
            depth = max(0, depth - 1)
    return max_depth


def build_radical_complexity_mirror_profile(latex_text: str) -> dict:
    """
    Radicals-only???漲?∪??rofile嚗h_*_FourOperationsOfRadicals 撠?澆暺???

    撖虫?蝑? _build_radical_profile嚗?怎垢敹?隞?skill_id gate ??撘??賭蝙?剁?
    ?湔嚗??豢??質?瘝輻 _build_structural_profile / operator fingerprint 頝臬???
    """
    profile = _build_radical_profile(latex_text)
    profile["fraction_count"] = len(list(_iter_frac_num_den_strings(latex_text or "")))
    profile["bracket_depth"] = _max_bracket_depth(_normalize_math_text(latex_text or ""))
    return profile


def radical_complexity_mirror_isomorphic(expected_profile: dict, generated_expr_latex: str) -> bool:
    """Radicals-only mirror check using profile isomorphism."""
    return _is_radical_isomorphic(expected_profile, generated_expr_latex)


def radical_complexity_mirror_diff(expected_profile: dict, generated_expr_latex: str) -> list:
    """Radicals-only mirror diff helper."""
    return _radical_profile_diff(expected_profile, generated_expr_latex)


def radical_complexity_mirror_compare(
    expected_profile: dict,
    generated_expr_latex: str,
    *,
    selected_pattern_id: str | None = None,
    style_preserved: bool = False,
) -> tuple[bool, bool, str]:
    """
    Radicals-only mirror comparator with p2a_mult_direct lightweight tolerance.

    Returns:
      (isomorphic, tolerance_applied, tolerance_reason)
    """
    generated_profile = build_radical_complexity_mirror_profile(generated_expr_latex or "")
    strict_ok = radical_complexity_mirror_isomorphic(expected_profile, generated_expr_latex or "")
    if strict_ok:
        return True, False, ""

    if selected_pattern_id != "p2a_mult_direct":
        return False, False, ""
    if style_preserved is not True:
        return False, False, ""

    counts = generated_profile.get("counts") if isinstance(generated_profile, dict) else {}
    only_times = (
        isinstance(counts, dict)
        and int(counts.get("times", 0) or 0) >= 1
        and int(counts.get("plus", 0) or 0) == 0
        and int(counts.get("minus", 0) or 0) == 0
        and int(counts.get("divide", 0) or 0) == 0
    )
    if not only_times:
        return False, False, ""

    exp_frac = int(expected_profile.get("fraction_count", 0) or 0)
    got_frac = int(generated_profile.get("fraction_count", 0) or 0)
    if exp_frac != got_frac:
        return False, False, ""

    exp_bd = int(expected_profile.get("bracket_depth", 0) or 0)
    got_bd = int(generated_profile.get("bracket_depth", 0) or 0)
    if got_bd > exp_bd:
        return False, False, ""

    exp_rad = int(expected_profile.get("rad_count", 0) or 0)
    got_rad = int(generated_profile.get("rad_count", 0) or 0)
    if abs(exp_rad - got_rad) > 1:
        return False, False, ""

    reason = (
        "p2a_mult_direct tolerance: style_preserved=True, multiplication-only, "
        f"fraction_count unchanged ({exp_frac}), bracket_depth {exp_bd}->{got_bd}, "
        f"rad_count delta={abs(exp_rad - got_rad)}<=1"
    )
    return True, True, reason

