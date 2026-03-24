from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Any


def _safe_eval_integer(expr: str) -> int:
    clean = str(expr or "").strip()
    clean = clean.replace("（", "(").replace("）", ")")
    clean = clean.replace("＋", "+").replace("－", "-")
    clean = clean.replace("×", "*").replace("÷", "/")
    clean = clean.replace("｜", "|")
    clean = clean.replace("\\left", "").replace("\\right", "")
    clean = clean.replace("\\times", "*").replace("\\div", "/")
    clean = re.sub(r"(?i)\btimes\b", "*", clean)
    clean = re.sub(r"(?i)\bdiv\b", "/", clean)
    clean = clean.replace("×", "*").replace("÷", "/")
    clean = clean.replace("[", "(").replace("]", ")")
    clean = clean.replace("{", "(").replace("}", ")")
    clean = clean.replace("^", "**")
    clean = re.sub(r"\|([^|]+)\|", r"abs(\1)", clean)
    result = eval(clean, {"__builtins__": {}, "abs": abs}, {})
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    if not isinstance(result, int):
        raise ValueError(f"non-integer result: {expr!r} -> {result!r}")
    return result


def _fmt_signed(n: int) -> str:
    return f"({n})" if n < 0 else str(n)


def _normalize_compact(text: str) -> str:
    return re.sub(r"\s+", "", str(text or ""))


def _replace_math_segments(source: str, replacements: list[str]) -> str:
    idx = 0

    def repl(_: re.Match[str]) -> str:
        nonlocal idx
        value = replacements[idx]
        idx += 1
        return f"${value}$"

    return re.sub(r"\$([^$]+)\$", repl, source)


def _consume_parenthesized(text: str, start: int) -> tuple[str, int]:
    if start >= len(text) or text[start] != "(":
        raise ValueError(f"expected '(' at index {start}")
    depth = 1
    j = start + 1
    while j < len(text) and depth > 0:
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
        j += 1
    if depth != 0:
        raise ValueError(f"unbalanced parentheses in {text!r}")
    return text[start + 1 : j - 1], j


@dataclass
class ExprTemplate:
    original: str
    skeleton: str
    values: list[int]


