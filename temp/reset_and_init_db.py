from app import app, db

with app.app_context():
    print("--- Step 1: Dropping all tables... ---")
    db.drop_all()
    print("--- Step 2: Creating all tables... ---")
    db.create_all()
    print("--- Database has been reset and initialized successfully! ---")
    print("--- You can now run 'python app.py' ---")
