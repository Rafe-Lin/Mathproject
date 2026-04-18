import random

# --- 資料庫 ---
# 定義各種立體圖形的結構與其中文描述
# 座標系：x: 向右, y: 向後, z: 向上
SHAPES = {
    'L型-1': {
        'description': '一個由5個正方體組成的立體圖形。<br>結構為：底層排成一行3個方塊，並在最左邊方塊的後方疊上1個方塊，最左邊方塊的上方也疊上1個方塊。',
        'views': {
            '前': '底層有3個方塊，第二層最左邊有1個方塊。',
            '後': '底層有3個方塊，第二層最右邊有1個方塊。',
            '右': '底層有2個方塊，第二層在左邊有1個方塊。',
            '左': '底層有2個方塊，第二層在右邊有1個方塊。',
            '上': '一個由4個方塊組成的L形。'
        }
    },
    'T型': {
        'description': '一個由5個正方體組成的立體圖形。<br>結構為：底層排成一行3個方塊，並在中間方塊的後方疊上1個方塊，中間方塊的上方也疊上1個方塊。',
        'views': {
            '前': '底層有3個方塊，第二層在中間有1個方塊。',
            '後': '底層有3個方塊，第二層在中間有1個方塊。',
            '右': '底層有2個方塊，第二層在左邊有1個方塊。',
            '左': '底層有2個方塊，第二層在右邊有1個方塊。',
            '上': '一個由4個方塊組成的T形。'
        }
    },
    '十字型': {
        'description': '一個由5個正方體組成的立體圖形。<br>結構為：底層排成一個十字形，並在正中央的方塊上方疊上1個方塊。',
        'views': {
            '前': '底層有3個方塊，第二層在中間有1個方塊。',
            '後': '底層有3個方塊，第二層在中間有1個方塊。',
            '右': '底層有3個方塊，第二層在中間有1個方塊。',
            '左': '底層有3個方塊，第二層在中間有1個方塊。',
            '上': '一個由5個方塊組成的十字形。'
        }
    },
    '階梯型': {
        'description': '一個由6個正方體組成的立體圖形。<br>結構為：共有三層，底層有3個方塊，中層有2個，頂層有1個，形成階梯狀。',
        'views': {
            '前': '一個3x3的階梯形，底層3塊，中層2塊，頂層1塊。',
            '後': '一個3x3的階梯形，底層3塊，中層2塊，頂層1塊。',
            '右': '一個高度為3的I形（3個方塊垂直堆疊）。',
            '左': '一個高度為3的I形（3個方塊垂直堆疊）。',
            '上': '一個3x3的正方形。'
        }
    }
}

def generate(level=1):
    """
    生成「三視圖」相關題目。
    包含：
    1. 繪製三視圖
    2. 依視圖判斷觀察方向
    """
    problem_type = random.choice(['describe_all_views', 'identify_view'])
    
    if problem_type == 'describe_all_views':
        return generate_describe_all_views_problem()
    else:
        return generate_identify_view_problem()

def generate_describe_all_views_problem():
    """
    題型：給定立體圖形描述，要求繪製或描述三視圖。
    """
    shape_name = random.choice(list(SHAPES.keys()))
    shape_info = SHAPES[shape_name]
    
    description = shape_info['description']
    
    question_text = f"一個由數個相同正方體堆疊成的立體圖形，其結構描述如下：<br>{description}<br>請繪製或寫出它的前視圖、上視圖、與右視圖的樣子。"
    
    front_view_desc = shape_info['views']['前']
    top_view_desc = shape_info['views']['上']
    right_view_desc = shape_info['views']['右']
    
    correct_answer = f"前視圖：${front_view_desc}<br>上視圖：${top_view_desc}<br>右視圖：${right_view_desc}"
    
    return {
        "question_text": question_text,
        "answer": correct_answer,  # The answer is a description, for handwriting comparison
        "correct_answer": correct_answer
    }

def generate_identify_view_problem():
    """
    題型：給定立體圖形與一個視圖，判斷觀察方向。
    """
    shape_name = random.choice(list(SHAPES.keys()))
    shape_info = SHAPES[shape_name]
    
    # 隨機選擇一個觀察方向
    possible_views = ['前', '後', '左', '右', '上']
    view_direction = random.choice(possible_views)
    
    # 取得對應的描述
    description = shape_info['description']
    view_prose = shape_info['views'][view_direction]
    
    # 生成題目
    persons = ['小明', '小華', '小嘉', '小莉', '小鈺']
    person = random.choice(persons)
    
    question_text = f"有一個立體圖形，其結構如下：<br>{description}<br>{person}從某個方向觀察，看到的圖形可以描述為：「{view_prose}」。<br>請問{person}最可能是從哪個方向觀察的？ (請填 前、後、左、右、上)"
    
    correct_answer = view_direction

    return {
        "question_text": question_text,
        "answer": correct_answer,
        "correct_answer": f"ID:${correct_answer}"  # 使用前綴來區分題型
    }

def check(user_answer, correct_answer):
    """
    檢查答案是否正確。
    - 對於「判斷方向」題，進行字串比對。
    - 對於「繪製視圖」題，由於是手寫，直接提供答案供使用者比對。
    """
    user_answer = user_answer.strip()

    if correct_answer.startswith("ID:"):
        # 此為「判斷方向」題
        actual_answer = correct_answer.replace("ID:", "").strip()
        is_correct = (user_answer == actual_answer)
        
        if is_correct:
            result_text = f"完全正確！答案是「{actual_answer}」。"
        else:
            result_text = f"答案不正確。正確答案應為：「{actual_answer}」。"
            
        return {"correct": is_correct, "result": result_text, "next_question": True}
    else:
        # 此為「繪製/描述視圖」題
        result_text = f"這是一題繪圖或描述題，答案沒有標準格式，請對照以下參考答案自行批改：<br>{correct_answer}"
        # 因為無法自動批改，所以預設為 True 讓使用者繼續下一題
        return {"correct": True, "result": result_text, "next_question": True}
