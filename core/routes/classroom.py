# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/routes/classroom.py
功能說明 (Description): 班級與學生管理模組，包含教師建立班級、學生加入班級 (Join Class)、Excel 批次匯入學生、邀請碼管理與班級列表查詢功能。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

from flask import request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
import pandas as pd

from . import core_bp
from models import db, Class, ClassStudent, User, generate_invitation_code

# ==========================================
# Teacher Routes (教師端功能)
# ==========================================

@core_bp.route('/classes/create', methods=['POST'])
@login_required
def create_class():
    """建立新班級"""
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403
    
    try:
        data = request.get_json()
        class_name = data.get('name')
        
        if not class_name:
            return jsonify({"success": False, "message": "請輸入班級名稱"}), 400
            
        new_class = Class(
            name=class_name,
            teacher_id=current_user.id
        )
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "班級建立成功",
            "class": new_class.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"建立班級失敗: {e}")
        return jsonify({"success": False, "message": "建立班級失敗"}), 500

@core_bp.route('/classes/regenerate_code/<int:class_id>', methods=['POST'])
@login_required
def regenerate_class_code(class_id):
    """重新產生班級邀請碼"""
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        target_class = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not target_class:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        target_class.class_code = generate_invitation_code()
        db.session.commit()
        
        return jsonify({"success": True, "new_code": target_class.class_code})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"重新產生代碼失敗: {e}")
        return jsonify({"success": False, "message": "產生新代碼失敗"}), 500

