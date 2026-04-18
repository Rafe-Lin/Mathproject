import random
import math
import ast # For safe evaluation of user input

# Helper function to format a matrix for LaTeX display
def _format_matrix_latex(matrix):
    rows_str = []
    for row in matrix:
        # Format elements: if float, show 2 decimal places, otherwise just string
        formatted_row = []
        for x in row:
            if isinstance(x, float):
                formatted_row.append(f"{x:.2f}")
            else:
                formatted_row.append(str(x))
        rows_str.append(" & ".join(formatted_row))
    return r"\begin{{pmatrix}}" + r" \\ ".join(rows_str) + r"\end{{pmatrix}}"

# Helper function for matrix multiplication
def _matrix_multiply(A, B):
    # A is m x n, B is n x p. Result is m x p
    m = len(A)
    n = len(A[0])
    p = len(B[0]) # Assuming B is n x p

    if n != len(B):
        raise ValueError("Matrix dimensions mismatch for multiplication")

    result = [[0 for _ in range(p)] for _ in range(m)]

    for i in range(m):
        for j in range(p):
            current_sum = 0
            for k in range(n):
                current_sum += A[i][k] * B[k][j]
            result[i][j] = current_sum
    return result

def generate(level=1):
    """
    生成「矩陣與數據表格」相關題目。
    包含：
    1. 將數據資料轉換為矩陣形式
    2. 矩陣加法 (處理類似數據的合併)
    3. 矩陣乘法 (處理更複雜的數據分析，如總銷售額、總成本)
    """
    problem_type_choices = []
    if level == 1:
        problem_type_choices.append('data_to_matrix')
        problem_type_choices.append('matrix_addition')
    elif level == 2:
        problem_type_choices.append('matrix_multiplication_integer') # 整數值矩陣乘法
    elif level >= 3:
        problem_type_choices.append('matrix_multiplication_decimal') # 包含小數值的矩陣乘法

    problem_type = random.choice(problem_type_choices)

    if problem_type == 'data_to_matrix':
        return generate_data_to_matrix_problem()
    elif problem_type == 'matrix_addition':
        return generate_matrix_addition_problem()
    elif problem_type == 'matrix_multiplication_integer':
        return generate_matrix_multiplication_problem(use_decimals=False)
    elif problem_type == 'matrix_multiplication_decimal':
        return generate_matrix_multiplication_problem(use_decimals=True)

def generate_data_to_matrix_problem():
    """
    題型：將文字描述的數據轉換為矩陣形式。
    """
    products = random.sample(['蘋果', '香蕉', '橘子', '梨子', '奇異果'], k=2)
    days = ['星期一', '星期二', '星期三']
    sales_data = {}
    for day in days:
        sales_data[day] = {}
        for product in products:
            sales_data[day][product] = random.randint(10, 50)

    question_text = f"某水果店連續三天銷售 {products[0]} 和 {products[1]} 的數量如下：<br>"
    for day in days:
        question_text += f"{day}: {products[0]} 售出 {sales_data[day][products[0]]} 顆, {products[1]} 售出 {sales_data[day][products[1]]} 顆。<br>"
    question_text += f"請將以上銷售資料表示為一個 ${{3 \\times 2}}$ 的矩陣，其中列代表日期 ({', '.join(days)})，行代表產品 ({', '.join(products)})。<br>"
    question_text += f"請以 Python 列表的列表格式輸入，例如 [[row1_col1, row1_col2], [row2_col1, row2_col2], ...]]"

    correct_matrix = []
    for day in days:
        correct_matrix.append([sales_data[day][products[0]], sales_data[day][products[1]]])
    correct_answer = str(correct_matrix) 

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_matrix_addition_problem():
    """
    題型：計算兩個數據矩陣的和。
    """
    rows = random.randint(2, 3)
    cols = random.randint(2, 3)
    
    matrix1 = [[random.randint(5, 30) for _ in range(cols)] for _ in range(rows)]
    matrix2 = [[random.randint(5, 30) for _ in range(cols)] for _ in range(rows)]

    result_matrix = [[matrix1[i][j] + matrix2[i][j] for j in range(cols)] for i in range(rows)]

    row_labels = random.sample(['A店', 'B店', 'C店', 'D店', 'E店'], k=rows)
    col_labels = random.sample(['產品X', '產品Y', '產品Z', '產品W', '產品V'], k=cols)
    period1_name = random.choice(['上午', '第一週', '春季'])
    period2_name = random.choice(['下午', '第二週', '夏季'])
    
    question_text = f"某商店 {period1_name} 的銷售數量矩陣 $M_{{1}}$ 和 {period2_name} 的銷售數量矩陣 $M_{{2}}$ 如下：<br>"
    question_text += f"$M_{{1}} = {_format_matrix_latex(matrix1)}$<br>"
    question_text += f"$M_{{2}} = {_format_matrix_latex(matrix2)}$<br>"
    question_text += f"請計算總銷售數量矩陣 $M_{{total}} = M_{{1}} + M_{{2}}$。<br>"
    question_text += f"請以 Python 列表的列表格式輸入，例如 [[row1_col1, row1_col2], [row2_col1, row2_col2], ...]]"

    correct_answer = str(result_matrix)
    
    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": correct_answer
    }

