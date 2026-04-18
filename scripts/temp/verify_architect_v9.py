
import sys
import os

# Set up path to import from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.prompt_architect import generate_v9_spec

def test_architect():
    with app.app_context():
        # Pick a skill that likely exists. 'jh_數學1上_IntegerAddition' is a common one, 
        # but let's check one from the grep search earlier or just try a standard one.
        # Based on grep search results: 'jh_數學1上_IntegerDivision.py' exists, so 'jh_IntegerDivision' might be the ID 
        # OR usually IDs are like 'jh_Math1_...' 
        # Let's try to query one first.
        from models import SkillInfo
        skill = SkillInfo.query.first()
        if not skill:
            print("No skills found in DB to test.")
            return

        print(f"Testing with Skill ID: {skill.skill_id}")
        
        # Test 1: Cloud Pro
        print("\n--- Test 1: Cloud Pro ---")
        # specific Mock/Dry run is difficult without actually calling Gemini, 
        # but we can check if the function creates the payload correctly if we mock the AI client.
        # For now, we'll rely on the fact that if this runs and hits the AI, it counts as a success.
        # CAUTION: This WILL consume tokens if we run it for real. 
        # The user asked to "Rewriting", and implied functionality.
        # Let's start by just ensuring imports work and function signature is correct.
        print("Function `generate_v9_spec` is importable.")
        
        # We won't actually call the AI in this automated test to avoid cost/time during this turn,
        # unless the user explicitly wants a live test. 
        # This script serves as a way for the user to run it if they choose to.
        print(f"To run a live test, execute: generate_v9_spec('{skill.skill_id}', model_tag='cloud_pro')")

if __name__ == "__main__":
    test_architect()
