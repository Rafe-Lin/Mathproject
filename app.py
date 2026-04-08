# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): app.py
功能說明 (Description): Flask 應用程式的主要進入點，負責初始化應用程式、註冊路由、設定資料庫連線、以及整合身分驗證與 AI 模組。
執行語法 (Usage): python app.py
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
# app.py
import pandas as pd
import re
from sqlalchemy.orm import aliased
import sys
import os

# Windows 主控台常為 cp950：請求流程中的 log 若含 emoji 會 UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# =========================================================
# [新增] 強制路徑修正：解決 No module named 'core'
# 這段程式碼必須放在所有 'from core ...' 之前
# =========================================================
# 取得 app.py 所在的絕對路徑 (即專案根目錄)
basedir = os.path.abspath(os.path.dirname(__file__))

# 如果這個路徑不在 Python 的搜尋清單中，將其插入到第一順位
if basedir not in sys.path:
    sys.path.insert(0, basedir)

# 確認 core 資料夾路徑也被加入 (雙重保險)
core_dir = os.path.join(basedir, 'core')
if os.path.exists(core_dir) and basedir not in sys.path:
     sys.path.insert(0, basedir)
# =========================================================
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
from matplotlib import font_manager
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import inspect, Table, MetaData, text, func
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from core.routes import core_bp
from core.ai_analyzer import configure_gemini
from core.rag_engine import init_rag
from core.advanced_rag_engine import init_adv_rag
from config import Config
from models import init_db, User, db, Progress, SkillInfo, SkillCurriculum, SkillPrerequisites
from core.utils import get_all_active_skills

def _prepare_skill_data_from_record(record):
    """從字典記錄中準備並清理 SkillInfo 的資料。"""
    skill_id = str(record['skill_id']).strip()
    return {
        'skill_id': skill_id,
        'skill_en_name': record.get('skill_en_name'),
        'skill_ch_name': record.get('skill_ch_name'),
        'category': record.get('category'),
        'description': record.get('description'),
        'input_type': record.get('input_type', 'text'),
        'gemini_prompt': record.get('gemini_prompt'),
        'consecutive_correct_required': int(record.get('consecutive_correct_required', 10)),
        'is_active': str(record.get('is_active', 'true')).lower() == 'true',
        'order_index': int(record.get('order_index', 999))
    }

