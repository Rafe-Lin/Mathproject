import sys
import os
import io

# Setup path to import app
sys.path.insert(0, os.getcwd())

# [Fix] Force UTF-8 encoding for Windows consoles
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from app import create_app, db
from models import User
from flask import session

def verify():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing
    
    with app.test_client() as client:
        print("--- [Verification] Instant Practice Mode ---")
        
        # 1. Login Mock
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'
            sess['_fresh'] = True
        
        # 2. Upload Image
        print("1. Uploading image to /practice/upload_instant...")
        data = {
            'image': (io.BytesIO(b"fake image data"), 'test.png')
        }
        
        # Mock core.ai_analyzer.analyze_question_image
        import core.ai_analyzer
        original_analyze = core.ai_analyzer.analyze_question_image
        
        def mock_analyze(file_obj):
            print("   [Mock] AI Analyze called.")
            return {
                "question_text": "Mock Question: 1+1=?",
                "correct_answer": "2",
                "predicted_topic": "Mock Topic",
                "image_base64": "", 
            }
        
        core.ai_analyzer.analyze_question_image = mock_analyze
        
        # Mock core.routes.analysis.get_chat_response (The one actually used by the route)
        import core.routes.analysis
        original_chat = core.routes.analysis.get_chat_response
        
        def mock_chat_response(prompt, image=None):
             # Check if our mock context is in the prompt
             found = "Mock Question" in prompt
             reply_msg = "Context found." if found else "Context NOT found."
             return {"reply": reply_msg + f" (Prompt len: {len(prompt)})", "follow_up_prompts": []}

        core.routes.analysis.get_chat_response = mock_chat_response

        try:
            response = client.post('/practice/upload_instant', data=data, content_type='multipart/form-data', follow_redirects=True)
            
            print(f"   Response Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.get_json()}")
                return
            
            # 3. Check Chat Context
            print("2. Checking Chat Context /chat_ai...")
            chat_payload = {"question": "How to solve?"}
            
            chat_resp = client.post('/chat_ai', json=chat_payload)
            print(f"   Chat Response: {chat_resp.get_json()}")
            
            resp_json = chat_resp.get_json()
            # We look for our Mock Question text in the prompt echo
            if "Context found." in resp_json.get('reply', ''):
                print("✅ SUCCESS: Chat AI received context.")
            else:
                print("❌ FAILURE: Chat AI did not receive context.")
                print(f"   Reply content: {resp_json.get('reply')}")

        finally:
            # Restore
            core.ai_analyzer.analyze_question_image = original_analyze
            core.routes.analysis.get_chat_response = original_chat

if __name__ == "__main__":
    verify()