def generate_matrix_multiplication_problem(use_decimals=False):
    """
    題型：利用矩陣乘法計算總銷售額或總成本。
    use_decimals: 若為 True，則價格/成本包含小數。
    """
    scenario_type = random.choice(['revenue', 'cost'])
    
    if scenario_type == 'revenue':
        m = random.randint(2, 3) # 實體數量 (e.g., 分店數量)
        n = random.randint(2, 3) # 項目數量 (e.g., 產品種類)
        
        # 數量矩陣 (m x n)
        matrix_Q = [[random.randint(10, 80) for _ in range(n)] for _ in range(m)]
        
        # 單價矩陣 (n x 1)
        if use_decimals:
            matrix_P = [[random.randint(10, 100) / 10.0 for _ in range(1)] for _ in range(n)]
        else:
            matrix_P = [[random.randint(1, 15) for _ in range(1)] for _ in range(n)]

        # 標籤
        entity_labels = random.sample(['總店', '分店A', '分店B', '分店C', '分店D'], k=m)
        item_labels = random.sample(['筆記本', '原子筆', '立可帶', '便利貼', '文件夾'], k=n)
        
        question_text = f"某文具店銷售多種產品。下表顯示不同分店的銷售數量，以及各產品的單價。<br>"
        question_text += f"數量矩陣 $Q$ (列:分店 - {', '.join(entity_labels)}, 行:產品 - {', '.join(item_labels)}):<br>"
        question_text += f"$Q = {_format_matrix_latex(matrix_Q)}$<br>"
        question_text += f"單價矩陣 $P$ (列:產品 - {', '.join(item_labels)}, 行:單價):<br>"
        question_text += f"$P = {_format_matrix_latex(matrix_P)}$<br>"
        question_text += f"請計算每個分店的總銷售額矩陣 $R = QP$。<br>"
        question_text += f"請以 Python 列表格式輸入結果矩陣 $R$ (例如 [val1, val2, ...])。"
        
        result_matrix_raw = _matrix_multiply(matrix_Q, matrix_P)
        # 將結果扁平化並四捨五入到小數點後兩位，以便比較
        correct_answer_list = [round(row[0], 2) for row in result_matrix_raw] 
        correct_answer = str(correct_answer_list)
        
    else: # scenario_type == 'cost'
        m = random.randint(2, 3) # 實體數量 (e.g., 食譜種類)
        n = random.randint(2, 3) # 項目數量 (e.g., 原料種類)
        
        # 原料份量矩陣 (m x n)
        matrix_M = [[random.randint(5, 100) for _ in range(n)] for _ in range(m)]
        
        # 單位成本矩陣 (n x 1)
        if use_decimals:
            matrix_C = [[random.randint(1, 20) / 10.0 for _ in range(1)] for _ in range(n)]
        else:
            matrix_C = [[random.randint(1, 10) for _ in range(1)] for _ in range(n)]

        # 標籤
        entity_labels = random.sample(['蛋糕', '餅乾', '麵包', '派'], k=m)
        item_labels = random.sample(['麵粉', '糖', '奶油', '雞蛋', '牛奶'], k=n)

        question_text = f"某烘焙坊製作不同點心。下表為每份點心所需的原料份量，以及每份原料的成本。<br>"
        question_text += f"原料份量矩陣 $M$ (列:點心 - {', '.join(entity_labels)}, 行:原料 - {', '.join(item_labels)}):<br>"
        question_text += f"$M = {_format_matrix_latex(matrix_M)}$<br>"
        question_text += f"單位成本矩陣 $C$ (列:原料 - {', '.join(item_labels)}, 行:成本):<br>"
        question_text += f"$C = {_format_matrix_latex(matrix_C)}$<br>"
        question_text += f"請計算每份點心的總成本矩陣 $R = MC$。<br>"
        question_text += f"請以 Python 列表格式輸入結果矩陣 $R$ (例如 [val1, val2, ...])。"

        result_matrix_raw = _matrix_multiply(matrix_M, matrix_C)
        # 將結果扁平化並四捨五入到小數點後兩位，以便比較
        correct_answer_list = [round(row[0], 2) for row in result_matrix_raw]
        correct_answer = str(correct_answer_list)

    return {
        "question_text": question_text,
        "answer": correct_answer, 
        "correct_answer": correct_answer
    }

