def generate(level=1, **kwargs):
    # 原題結構：8x-$(-5x)$ → 項數=2，運算符=1（減），無絕對值，有括號負數
    # 動態生成：保持 2 個數字，1 個減號，保留 (-x) 格式
    v1 = IntegerOps.random_nonzero(1, 100)  # 第一項：正數 [1,100]
    v2 = IntegerOps.random_nonzero(-12, -1) # 第二項：負數 [-12,-1]，確保為負數
    # 保持運算符為減，且不改變順序
    eval_str = f"{v1} - {v2}"
    math_str = f"{IntegerOps.fmt_num(v1)} - {IntegerOps.fmt_num(v2)}"
    ans = IntegerOps.safe_eval(eval_str)
    return (
        f"計算 ${math_str}$ 的值。",
        str(int(round(ans)))
    )

def check(user_answer, correct_answer):
    try:
        user_val = int(user_answer.strip())
        return user_val == int(correct_answer)
    except:
        return False