@core_bp.route('/classes/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    """刪除班級"""
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403
        
    try:
        target_class = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not target_class:
            return jsonify({"success": False, "message": "找不到班級或無權限刪除"}), 404
            
        db.session.delete(target_class)
        db.session.commit()
        
        return jsonify({"success": True, "message": "班級已刪除"})
    except Exception as e:
        current_app.logger.error(f"刪除班級失敗: {e}")
        return jsonify({"success": False, "message": "刪除班級失敗"}), 500

@core_bp.route('/api/teacher/classes')
@login_required
def get_teacher_classes():
    """獲取教師的所有班級"""
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403
        
    try:
        classes = db.session.query(Class).filter_by(teacher_id=current_user.id).order_by(Class.created_at.desc()).all()
        return jsonify({
            "success": True,
            "classes": [c.to_dict() for c in classes]
        })
    except Exception as e:
        current_app.logger.error(f"獲取班級列表失敗: {e}")
        return jsonify({"success": False, "message": "獲取班級列表失敗"}), 500

# ==========================================
# Student Management (學生管理)
# ==========================================

@core_bp.route('/api/classes/<int:class_id>/students', methods=['GET'])
@login_required
def get_class_students(class_id):
    """獲取班級內所有學生"""
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        class_obj = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not class_obj:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        students = db.session.query(User).join(ClassStudent).filter(ClassStudent.class_id == class_id).all()
        
        return jsonify({
            "success": True,
            "students": [{
                "id": s.id,
                "username": s.username,
                "role": s.role,
                "created_at": s.created_at.strftime('%Y-%m-%d')
            } for s in students]
        })

    except Exception as e:
        current_app.logger.error(f"獲取學生列表失敗: {e}")
        return jsonify({"success": False, "message": "獲取學生列表失敗"}), 500

@core_bp.route('/class/add_student/<int:class_id>', methods=['POST'])
@login_required
def add_student_to_class(class_id):
    """新增單一學生到班級 (若學生不存在則自動建立帳號)"""
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({"success": False, "message": "請輸入帳號與密碼"}), 400

        # 確認班級存在且屬於該教師
        target_class = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not target_class:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        # 檢查學生是否已存在
        student = db.session.query(User).filter_by(username=username).first()

        if not student:
            # 建立新學生帳號
            student = User(
                username=username,
                password_hash=generate_password_hash(password),
                role='student'
            )
            db.session.add(student)
            db.session.flush() # 取得 ID
        else:
            # 學生已存在，檢查是否已在班級中
            is_member = db.session.query(ClassStudent).filter_by(class_id=class_id, student_id=student.id).first()
            if is_member:
                return jsonify({"success": False, "message": "該學生已經在班級中了"}), 400
        
        # 加入班級
        new_member = ClassStudent(class_id=class_id, student_id=student.id)
        db.session.add(new_member)
        db.session.commit()

        return jsonify({"success": True, "message": "新增學生成功"})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"新增學生失敗: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@core_bp.route('/api/classes/<int:class_id>/students/upload', methods=['POST'])
@login_required
def upload_students_excel(class_id):
    """Excel 批次匯入學生"""
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "權限不足"}), 403

    try:
        class_obj = db.session.query(Class).filter_by(id=class_id, teacher_id=current_user.id).first()
        if not class_obj:
            return jsonify({"success": False, "message": "找不到班級或無權限"}), 404

        if 'file' not in request.files:
            return jsonify({"success": False, "message": "未上傳檔案"}), 400

        file = request.files['file']
        if file.filename == '' or not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({"success": False, "message": "請上傳 Excel 檔案"}), 400

        df = pd.read_excel(file, header=None)
        if df.shape[1] < 2:
            return jsonify({"success": False, "message": "格式錯誤：需包含帳號與密碼欄位"}), 400

        stats = {"total": 0, "added": 0, "skipped": 0, "failed": 0, "errors": []}

        for index, row in df.iterrows():
            try:
                username = str(row[0]).strip()
                password = str(row[1]).strip()
                if index == 0 and any(x in username.lower() for x in ['account', 'username', '帳號']):
                    continue # Skip header
                if not username or not password or pd.isna(row[0]) or pd.isna(row[1]):
                    continue

                stats["total"] += 1
                existing_user = db.session.query(User).filter_by(username=username).first()
                
                if existing_user:
                    in_class = db.session.query(ClassStudent).filter_by(class_id=class_id, student_id=existing_user.id).first()
                    if not in_class:
                        db.session.add(ClassStudent(class_id=class_id, student_id=existing_user.id))
                        stats["added"] += 1
                    else:
                        stats["skipped"] += 1
                else:
                    new_student = User(username=username, password_hash=generate_password_hash(password), role='student')
                    db.session.add(new_student)
                    db.session.flush()
                    db.session.add(ClassStudent(class_id=class_id, student_id=new_student.id))
                    stats["added"] += 1

            except Exception as row_error:
                stats["failed"] += 1
                stats["errors"].append(f"Row {index+1}: {row_error}")
                continue

        db.session.commit()
        return jsonify({"success": True, "message": f"處理完成。新增: {stats['added']}, 略過: {stats['skipped']}", "stats": stats})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"匯入學生失敗: {e}")
        return jsonify({"success": False, "message": f"匯入失敗: {str(e)}"}), 500

@core_bp.route('/class/join', methods=['POST'])
@login_required
def join_class():
    """學生輸入代碼加入班級"""
    if current_user.role != 'student':
        flash('只有學生才能加入班級。', 'warning')
        return redirect(url_for('core.dashboard'))

    class_code = request.form.get('class_code', '').strip()
    target_class = db.session.query(Class).filter_by(class_code=class_code).first()

    if not target_class:
        flash('無效的班級代碼。', 'danger')
        return redirect(url_for('core.dashboard'))

    is_member = db.session.query(ClassStudent).filter_by(class_id=target_class.id, student_id=current_user.id).first()
    if is_member:
        flash(f'您已經在「{target_class.name}」班級中了。', 'info')
    else:
        try:
            db.session.add(ClassStudent(class_id=target_class.id, student_id=current_user.id))
            db.session.commit()
            flash(f'成功加入班級：「{target_class.name}」！', 'success')
        except:
            db.session.rollback()
            flash('加入失敗，請重試。', 'danger')

    return redirect(url_for('core.dashboard'))