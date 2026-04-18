import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "http://127.0.0.1:5000"
SESSION = requests.Session()

def register_teacher(username, password):
    print(f"Registering teacher {username}...")
    resp = SESSION.post(f"{BASE_URL}/register", data={
        "username": username,
        "password": password,
        "role": "teacher"
    })
    if resp.url.endswith("/login"):
        print("Registration successful (redirected to login).")
        return True
    elif "帳號已存在" in resp.text:
        print("User already exists.")
        return True
    else:
        print(f"Registration failed. URL: {resp.url}")
        return False

def login(username, password):
    print(f"Logging in as {username}...")
    resp = SESSION.post(f"{BASE_URL}/login", data={
        "username": username,
        "password": password,
        "role": "teacher"
    })
    if resp.url.endswith("/teacher_dashboard"):
        print("Login successful.")
        return True
    else:
        print(f"Login failed. URL: {resp.url}")
        return False

def test_class_management():
    print("\n--- Testing Class Management ---")
    # 1. Create Class
    print("Creating class 'API Test Class'...")
    resp = SESSION.post(f"{BASE_URL}/classes/create", json={"name": "API Test Class"})
    data = resp.json()
    if data.get("success"):
        class_id = data["class"]["id"]
        print(f"Class created. ID: {class_id}")
    else:
        print(f"Class creation failed: {data}")
        return False

    # 2. Get Classes
    print("Fetching classes...")
    resp = SESSION.get(f"{BASE_URL}/api/teacher/classes")
    data = resp.json()
    classes = data.get("classes", [])
    found = any(c["id"] == class_id for c in classes)
    if found:
        print("Class found in list.")
    else:
        print("Class NOT found in list.")
        return False

    # 3. Delete Class
    print(f"Deleting class {class_id}...")
    resp = SESSION.post(f"{BASE_URL}/classes/delete/{class_id}")
    data = resp.json()
    if data.get("success"):
        print("Class deleted.")
    else:
        print(f"Class deletion failed: {data}")
        return False
    
    # 4. Verify Deletion
    resp = SESSION.get(f"{BASE_URL}/api/teacher/classes")
    classes = resp.json().get("classes", [])
    found = any(c["id"] == class_id for c in classes)
    if not found:
        print("Class successfully removed from list.")
    else:
        print("Class still present in list.")
        return False
        
    return True

def test_skill_management():
    print("\n--- Testing Skill Management ---")
    skill_id = "api_test_skill"
    
    # 1. Add Skill
    print(f"Adding skill {skill_id}...")
    # admin_add_skill expects form data
    data = {
        "skill_id": skill_id,
        "skill_en_name": "API Test Skill",
        "skill_ch_name": "API 測試單元",
        "category": "Test",
        "description": "Created via API verification script",
        "input_type": "text",
        "gemini_prompt": "Test Prompt",
        "consecutive_correct_required": 5,
        "is_active": "on",
        "order_index": 100
    }
    resp = SESSION.post(f"{BASE_URL}/admin/skills/add", data=data)
    # It redirects to admin_skills on success
    if resp.url.endswith("/admin/skills"):
        print("Skill added (redirected to skills page).")
    else:
        print(f"Skill addition failed. URL: {resp.url}")
        return False

    # 2. Verify Skill in List
    print("Verifying skill in list...")
    resp = SESSION.get(f"{BASE_URL}/admin/skills")
    if skill_id in resp.text:
        print(f"Skill {skill_id} found in page.")
    else:
        print(f"Skill {skill_id} NOT found in page.")
        return False

    # 3. Delete Skill
    print(f"Deleting skill {skill_id}...")
    resp = SESSION.post(f"{BASE_URL}/admin/skills/delete/{skill_id}")
    if resp.url.endswith("/admin/skills"):
        print("Skill deleted.")
    else:
        print(f"Skill deletion failed. URL: {resp.url}")
        return False

    # 4. Verify Deletion
    resp = SESSION.get(f"{BASE_URL}/admin/skills")
    if skill_id not in resp.text:
        print(f"Skill {skill_id} successfully removed from page.")
    else:
        print(f"Skill {skill_id} still present in page.")
        return False

    return True

if __name__ == "__main__":
    try:
        if register_teacher("teacher_api", "password"):
            if login("teacher_api", "password"):
                class_result = test_class_management()
                skill_result = test_skill_management()
                
                if class_result and skill_result:
                    print("\nALL TESTS PASSED!")
                else:
                    print("\nSOME TESTS FAILED.")
    except Exception as e:
        print(f"An error occurred: {e}")
