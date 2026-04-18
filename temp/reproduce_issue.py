import sys
import os

# Add root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from core.code_generator import auto_generate_skill_code
from flask import current_app

def test():
    app = create_app()
    with app.app_context():
        skill_id = "jh_數學1上_PowersOfTen"
        print(f"Testing generation for {skill_id}...")
        try:
            result = auto_generate_skill_code(skill_id, queue=None)
            print(f"Result type: {type(result)}")
            print(f"Result value: {result}")
        except Exception as e:
            print(f"Exception caught during test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test()