login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # --- Matplotlib Font Settings for Chinese Characters ---
    # This is a common path for Windows. If deploying on another OS, this path might need to be changed.
    try:
        font_path = 'C:/Windows/Fonts/msjhl.ttc'
        if os.path.exists(font_path):
            font_manager.fontManager.addfont(font_path)
            available_fonts = {f.name for f in font_manager.fontManager.ttflist}
            if 'Microsoft JhengHei' in available_fonts:
                plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'DejaVu Sans']
            elif 'Microsoft JhengHei UI' in available_fonts:
                plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei UI', 'DejaVu Sans']
            else:
                plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        else:
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False  # Fix for displaying the minus sign
    except Exception as e:
        app.logger.warning(f"Could not set Chinese font: {e}")
    # --- End Font Settings ---

    # 載入設定
    app.config.update(
        SQLALCHEMY_DATABASE_URI=Config.SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=Config.SQLALCHEMY_TRACK_MODIFICATIONS,
        SECRET_KEY=Config.SECRET_KEY,
        GEMINI_API_KEY=Config.GEMINI_API_KEY,
        GEMINI_MODEL_NAME=Config.GEMINI_MODEL_NAME
        ,SQLALCHEMY_ENGINE_OPTIONS={
            "connect_args": {"timeout": 30}  # 增加等待解鎖的時間到 30 秒
        }
    )    

    # 只有在真的要用 Gemini 時才檢查
    if app.config.get('AI_PROVIDER') == 'gemini' and not app.config.get('GEMINI_API_KEY'):
        raise ValueError("Gemini 模式請設定 GEMINI_API_KEY 環境變數！")

    # 初始化擴充套件
    db.init_app(app)
    login_manager.init_app(app)

    # 註冊藍圖
    from core.routes import practice_bp, live_show_bp # 導入新的 blueprint
    # 修改：移除 url_prefix，讓 API 路由可以直接使用 /api/skills/...
    # 而 admin 頁面路由已經在 routes.py 中定義為 /admin/...
    app.register_blueprint(core_bp)
    app.register_blueprint(practice_bp) # 註冊練習用的 blueprint，沒有前綴
    app.register_blueprint(live_show_bp) # 註冊科展展演用的 blueprint

    # [模擬學生 API] 註冊模擬學生 blueprint（本地開發用）
    try:
        from Simulated_student.sim_api import sim_bp
        app.register_blueprint(sim_bp)
    except ImportError:
        pass  # Simulated_student 套件未安裝時不影響主程式
    
    # [隱藏路由清單輸出] 暫時註解掉以減少干擾
    # print("--- 目前系統註冊的所有路由清單 ---")
    # print(app.url_map)

    # === 路由定義 ===
    # 將所有路由定義移至工廠函式內部

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role', 'student') # 獲取身分，預設為學生
            
            user = db.session.query(User).filter_by(username=username).first()

            if user and check_password_hash(user.password_hash, password):
                # 檢查身分是否相符
                if user.role != role:
                    flash(f'身分錯誤！此帳號為「{user.role}」帳號，請切換身分後再試。', 'warning')
                    return redirect(url_for('login'))

                login_user(user)
                
                # 根據身分導向不同頁面
                if user.role == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            flash('帳號或密碼錯誤', 'danger')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role', 'student') # 獲取身分

            if len(password) < 4:
                flash('密碼至少 4 個字', 'warning')
                return redirect(url_for('register'))

            if db.session.query(User).filter_by(username=username).first():
                flash('帳號已存在', 'warning')
                return redirect(url_for('register'))

            new_user = User(
                username=username,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
                role=role # 儲存身分
            )
            db.session.add(new_user)
            db.session.commit()
            flash(f'註冊成功！身分：{role}。請登入', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('已登出', 'info')
        return redirect(url_for('login'))

    @app.route('/teacher_dashboard')
    @login_required
    def teacher_dashboard():
        if current_user.role != 'teacher':
            flash('權限不足，無法存取教師頁面', 'warning')
            return redirect(url_for('dashboard'))
        return render_template('teacher_dashboard.html', username=current_user.username)

    @app.route('/teacher/analysis')
    @login_required
    def teacher_analysis():
        if current_user.role != 'teacher':
            flash('權限不足，無法存取教師頁面', 'warning')
            return redirect(url_for('dashboard'))

        # 1. 取得錯題排行榜 (最多人做錯的題目)
        # 統計 MistakeLog 中，相同的 question_content 出現的次數
        from models import MistakeLog, LearningDiagnosis, User  # 確保導入模型
        
        top_mistakes = db.session.query(
            MistakeLog.question_content,
            func.count(MistakeLog.id).label('count')
        ).group_by(MistakeLog.question_content)\
        .order_by(text('count DESC'))\
        .limit(10).all()

        # 整理成 Chart.js 需要的格式
        mistake_labels = []
        mistake_data = []
        for q_content, count in top_mistakes:
            # 截斷過長的題目文字以利顯示
            display_text = q_content[:20] + "..." if len(q_content) > 20 else q_content
            mistake_labels.append(display_text)
            mistake_data.append(count)

        # 2. 取得學生學習診斷分析結果
        # 關聯 User 表以獲取學生姓名
        diagnoses = db.session.query(LearningDiagnosis, User.username)\
            .join(User, LearningDiagnosis.student_id == User.id)\
            .order_by(LearningDiagnosis.created_at.desc())\
            .all()

        return render_template('teacher_analysis.html', 
                               username=current_user.username,
                               mistake_labels=mistake_labels,
                               mistake_data=mistake_data,
                               diagnoses=diagnoses)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # --- 修改點：允許教師訪問學生儀表板 ---
        # 原本會將教師重導向，現在註解掉此邏輯，讓教師可以查看學生介面。
        # if current_user.role == 'teacher':
        #     return redirect(url_for('teacher_dashboard'))

        # 取得學生已加入的班級
        enrolled_classes = current_user.enrolled_classes if current_user.is_authenticated and hasattr(current_user, 'enrolled_classes') else []

        view_mode = request.args.get('view', 'curriculum')
        curriculum = request.args.get('curriculum', 'junior_high')
        volume = request.args.get('volume')
        chapter = request.args.get('chapter')
        
        progress_records = db.session.query(Progress).filter_by(user_id=current_user.id).all()
        progress_dict = {
            p.skill_id: (p.skill_id, p.consecutive_correct, p.questions_solved, p.current_level)
            for p in progress_records
        }
        
        if view_mode == 'curriculum':
            from core.utils import get_volumes_by_curriculum, get_chapters_by_curriculum_volume, get_skills_by_volume_chapter
            
            if curriculum:
                session['current_curriculum'] = curriculum

            if curriculum and volume and chapter:
                skills_raw = get_skills_by_volume_chapter(volume, chapter)

                all_skills_with_progress = []
                for s in skills_raw:
                    prog = progress_dict.get(s['skill_id'], (s['skill_id'], 0, 0, 1))
                    all_skills_with_progress.append({
                        **s,
                        'consecutive_correct': prog[1],
                        'questions_solved': prog[2],
                        'current_level': prog[3],
                    })

                sections_map = {}
                for skill in all_skills_with_progress:
                    section_name = skill['section']
                    if section_name not in sections_map:
                        sections_map[section_name] = {'section': section_name, 'skills': []}
                    sections_map[section_name]['skills'].append(skill)
                
                
                grouped_sections = list(sections_map.values())
                
                # [Fix] 對 sections 進行自然排序
                def natural_keys(text):
                    """
                    將字串拆解為數字與文字部分，以實現自然排序
                    例如: "1-10" -> ['', 1, '-', 10, '']
                    """
                    if not text:
                        return []
                    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(text))]
                
                grouped_sections.sort(key=lambda x: natural_keys(x['section']))


                return render_template('dashboard.html',
                                     view_mode='curriculum',
                                     level='skills',
                                     curriculum=curriculum,
                                     volume=volume,
                                     chapter=chapter,
                                     grouped_sections=grouped_sections,
                                     username=current_user.username,
                                     enrolled_classes=enrolled_classes)
            elif curriculum and volume:
                chapters = get_chapters_by_curriculum_volume(curriculum, volume)
                return render_template('dashboard.html',
                                     view_mode='curriculum',
                                     level='chapters',
                                     curriculum=curriculum,
                                     volume=volume,
                                     chapters=chapters,
                                     username=current_user.username,
                                     enrolled_classes=enrolled_classes)
            elif curriculum:
                volumes = get_volumes_by_curriculum(curriculum)

                # 新增：針對國中冊別的排序邏輯
                if curriculum == 'junior_high':
                    desired_order_jh = {
                        '數學1上': 0, '數學1下': 1, '數學2上': 2, '數學2下': 3, '數學3上': 4, '數學3下': 5
                    }
                    for grade in volumes:
                        volumes[grade].sort(key=lambda vol: desired_order_jh.get(vol, 99))

                if 11 in volumes:
                    desired_order_g11 = {
                        '數學3A': 0, '數學4A': 1,
                        '數學3B': 2, '數學4B': 3
                    }
                    volumes[11].sort(key=lambda vol: desired_order_g11.get(vol, 99))

                if 12 in volumes:
                    desired_order = {
                        '數學甲(上)': 0, '數學甲(下)': 1,
                        '數學乙(上)': 2, '數學乙(下)': 3,
                        '數學3A': 4, '數學3B': 5
                    }
                    volumes[12].sort(key=lambda vol: desired_order.get(vol, 99))

                if curriculum == 'junior_high':
                    grade_map = {
                        7: '七年級', 8: '八年級', 9: '九年級'
                    }
                else:
                    grade_map = {
                        10: '一年級', 11: '二年級', 12: '三年級'
                    }

                return render_template('dashboard.html',
                                     view_mode='curriculum',
                                     level='volumes',
                                     curriculum=curriculum,
                                     volumes=volumes,
                                     grade_map=grade_map,
                                     username=current_user.username,
                                     enrolled_classes=enrolled_classes)
        else:
            selected_category = request.args.get('category')

            if selected_category:
                skills = db.session.query(SkillInfo).filter_by(is_active=True, category=selected_category).order_by(SkillInfo.order_index).all()
                
                dashboard_data = []
                for skill in skills:
                    prog = progress_dict.get(skill.skill_id, (skill.skill_id, 0, 0, 1))
                    dashboard_data.append({
                        'skill': skill,
                        'consecutive_correct': prog[1],
                        'questions_solved': prog[2],
                        'current_level': prog[3]
                    })
                
                return render_template('dashboard.html', 
                                     dashboard_data=dashboard_data,
                                     view_mode='all',
                                     level='skills_in_category',
                                     category=selected_category,
                                     username=current_user.username,
                                     enrolled_classes=enrolled_classes)
            else:
                ordered_categories_query = db.session.query(SkillInfo.category)\
                    .join(SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id)\
                    .filter(SkillCurriculum.curriculum == 'general', SkillInfo.is_active == True)\
                    .order_by(SkillCurriculum.grade, SkillCurriculum.display_order)\
                    .all()
                
                desired_order_list = []
                seen_categories = set()
                for row in ordered_categories_query:
                    category = row[0]
                    if category and category not in seen_categories:
                        desired_order_list.append(category)
                        seen_categories.add(category)
                
                all_category_rows = db.session.query(SkillInfo.category).filter(SkillInfo.is_active == True).distinct().all()
                categories = [row[0] for row in all_category_rows if row[0]]
                
                order_map = {category: index for index, category in enumerate(desired_order_list)}
                categories.sort(key=lambda cat: order_map.get(cat, 999))
                
                return render_template('dashboard.html',
                                     view_mode='all',
                                     level='categories',
                                     categories=categories,
                                     username=current_user.username,
                                     enrolled_classes=enrolled_classes)

    with app.app_context():
        init_db(db.engine)
        # 啟用 WAL (Write-Ahead Logging) 模式以提高併發性並減少鎖定
        try:
            with db.engine.connect() as conn:
                # 啟用 WAL 模式，允許讀取和寫入並行
                conn.execute(text("PRAGMA journal_mode=WAL"))
                # 設定同步等級為 NORMAL，在 WAL 模式下是安全且高效的選擇
                conn.execute(text("PRAGMA synchronous=NORMAL"))
        except Exception as e:
            app.logger.error(f"Failed to set WAL mode for SQLite: {e}")

        if os.environ.get('SEED_DB_ONLY') != '1':
            configure_gemini(
                api_key=app.config['GEMINI_API_KEY'],
                model_name=app.config['GEMINI_MODEL_NAME']
            )
            try:
                init_rag(app)
            except Exception as e:
                app.logger.error(f"RAG initialization failed: {e}")
                
            try:
                init_adv_rag(app)
            except Exception as e:
                app.logger.error(f"Advanced RAG initialization failed: {e}")

    return app

app = create_app()

if __name__ == '__main__':
    # 加入 use_reloader=False 以防止寫入檔案時伺服器自動重啟
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host=host, port=port, use_reloader=False)
