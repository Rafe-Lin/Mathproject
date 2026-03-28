# -*- coding: utf-8 -*-
from __future__ import annotations

from skills.jh_數學1上_OperationsOnLinearExpressions import generate as _generate_main


def generate(level=1):
    return _generate_main(level=level, family_id="L2")


def check(user_answer, correct_answer):
    return str(user_answer).strip().replace(" ","") == str(correct_answer).strip().replace(" ","")
