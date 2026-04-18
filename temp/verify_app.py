
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())
os.environ['GEMINI_API_KEY'] = 'dummy_key'

try:
    from app import app
    print("App imported successfully.")
    
    # Check if the new route is registered
    found = False
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}, Rule: {rule}")
        if rule.endpoint == 'core.import_textbook_examples':
            found = True
    
    if found:
        print("Verification SUCCESS: Route 'core.import_textbook_examples' is registered.")
    else:
        print("Verification FAILED: Route 'core.import_textbook_examples' NOT found.")
        sys.exit(1)

except Exception as e:
    print(f"Verification FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
