
import requests
import json

# 設定 API URL
BASE_URL = 'http://127.0.0.1:5000'

# 模擬登入
def login(username, password):
    session = requests.Session()
    response = session.post(f'{BASE_URL}/login', data={'username': username, 'password': password})
    if response.status_code == 200:
        print(f"登入成功: {username}")
        return session
    else:
        print(f"登入失敗: {response.text}")
        return None

# 模擬答錯並檢查是否記錄錯誤
def test_mistake_logging(session):
    # 1. 獲取題目 (假設 skill 為 'remainder')
    response = session.get(f'{BASE_URL}/get_next_question?skill=remainder')
    if response.status_code != 200:
        print("獲取題目失敗")
        return

    data = response.json()
    question_text = data.get('new_question_text')
    print(f"獲取題目: {question_text}")

    # 2. 提交錯誤答案
    wrong_answer = "這是一個錯誤的答案"
    print(f"提交錯誤答案: {wrong_answer}")
    
    check_response = session.post(f'{BASE_URL}/check_answer', json={'answer': wrong_answer})
    check_data = check_response.json()
    
    print(f"批改結果: {check_data}")
    
    if not check_data.get('correct'):
        print("系統判定為錯誤 (預期結果)")
        
        # 3. 檢查是否有 AI 分析結果
        mistake_analysis = check_data.get('mistake_analysis')
        if mistake_analysis:
            print("收到 AI 錯誤分析:")
            print(json.dumps(mistake_analysis, indent=2, ensure_ascii=False))
        else:
            print("警告: 未收到 AI 錯誤分析")
    else:
        print("系統判定為正確 (非預期結果)")

if __name__ == "__main__":
    # 請確保資料庫中有此使用者，或先註冊
    # 這裡假設 admin 已經存在
    session = login('admin', 'admin123')
    if session:
        test_mistake_logging(session)