def check(user_answer, correct_answer):
    """
    檢查使用者輸入的矩陣答案是否正確。
    支援列表 (向量) 或列表的列表 (矩陣) 形式的答案。
    會進行浮點數的近似比較。
    """
    is_correct = False
    result_text = ""

    try:
        user_val = ast.literal_eval(user_answer.strip())
        correct_val = ast.literal_eval(correct_answer.strip())

        # 將單一數值答案轉換為列表，以便統一處理 (雖然此技能的答案通常是列表或列表的列表)
        if not isinstance(user_val, list):
            user_val = [user_val]
        if not isinstance(correct_val, list):
            correct_val = [correct_val]

        if len(user_val) != len(correct_val):
            is_correct = False
        else:
            all_elements_match = True
            for i in range(len(user_val)):
                if isinstance(user_val[i], list) and isinstance(correct_val[i], list):
                    # 比較矩陣的行 (巢狀列表)
                    if len(user_val[i]) != len(correct_val[i]):
                        all_elements_match = False
                        break
                    for j in range(len(user_val[i])):
                        # 浮點數比較
                        if not math.isclose(float(user_val[i][j]), float(correct_val[i][j]), rel_tol=1e-5, abs_tol=1e-9):
                            all_elements_match = False
                            break
                    if not all_elements_match:
                        break
                elif not isinstance(user_val[i], list) and not isinstance(correct_val[i], list):
                    # 比較向量的元素 (扁平列表)
                    # 浮點數比較
                    if not math.isclose(float(user_val[i]), float(correct_val[i]), rel_tol=1e-5, abs_tol=1e-9):
                        all_elements_match = False
                        break
                else: # 類型不匹配 (例如，一個是列表，另一個是數值)
                    all_elements_match = False
                    break
            is_correct = all_elements_match
        
    except (ValueError, SyntaxError, TypeError):
        is_correct = False
        result_text = "輸入格式錯誤。請確保輸入為有效的 Python 列表或列表的列表，例如 [[1, 2], [3, 4]] 或 [100, 200]。"

    if is_correct:
        result_text = f"完全正確！答案是 ${correct_answer}$。"
    elif "輸入格式錯誤" not in result_text: # 如果已經有格式錯誤訊息，則不再覆蓋
        result_text = f"答案不正確。正確答案應為：${correct_answer}$。"
        
    return {"correct": is_correct, "result": result_text, "next_question": True}