class IntegerFunctionHelper:
    _NUMBER_TOKEN_RE = re.compile(r"(?:(?<=^)|(?<=[\(\[\+\-\*/]))-?\d+")
    _SPECIAL_MULTIPLIER_BASES = {
        999: (1000, -1),
        1001: (1000, 1),
        1002: (1000, 2),
        998: (1000, -2),
        499: (500, -1),
        501: (500, 1),
        401: (400, 1),
        399: (400, -1),
        198: (200, -2),
        202: (200, 2),
        125: (125, 0),
    }

    def can_handle(self, question_text: str) -> bool:
        try:
            return bool(self.build_config(question_text))
        except Exception:
            return False

    def build_generator_code(self, question_text: str) -> str:
        config_repr = repr(self.build_config(question_text))
        return f"""from core.integer_domain_functions import IntegerFunctionHelper

_INT_HELPER = IntegerFunctionHelper()
_INT_CONFIG = {config_repr}

def generate(level=1, **kwargs):
    return _INT_HELPER.generate_from_config(_INT_CONFIG)

def check(user_answer, correct_answer):
    u = str(user_answer or "").strip().replace(" ", "")
    c = str(correct_answer or "").strip().replace(" ", "")
    if u == c:
        return {{"correct": True, "result": "正確"}}
    try:
        if float(u) == float(c):
            return {{"correct": True, "result": "正確"}}
    except Exception:
        pass
    return {{"correct": False, "result": "錯誤"}}
"""

    def build_config(self, question_text: str) -> dict[str, Any]:
        src = str(question_text or "").strip()

        if self._looks_like_exam_score(src):
            return {"family": "int_exam_score", "source_text": src}
        if self._looks_like_dice_walk(src):
            return {"family": "int_dice_walk", "source_text": src}
        if self._looks_like_guessing_game_score(src):
            return {"family": "int_guessing_game_score", "source_text": src}
        if self._looks_like_temperature_story(src):
            return {"family": "int_temperature_story", "source_text": src}
        if self._looks_like_net_change_story(src):
            return {"family": "int_net_change_story", "source_text": src}
        if self._looks_like_comparison_pairs(src):
            return {
                "family": "int_compare_pairs",
                "source_text": src,
                "pairs": self._extract_compare_pairs(src),
            }
        if self._looks_like_truth_claim(src):
            return {"family": "int_truth_claim", "source_text": src}

        special_mul = self._extract_special_multiplier_config(src)
        if special_mul:
            return special_mul

        expr_templates = self._extract_expr_templates(src)
        if expr_templates:
            return {
                "family": "int_eval_batch",
                "source_text": src,
                "expressions": [template.__dict__ for template in expr_templates],
            }

        raise ValueError(f"Unsupported integer family: {src[:80]}")

    def generate_from_config(self, config: dict[str, Any]) -> dict[str, Any]:
        family = config["family"]
        if family == "int_eval_batch":
            return self._generate_eval_batch(config)
        if family == "int_temperature_story":
            return self._generate_temperature_story(config)
        if family == "int_net_change_story":
            return self._generate_net_change_story(config)
        if family == "int_guessing_game_score":
            return self._generate_guessing_game_score(config)
        if family == "int_exam_score":
            return self._generate_exam_score(config)
        if family == "int_dice_walk":
            return self._generate_dice_walk(config)
        if family == "int_compare_pairs":
            return self._generate_compare_pairs(config)
        if family == "int_truth_claim":
            return self._generate_truth_claim(config)
        if family == "int_special_multiplier":
            return self._generate_special_multiplier(config)
        raise ValueError(f"Unsupported integer family: {family}")

    def _extract_expr_templates(self, text: str) -> list[ExprTemplate]:
        exprs = re.findall(r"\$([^$]+)\$", text)
        if not exprs:
            bare = str(text or "").strip()
            if self._looks_like_bare_expression(bare):
                exprs = [bare]
        templates: list[ExprTemplate] = []
        for expr in exprs:
            py_expr = self._pythonize(expr)
            values = self._extract_values(py_expr)
            if not values:
                continue
            templates.append(
                ExprTemplate(
                    original=expr,
                    skeleton=self._build_skeleton(py_expr),
                    values=values,
                )
            )
        return templates

    def _extract_values(self, py_expr: str) -> list[int]:
        return [int(m.group(0)) for m in self._NUMBER_TOKEN_RE.finditer(py_expr)]

    def _build_skeleton(self, py_expr: str) -> str:
        idx = 0

        def repl(_: re.Match[str]) -> str:
            nonlocal idx
            slot = f"__N{idx}__"
            idx += 1
            return slot

        return self._NUMBER_TOKEN_RE.sub(repl, py_expr)

    def _instantiate_expr(self, skeleton: str, values: list[int]) -> str:
        out = skeleton
        for idx, original in enumerate(values):
            value = self._randomized_like(original)
            out = out.replace(f"__N{idx}__", str(value), 1)
        return out

    def _instantiate_template(self, template: ExprTemplate) -> tuple[str, str, str]:
        original_py = self._pythonize(template.original)
        original_rendered = template.original

        if "\\frac" in template.original:
            return original_py, original_rendered, str(_safe_eval_integer(original_py))

        if "/" in template.skeleton:
            for _ in range(80):
                candidate = self._instantiate_expr(template.skeleton, template.values)
                try:
                    answer = str(_safe_eval_integer(candidate))
                    return candidate, self._display_from_python_expr(candidate), answer
                except Exception:
                    continue
            return original_py, original_rendered, str(_safe_eval_integer(original_py))

        candidate = self._instantiate_expr(template.skeleton, template.values)
        return candidate, self._display_from_python_expr(candidate), str(_safe_eval_integer(candidate))

    def _randomized_like(self, original: int) -> int:
        if original == 0:
            return 0
        if abs(original) == 1:
            magnitude = random.randint(1, 9)
        else:
            magnitude = random.randint(2, max(12, abs(original) + 4))
        return magnitude if original > 0 else -magnitude

    def _display_from_python_expr(self, expr: str) -> str:
        disp_parts: list[str] = []
        i = 0
        while i < len(expr):
            if expr.startswith("abs(", i):
                inner, next_i = _consume_parenthesized(expr, i + 3)
                disp_parts.append(f"|{self._display_from_python_expr(inner)}|")
                i = next_i
                continue
            if expr.startswith("**", i):
                disp_parts.append("^")
                i += 2
                continue
            if expr[i] == "*":
                disp_parts.append("\\times")
                i += 1
                continue
            if expr[i] == "/":
                disp_parts.append("\\div")
                i += 1
                continue
            disp_parts.append(expr[i])
            i += 1
        return "".join(disp_parts)

    def _generate_eval_batch(self, config: dict[str, Any]) -> dict[str, Any]:
        rendered_exprs: list[str] = []
        answers: list[str] = []
        for raw in config["expressions"]:
            template = ExprTemplate(**raw)
            _, rendered, answer = self._instantiate_template(template)
            rendered_exprs.append(rendered)
            answers.append(answer)

        if "$" in config["source_text"]:
            question_text = _replace_math_segments(config["source_text"], rendered_exprs)
        elif len(rendered_exprs) == 1:
            question_text = f"計算 ${rendered_exprs[0]}$ 的值。"
        else:
            question_text = config["source_text"]
        correct_answer = answers[0] if len(answers) == 1 else "；".join(
            f"{i + 1}:{ans}" for i, ans in enumerate(answers)
        )
        return {
            "question_text": question_text,
            "answer": correct_answer,
            "correct_answer": correct_answer,
            "mode": 1,
        }

    def _extract_special_multiplier_config(self, source_text: str) -> dict[str, Any] | None:
        exprs = re.findall(r"\$([^$]+)\$", source_text)
        if not exprs:
            bare = str(source_text or "").strip()
            if self._looks_like_bare_expression(bare):
                exprs = [bare]
        if len(exprs) != 1:
            return None

        expr = exprs[0]
        py_expr = self._pythonize(expr)
        m = re.fullmatch(r"(\(?-?\d+\)?)\*(\(?-?\d+\)?)", py_expr)
        if not m:
            return None

        left_raw, right_raw = m.group(1), m.group(2)
        left = int(left_raw.strip("()"))
        right = int(right_raw.strip("()"))

        if abs(left) in self._SPECIAL_MULTIPLIER_BASES:
            special_side = "left"
            special_value = left
            normal_value = right
        elif abs(right) in self._SPECIAL_MULTIPLIER_BASES:
            special_side = "right"
            special_value = right
            normal_value = left
        else:
            return None

        base, delta = self._SPECIAL_MULTIPLIER_BASES[abs(special_value)]
        return {
            "family": "int_special_multiplier",
            "source_text": source_text,
            "special_side": special_side,
            "special_value": special_value,
            "normal_value": normal_value,
            "base": base,
            "delta": delta,
        }

    def _randomized_special_multiplier(self, special_value: int, base: int, delta: int) -> int:
        sign = -1 if special_value < 0 else 1
        if base == 125 and delta == 0:
            return sign * 125
        return sign * (base + delta)

    def _randomized_special_partner(self, original: int, special_abs: int) -> int:
        sign = -1 if original < 0 else 1
        if special_abs == 125:
            magnitude = random.choice([16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 136, 144, 152, 160,
                                       168, 176, 184, 192, 200, 208, 216, 224, 232, 240, 248, 256, 264, 272, 280, 288, 296, 304])
        else:
            low = max(12, min(abs(original), 999) // 2)
            high = max(low + 5, min(max(abs(original) + 60, 80), 999))
            magnitude = random.randint(low, high)
        return sign * magnitude

    def _generate_special_multiplier(self, config: dict[str, Any]) -> dict[str, Any]:
        special_value = self._randomized_special_multiplier(
            config["special_value"], config["base"], config["delta"]
        )
        partner = self._randomized_special_partner(config["normal_value"], abs(special_value))

        def _atom(n: int) -> str:
            return f"({n})" if n < 0 else str(n)

        if config["special_side"] == "left":
            expr = f"{_atom(special_value)}*{_atom(partner)}"
        else:
            expr = f"{_atom(partner)}*{_atom(special_value)}"

        rendered = self._display_from_python_expr(expr)
        answer = str(_safe_eval_integer(expr))
        source_text = str(config.get("source_text") or "")
        if "$" in source_text:
            question_text = _replace_math_segments(source_text, [rendered])
        else:
            question_text = f"計算 ${rendered}$ 的值。"
        return {
            "question_text": question_text,
            "answer": answer,
            "correct_answer": answer,
            "mode": 1,
        }

    def _generate_temperature_story(self, config: dict[str, Any]) -> dict[str, Any]:
        src = config["source_text"]
        if "先調高" in src or "先調低" in src:
            first = random.randint(2, 9)
            second = random.randint(2, 8)
            if "先調高" in src and "再調低" in src:
                question = f"小妍將冷氣先調高 {first} 度，再調低 {second} 度，溫度總變化為幾度？"
                answer = str(first - second)
            else:
                question = f"小妍將冷氣先調低 {first} 度，再調高 {second} 度，溫度總變化為幾度？"
                answer = str(-first + second)
            return {"question_text": question, "answer": answer, "correct_answer": answer, "mode": 1}

        if "高溫比低溫高了多少" in src:
            hot = random.randint(36, 41)
            cold = -random.randint(10, 20)
            question = (
                f"臺灣的氣溫紀錄中，某地出現過 {hot}°C 的高溫；"
                f"另一地出現過 {cold}°C 的低溫。請問這兩個溫度中，高溫比低溫高了多少 °C？"
            )
            answer = str(hot - cold)
            return {"question_text": question, "answer": answer, "correct_answer": answer, "mode": 1}

        start = random.choice([-14, -7, -5, 6, 12])
        end = random.choice([-18, -10, -8, 3, 5, 9])
        while end == start:
            end = random.choice([-18, -10, -8, 3, 5, 9])
        question = (
            f"冷凍庫原為{self._temp_phrase(start)}，調整之後溫度變成{self._temp_phrase(end)}，"
            "則溫度變化為多少？"
        )
        answer = str(end - start)
        return {"question_text": question, "answer": answer, "correct_answer": answer, "mode": 1}

    def _generate_net_change_story(self, config: dict[str, Any]) -> dict[str, Any]:
        src = config["source_text"]
        if "衣服" in src and "回收箱" in src:
            gain = random.randint(2, 5)
            lose = random.randint(2, 6)
            question = (
                f"媽媽買了 {gain} 件新衣服給皓云，皓云又拿了 {lose} 件太小的衣服投入舊衣回收箱，"
                "皓云衣服的總數變化為幾件？"
            )
            answer = str(gain - lose)
        else:
            send = random.randint(2, 5)
            take = random.randint(2, 6)
            question = (
                f"爸爸拿 {send} 件衣服送洗，又從洗衣店領回 {take} 件上次洗的衣服，"
                "爸爸可換穿衣服的總數變化為幾件？"
            )
            answer = str(-send + take)
        return {"question_text": question, "answer": answer, "correct_answer": answer, "mode": 1}

    def _generate_guessing_game_score(self, config: dict[str, Any]) -> dict[str, Any]:
        total = 9
        win_a = random.randint(2, 5)
        win_b = random.randint(1, 4)
        draw = total - win_a - win_b
        if draw < 0:
            draw = 1
            win_b = total - win_a - draw
        score_a = win_a * 3 + win_b * (-2) + draw
        score_b = win_b * 3 + win_a * (-2) + draw
        question = (
            "小妍與小美玩猜拳遊戲，得分與扣分方式如下：贏 +3 分，輸 -2 分，平手 +1 分。"
            f"已知兩人共猜了 {total} 次拳，其中小妍贏 {win_a} 次，小美贏 {win_b} 次，平手 {draw} 次，"
            "分別求出兩人最後的分數為何？"
        )
        answer = f"小妍：{score_a}；小美：{score_b}"
        return {"question_text": question, "answer": answer, "correct_answer": answer, "mode": 1}

    def _generate_exam_score(self, config: dict[str, Any]) -> dict[str, Any]:
        total = 25
        wrong = random.randint(3, 6)
        blank = random.randint(2, 5)
        correct = total - wrong - blank
        score = correct * 4 - wrong
        question = (
            f"某次數學測驗共考 {total} 題選擇題，答對 1 題得 4 分，答錯 1 題倒扣 1 分，不作答則不給分。"
            f"已知小羅在此次測驗中答錯 {wrong} 題，剩下最後 {blank} 題沒有作答，其餘皆正確，求小羅此次測驗的成績為何？"
        )
        answer = str(score)
        return {"question_text": question, "answer": answer, "correct_answer": answer, "mode": 1}

    def _generate_dice_walk(self, config: dict[str, Any]) -> dict[str, Any]:
        throws = 10
        even = random.randint(2, 6)
        odd = throws - even
        position = even * 5 - odd * 4
        question = (
            "小翊投擲一顆點數為 1、2、3、4、5、6 的骰子，並將一個棋子放在數線上，依照下列規則移動。"
            "擲出偶數點：棋子往數線右方移動 5 個單位；"
            "擲出奇數點：棋子往數線左方移動 4 個單位。"
            f"已知小翊一開始將棋子放在原點，共投擲了 {throws} 次，其中出現 {even} 次偶數點，則棋子最後的位置在哪個坐標上？"
        )
        answer = str(position)
        return {"question_text": question, "answer": answer, "correct_answer": answer, "mode": 1}

    def _generate_compare_pairs(self, config: dict[str, Any]) -> dict[str, Any]:
        rendered: list[str] = []
        answers: list[str] = []
        for left_src, right_src in config["pairs"]:
            left_py = self._instantiate_expr(self._build_skeleton(self._pythonize(left_src)), self._extract_values(self._pythonize(left_src)))
            right_py = self._instantiate_expr(self._build_skeleton(self._pythonize(right_src)), self._extract_values(self._pythonize(right_src)))
            rendered.append(f"${self._display_from_python_expr(left_py)}$ 和 ${self._display_from_python_expr(right_py)}$")
            answers.append("相同" if _safe_eval_integer(left_py) == _safe_eval_integer(right_py) else "不相同")

        lines = [f"⑴ {rendered[0]}"]
        for idx, item in enumerate(rendered[1:], start=2):
            lines.append(f"⑵ {item}" if idx == 2 else f"({idx}) {item}")
        question = "比較下列各題中，兩式的運算結果是否相同。\n" + "\n".join(lines)
        answer = "；".join(f"{idx + 1}:{value}" for idx, value in enumerate(answers))
        return {"question_text": question, "answer": answer, "correct_answer": answer, "mode": 1}

    def _generate_truth_claim(self, config: dict[str, Any]) -> dict[str, Any]:
        src = config["source_text"]
        compact = _normalize_compact(src)
        if "5＋a" in src or "5+a" in compact:
            question = "關於「如果 a 是一個整數，那麼 5＋a 一定比 5 大！」的敘述，你認為說法正確嗎？為什麼？"
            answer = "不正確；當 a 是 0 或負整數時，5＋a 不一定比 5 大。"
        elif "減法運算中，有沒有交換律和結合律" in src:
            question = "整數的加法運算有交換律和結合律，那麼整數的減法運算中，有沒有交換律和結合律呢？請舉例說明。"
            answer = "沒有；例如 6－2 不等於 2－6，可知沒有交換律，且 (8－3)－1 不等於 8－(3－1)，可知沒有結合律。"
        elif "除法運算中，有沒有交換律和結合律" in src:
            question = "整數的乘法運算有交換律和結合律，那麼整數的除法運算中，有沒有交換律和結合律呢？請舉例說明。"
            answer = "沒有；例如 12÷3 不等於 3÷12，可知沒有交換律，且 (24÷6)÷2 不等於 24÷(6÷2)，可知沒有結合律。"
        elif "－( a－b )＝b－a" in src or "-(a-b)=b-a" in compact:
            question = "「若 a、b 為整數，則 －( a－b )＝b－a」這個說法是否正確？"
            answer = "正確"
        elif "減法運算中，有交換律和結合律" in src:
            question = "「整數的減法運算中，有交換律和結合律」這個說法是否正確？"
            answer = "不正確"
        elif "相反數的中點坐標為 0" in src:
            question = "「任意兩相反數的中點坐標為 0」這個說法是否正確？"
            answer = "正確"
        elif "相等嗎" in src and src.count("$") >= 2:
            exprs = re.findall(r"\$([^$]+)\$", src)
            left = _safe_eval_integer(self._pythonize(exprs[0]))
            right = _safe_eval_integer(self._pythonize(exprs[1]))
            question = src
            answer = "相同" if left == right else "不相同"
        else:
            question = src
            answer = "不正確"
        return {"question_text": question, "answer": answer, "correct_answer": answer, "mode": 1}

    def _extract_compare_pairs(self, text: str) -> list[tuple[str, str]]:
        segments = re.findall(r"\$([^$]+)\$", text)
        return [(segments[i], segments[i + 1]) for i in range(0, len(segments) - 1, 2)]

    def _pythonize(self, expr: str) -> str:
        s = str(expr or "")
        s = s.replace("（", "(").replace("）", ")")
        s = s.replace("＋", "+").replace("－", "-")
        s = s.replace("×", "*").replace("÷", "/")
        s = s.replace("｜", "|")
        s = s.replace("\\left", "").replace("\\right", "")
        s = s.replace("\\times", "*").replace("\\div", "/")
        s = re.sub(r"(?i)\btimes\b", "*", s)
        s = re.sub(r"(?i)\bdiv\b", "/", s)
        s = s.replace("×", "*").replace("÷", "/")
        s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", s)
        s = s.replace("[", "(").replace("]", ")")
        s = s.replace(" ", "")
        s = re.sub(r"\|([^|]+)\|", r"abs(\1)", s)
        return s

    def _looks_like_exam_score(self, text: str) -> bool:
        return all(keyword in text for keyword in ("答對", "答錯", "倒扣", "不作答"))

    def _looks_like_dice_walk(self, text: str) -> bool:
        return all(keyword in text for keyword in ("骰子", "偶數", "奇數", "原點"))

    def _looks_like_guessing_game_score(self, text: str) -> bool:
        return all(keyword in text for keyword in ("猜拳", "贏", "輸", "平手"))

    def _looks_like_temperature_story(self, text: str) -> bool:
        return any(keyword in text for keyword in ("冷氣", "冷凍庫", "氣溫", "高溫比低溫高", "零下"))

    def _looks_like_net_change_story(self, text: str) -> bool:
        return "衣服" in text and ("總數變化" in text or "可換穿衣服的總數變化" in text)

    def _looks_like_comparison_pairs(self, text: str) -> bool:
        return "運算結果是否相同" in text and text.count("$") >= 4

    def _looks_like_truth_claim(self, text: str) -> bool:
        return any(
            key in text
            for key in (
                "你認為說法正確嗎",
                "這個說法是否正確",
                "有沒有交換律和結合律",
                "相等嗎",
                "是否正確",
            )
        )

    def _looks_like_bare_expression(self, text: str) -> bool:
        content = str(text or "").strip()
        if not content:
            return False
        normalized = content
        normalized = normalized.replace("\\left", "").replace("\\right", "")
        normalized = normalized.replace("\\times", "*").replace("\\div", "/")
        normalized = re.sub(r"(?i)\btimes\b", "*", normalized)
        normalized = re.sub(r"(?i)\bdiv\b", "/", normalized)
        normalized = normalized.replace("×", "*").replace("÷", "/")
        if re.search(r"[A-Za-z\u4e00-\u9fff]", normalized):
            return False
        return bool(re.fullmatch(r"[\d\-\+\*/\(\)\[\]\{\}\|\\\s]+", normalized))

    def _temp_phrase(self, value: int) -> str:
        if value < 0:
            return f"零下 {abs(value)} 度"
        return f"{value} 度"
