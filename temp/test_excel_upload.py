import pandas as pd
import io
from app import app, db
from models import User, Class, ClassStudent
from werkzeug.security import generate_password_hash

def test_upload():
    print("Starting test_upload...")
    with app.app_context():
        # 1. Create a test teacher
        teacher_username = 'test_teacher_upload'
        teacher = db.session.query(User).filter_by(username=teacher_username).first()
        if not teacher:
            print(f"Creating teacher {teacher_username}...")
            teacher = User(
                username=teacher_username,
                password_hash=generate_password_hash('password'),
                role='teacher'
            )
            db.session.add(teacher)
            db.session.commit()
        else:
            print(f"Teacher {teacher_username} exists.")
        
        # 2. Create a test class
        class_name = 'Test Upload Class'
        test_class = db.session.query(Class).filter_by(name=class_name).first()
        if not test_class:
            print(f"Creating class {class_name}...")
            test_class = Class(name=class_name, teacher_id=teacher.id, class_code='TEST001')
            db.session.add(test_class)
            db.session.commit()
        else:
            print(f"Class {class_name} exists.")
            
        # 3. Create dummy Excel file
        # We simulate a file with a header row and 2 student rows
        data = [
            ['Account', 'Password'],
            ['student_upload_1', 'pass1'],
            ['student_upload_2', 'pass2']
        ]
        df = pd.DataFrame(data)
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False, header=False)
        excel_file.seek(0)

        # 4. Login and Upload
        client = app.test_client()
        print("Logging in...")
        login_resp = client.post('/login', data={'username': teacher_username, 'password': 'password', 'role': 'teacher'})
        if login_resp.status_code != 302: # Should redirect on success
             # Check if login failed (maybe already logged in? No, test client is fresh)
             # Wait, app.py login returns redirect.
             pass
        
        print("Uploading Excel file...")
        response = client.post(
            f'/api/classes/{test_class.id}/students/upload',
            data={'file': (excel_file, 'students.xlsx')},
            content_type='multipart/form-data'
        )
        
        print(f"Response status: {response.status_code}")
        json_data = response.get_json()
        print(f"Response JSON: {json_data}")
        
        # 5. Verify
        if response.status_code == 200 and json_data['success']:
            print("Upload successful!")
            stats = json_data['stats']
            if stats['added'] >= 2: # Might be 0 if they already exist from previous run
                print("Stats check passed.")
            else:
                print(f"Stats check: Added {stats['added']} (Expected 2 if fresh run)")
        else:
            print("Upload failed!")
            exit(1)

        # 6. Check DB
        s1 = db.session.query(User).filter_by(username='student_upload_1').first()
        s2 = db.session.query(User).filter_by(username='student_upload_2').first()
        
        if s1 and s2:
            print("Database check passed: Students found.")
            # Check if they are in the class
            cs1 = db.session.query(ClassStudent).filter_by(class_id=test_class.id, student_id=s1.id).first()
            cs2 = db.session.query(ClassStudent).filter_by(class_id=test_class.id, student_id=s2.id).first()
            if cs1 and cs2:
                print("Class membership check passed.")
            else:
                print("Class membership check FAILED.")
        else:
            print("Database check FAILED: Students not found.")

        # Cleanup (Optional)
        # db.session.delete(test_class)
        # db.session.delete(teacher)
        # if s1: db.session.delete(s1)
        # if s2: db.session.delete(s2)
        # db.session.commit()
        # print("Cleanup done.")

if __name__ == '__main__':
    test_upload()
