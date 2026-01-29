# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): models.py
功能說明 (Description): 定義系統的資料庫模型 (Schema)，包含使用者 (User)、技能 (Skill)、課綱架構 (Curriculum)、以及實驗記錄與錯誤日誌 (Logging)。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
# ==============================================================================
import sqlite3
import json
import secrets
import string
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# 建立 SQLAlchemy 實例
db = SQLAlchemy()

def init_db(engine):
    """
    初始化資料庫結構 (v9.0 Update)。
    包含新表格 skill_gencode_prompt 與 experiment_log 的新欄位。
    """
    conn = engine.raw_connection()
    c = conn.cursor()

    # --------------------------------------------------------
    # 1. 建立所有基礎表格
    # --------------------------------------------------------
    
    # Users, Progress, Skills Info ... (保持不變)
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, email TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, role TEXT DEFAULT 'student')''')
    c.execute('''CREATE TABLE IF NOT EXISTS progress (user_id INTEGER, skill_id TEXT, consecutive_correct INTEGER DEFAULT 0, consecutive_wrong INTEGER DEFAULT 0, current_level INTEGER DEFAULT 1, questions_solved INTEGER DEFAULT 0, last_practiced DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_id, skill_id), FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Skills Info (包含 suggested_prompts)
    c.execute('''
        CREATE TABLE IF NOT EXISTS skills_info (
            skill_id TEXT PRIMARY KEY, skill_en_name TEXT NOT NULL, skill_ch_name TEXT NOT NULL, category TEXT, description TEXT NOT NULL, input_type TEXT DEFAULT 'text', gemini_prompt TEXT NOT NULL, consecutive_correct_required INTEGER DEFAULT 10, is_active BOOLEAN DEFAULT TRUE, order_index INTEGER DEFAULT 0,
            suggested_prompt_1 TEXT, suggested_prompt_2 TEXT, suggested_prompt_3 TEXT
        )
    ''')

    # Skill Curriculum 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS skill_curriculum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            curriculum TEXT NOT NULL,
            grade INTEGER NOT NULL,
            volume TEXT NOT NULL,
            chapter TEXT NOT NULL,
            section TEXT NOT NULL,
            paragraph TEXT,
            display_order INTEGER DEFAULT 0,
            difficulty_level INTEGER DEFAULT 1,
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE,
            UNIQUE(curriculum, grade, volume, chapter, section, paragraph, skill_id, difficulty_level)
        )
    ''')

    # Skill Prerequisites 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS skill_prerequisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            prerequisite_id TEXT NOT NULL,
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE,
            FOREIGN KEY (prerequisite_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE,
            UNIQUE (skill_id, prerequisite_id)
        )
    ''')

    # Classes 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            teacher_id INTEGER NOT NULL,
            class_code TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')

    # Class Students 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS class_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(class_id, student_id)
        )
    ''')

    # Mistake Logs 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS mistake_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_id TEXT NOT NULL,
            question_content TEXT NOT NULL,
            user_answer TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            error_type TEXT,
            error_description TEXT,
            improvement_suggestion TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Exam Analysis 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS exam_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_id TEXT NOT NULL,
            curriculum TEXT,
            grade INTEGER,
            volume TEXT,
            chapter TEXT,
            section TEXT,
            is_correct BOOLEAN NOT NULL,
            error_type TEXT,
            confidence FLOAT,
            student_answer_latex TEXT,
            feedback TEXT,
            image_path TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id)
        )
    ''')

    # Mistake Notebook Entries 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS mistake_notebook_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            exam_image_path TEXT,
            question_data TEXT,
            notes TEXT,
            skill_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id)
        )
    ''')

    # Textbook Examples 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS textbook_examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            source_curriculum TEXT NOT NULL,
            source_volume TEXT NOT NULL,
            source_chapter TEXT NOT NULL,
            source_section TEXT NOT NULL,
            source_description TEXT NOT NULL,
            source_paragraph TEXT,
            problem_text TEXT NOT NULL,
            problem_type TEXT,
            correct_answer TEXT,
            detailed_solution TEXT,
            difficulty_level INTEGER DEFAULT 1,
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE
        )
    ''')

    # Learning Diagnosis 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_diagnosis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            radar_chart_data TEXT NOT NULL,
            ai_comment TEXT,
            recommended_unit TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')

    # System Settings 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            description TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # [v9.0 新增] Skill GenCode Prompt 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS skill_gencode_prompt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            architect_model TEXT DEFAULT 'human',
            model_tag TEXT DEFAULT 'default' NOT NULL,
            prompt_strategy TEXT DEFAULT 'standard',
            system_prompt TEXT,
            user_prompt_template TEXT,
            creation_prompt_tokens INTEGER DEFAULT 0,
            creation_completion_tokens INTEGER DEFAULT 0,
            creation_total_tokens INTEGER DEFAULT 0,
            version INTEGER DEFAULT 1,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            success_rate FLOAT DEFAULT 0.0,
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id)
        )
    ''')

    # [v9.0 更新] Experiment Log 表格 (包含所有新欄位)
    c.execute('''
        CREATE TABLE IF NOT EXISTS experiment_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            skill_id TEXT,
            ai_provider TEXT,
            model_name TEXT,
            duration_seconds REAL,
            input_length INTEGER,
            output_length INTEGER,
            is_success BOOLEAN DEFAULT 0,
            syntax_error_initial TEXT,
            ast_repair_triggered BOOLEAN DEFAULT 0,
            cpu_usage REAL,
            ram_usage REAL,
            experiment_batch TEXT,
            prompt_strategy TEXT,
            prompt_version INTEGER,
            error_category TEXT,
            regex_fix_count INTEGER DEFAULT 0,
            logic_fix_count INTEGER DEFAULT 0,
            ast_repair_count INTEGER DEFAULT 0,
            prompt_tokens INTEGER DEFAULT 0,
            completion_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            code_complexity INTEGER DEFAULT 0
        )
    ''')

    # [補上缺失] Questions 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            content TEXT NOT NULL,
            difficulty_level INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # [補上缺失] Quiz Attempts 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            user_answer TEXT,
            is_correct BOOLEAN DEFAULT 0,
            duration_seconds REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')

    # --------------------------------------------------------
    # 2. 自動升級邏輯：為舊資料庫補上新欄位
    # --------------------------------------------------------
    def add_column_if_not_exists(table, column, definition):
        try:
            c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not c.fetchone(): return
            c.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in c.fetchall()]
            if column not in columns:
                print(f"自動升級資料庫: 正在為 {table} 新增欄位 {column}")
                c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        except sqlite3.OperationalError: pass

    # Users
    add_column_if_not_exists('users', 'role', 'TEXT DEFAULT "student"')

    # Skills Info
    add_column_if_not_exists('skills_info', 'suggested_prompt_1', 'TEXT')
    add_column_if_not_exists('skills_info', 'suggested_prompt_2', 'TEXT')
    add_column_if_not_exists('skills_info', 'suggested_prompt_3', 'TEXT')

    # Experiment Log (v9.0 補丁)
    new_log_cols = [
        ('experiment_batch', 'TEXT'), ('prompt_strategy', 'TEXT'), ('prompt_version', 'INTEGER'),
        ('error_category', 'TEXT'),
        ('regex_fix_count', 'INTEGER DEFAULT 0'), ('logic_fix_count', 'INTEGER DEFAULT 0'), ('ast_repair_count', 'INTEGER DEFAULT 0'),
        ('prompt_tokens', 'INTEGER DEFAULT 0'), ('completion_tokens', 'INTEGER DEFAULT 0'), ('total_tokens', 'INTEGER DEFAULT 0'),
        ('code_complexity', 'INTEGER DEFAULT 0'),
        ('gpu_usage', 'REAL DEFAULT 0'), ('gpuram_usage', 'REAL DEFAULT 0'),
        ('raw_output_length', 'INTEGER DEFAULT 0'), ('perfect_utils_length', 'INTEGER DEFAULT 0')
    ]
    for col, definition in new_log_cols:
        add_column_if_not_exists('experiment_log', col, definition)

    # [v9.0 補丁] Skill GenCode Prompt 新增 architect_model
    add_column_if_not_exists('skill_gencode_prompt', 'architect_model', "TEXT DEFAULT 'human'")

    conn.commit()
    conn.close()
    print("資料庫結構初始化與檢查完成 (v9.0)！")

# --- 以下為 ORM 模型定義 (對應上述所有表格) ---

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_admin(self):
        return self.role == 'admin' or self.username in ['admin', 'testuser']

class Progress(db.Model):
    __tablename__ = 'progress'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    skill_id = db.Column(db.String, primary_key=True)
    consecutive_correct = db.Column(db.Integer, default=0)
    consecutive_wrong = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    questions_solved = db.Column(db.Integer, default=0)
    last_practiced = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('progress', lazy=True))

class SkillInfo(db.Model):
    __tablename__ = 'skills_info'
    skill_id = db.Column(db.String, primary_key=True)
    skill_en_name = db.Column(db.String, nullable=False)
    skill_ch_name = db.Column(db.String, nullable=False)
    category = db.Column(db.String)
    description = db.Column(db.String, nullable=False)
    input_type = db.Column(db.String, default='text')
    gemini_prompt = db.Column(db.String, nullable=False)
    consecutive_correct_required = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)
    # [新版對應] 新增三個提示詞欄位
    suggested_prompt_1 = db.Column(db.String, nullable=True)
    suggested_prompt_2 = db.Column(db.String, nullable=True)
    suggested_prompt_3 = db.Column(db.String, nullable=True)

    prerequisites = db.relationship(
        'SkillInfo',
        secondary='skill_prerequisites',
        primaryjoin='SkillInfo.skill_id == SkillPrerequisites.skill_id',
        secondaryjoin='SkillInfo.skill_id == SkillPrerequisites.prerequisite_id',
        backref=db.backref('subsequent_skills', lazy='dynamic')
    )

    def to_dict(self):
        return {
            'skill_id': self.skill_id,
            'skill_en_name': self.skill_en_name,
            'skill_ch_name': self.skill_ch_name,
            'category': self.category,
            'description': self.description,
            'input_type': self.input_type,
            'gemini_prompt': self.gemini_prompt,
            'consecutive_correct_required': self.consecutive_correct_required,
            'is_active': self.is_active,
            'order_index': self.order_index,
            'suggested_prompt_1': self.suggested_prompt_1,
            'suggested_prompt_2': self.suggested_prompt_2,
            'suggested_prompt_3': self.suggested_prompt_3
        }

class SkillGenCodePrompt(db.Model):
    __tablename__ = 'skill_gencode_prompt'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String(50), db.ForeignKey('skills_info.skill_id'), nullable=False)
    
    # [新增] 記錄這段 Prompt 是由誰設計的 (例如: 'human', 'gpt-4o', 'gemini-1.5-pro')
    architect_model = db.Column(db.String(50), default='human', nullable=False)

    # [模型分級策略]
    # 值範例: 'category:teacher', 'category:cloud_tutor', 'category:local_edge'
    model_tag = db.Column(db.String(50), default='default', nullable=False)
    
    # [提示策略]
    # 值範例: 'Architect-Engineer', 'CoT_Decomposed'
    prompt_strategy = db.Column(db.String(50), default='standard')
    
    # [內容核心]
    system_prompt = db.Column(db.Text)          # 系統角色設定
    user_prompt_template = db.Column(db.Text)   # 使用者指令模板 (架構師生成的 Spec)
    
    # [成本追蹤 - Architect Phase] (記錄生成此 Prompt 花費的 tokens)
    creation_prompt_tokens = db.Column(db.Integer, default=0)      # 輸入
    creation_completion_tokens = db.Column(db.Integer, default=0)  # 輸出
    creation_total_tokens = db.Column(db.Integer, default=0)       # 總計
    
    # [版本控制]
    version = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # [效能追蹤]
    success_rate = db.Column(db.Float, default=0.0)

    # 建立關聯
    skill = db.relationship('SkillInfo', backref=db.backref('gencode_prompts', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'model_tag': self.model_tag,
            'prompt_strategy': self.prompt_strategy,
            'version': self.version,
            'is_active': self.is_active
        }

class SkillCurriculum(db.Model):
    __tablename__ = 'skill_curriculum'
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)
    curriculum = db.Column(db.String, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.String, nullable=False)
    chapter = db.Column(db.String, nullable=False)
    section = db.Column(db.String, nullable=False)
    paragraph = db.Column(db.String)
    display_order = db.Column(db.Integer, default=0)
    difficulty_level = db.Column(db.Integer, default=1)
    skill_info = db.relationship('SkillInfo', backref=db.backref('curriculum_entries', lazy=True, cascade="all, delete-orphan"))
    __table_args__ = (db.UniqueConstraint('curriculum', 'grade', 'volume', 'chapter', 'section', 'paragraph', 'skill_id', 'difficulty_level', name='_curriculum_skill_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'curriculum': self.curriculum,
            'grade': self.grade,
            'volume': self.volume,
            'chapter': self.chapter,
            'section': self.section,
            'paragraph': self.paragraph,
            'display_order': self.display_order,
            'difficulty_level': self.difficulty_level
        }

class SkillPrerequisites(db.Model):
    __tablename__ = 'skill_prerequisites'
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)
    prerequisite_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)
    __table_args__ = (db.UniqueConstraint('skill_id', 'prerequisite_id', name='_skill_prerequisite_uc'),)

def generate_invitation_code(length=8):
    """產生一個隨機的、由大寫字母和數字組成的邀請碼"""
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(alphabet) for i in range(length))
        # 確保生成的代碼是唯一的
        if not Class.query.filter_by(class_code=code).first():
            return code

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_code = db.Column(db.String(8), unique=True, nullable=False, default=generate_invitation_code)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('teaching_classes', lazy=True))
    students = db.relationship('User', secondary='class_students', backref=db.backref('enrolled_classes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'class_code': self.class_code,
            'student_count': len(self.students),
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }


class ClassStudent(db.Model):
    __tablename__ = 'class_students'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class MistakeNotebookEntry(db.Model):
    __tablename__ = 'mistake_notebook_entries'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_image_path = db.Column(db.String(255), nullable=True)
    question_data = db.Column(db.JSON, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    skill_id = db.Column(db.String(50), db.ForeignKey('skills_info.skill_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('User', backref=db.backref('mistake_entries', lazy=True))
    skill = db.relationship('SkillInfo', backref=db.backref('mistake_entries', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'exam_image_path': self.exam_image_path,
            'question_data': self.question_data,
            'notes': self.notes,
            'skill_id': self.skill_id,
            'skill_name': self.skill.skill_ch_name if self.skill else '未分類',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

class MistakeLog(db.Model):
    __tablename__ = 'mistake_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.String, nullable=False)
    question_content = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    error_type = db.Column(db.String(50))
    error_description = db.Column(db.Text)
    improvement_suggestion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('mistakes', lazy=True))

class ExamAnalysis(db.Model):
    __tablename__ = 'exam_analysis'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id'), nullable=False)
    curriculum = db.Column(db.String)
    grade = db.Column(db.Integer)
    volume = db.Column(db.String)
    chapter = db.Column(db.String)
    section = db.Column(db.String)
    is_correct = db.Column(db.Boolean, nullable=False)
    error_type = db.Column(db.String)
    confidence = db.Column(db.Float)
    student_answer_latex = db.Column(db.Text)
    feedback = db.Column(db.Text)
    image_path = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('exam_analyses', lazy=True))
    skill_info = db.relationship('SkillInfo', backref=db.backref('exam_analyses', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_id': self.skill_id,
            'curriculum': self.curriculum,
            'grade': self.grade,
            'volume': self.volume,
            'chapter': self.chapter,
            'section': self.section,
            'is_correct': self.is_correct,
            'error_type': self.error_type,
            'confidence': self.confidence,
            'student_answer_latex': self.student_answer_latex,
            'feedback': self.feedback,
            'image_path': self.image_path,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class TextbookExample(db.Model):
    __tablename__ = 'textbook_examples'
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)
    source_curriculum = db.Column(db.String, nullable=False)
    source_volume = db.Column(db.String, nullable=False)
    source_chapter = db.Column(db.String, nullable=False)
    source_section = db.Column(db.String, nullable=False)
    source_description = db.Column(db.String, nullable=False)
    source_paragraph = db.Column(db.String)
    problem_text = db.Column(db.Text, nullable=False)
    problem_type = db.Column(db.String)
    correct_answer = db.Column(db.String)
    detailed_solution = db.Column(db.Text)
    difficulty_level = db.Column(db.Integer, default=1)
    skill_info = db.relationship('SkillInfo', backref=db.backref('textbook_examples', lazy=True, cascade="all, delete-orphan"))
    
    def to_dict(self):
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'source_curriculum': self.source_curriculum,
            'source_volume': self.source_volume,
            'source_chapter': self.source_chapter,
            'source_section': self.source_section,
            'source_description': self.source_description,
            'source_paragraph': self.source_paragraph,
            'problem_text': self.problem_text,
            'problem_type': self.problem_type,
            'correct_answer': self.correct_answer,
            'detailed_solution': self.detailed_solution,
            'difficulty_level': self.difficulty_level
        }

class LearningDiagnosis(db.Model):
    __tablename__ = 'learning_diagnosis'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    radar_chart_data = db.Column(db.Text, nullable=False)
    ai_comment = db.Column(db.Text)
    recommended_unit = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('User', backref=db.backref('learning_diagnoses', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'radar_chart_data': json.loads(self.radar_chart_data) if self.radar_chart_data else {},
            'ai_comment': self.ai_comment,
            'recommended_unit': self.recommended_unit,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

# [新增] ExperimentLog 模型 (科展實驗數據記錄)
class ExperimentLog(db.Model):
    """
    科展實驗數據記錄表
    用於記錄每一次 AI 生成的詳細效能指標與修復狀況
    """
    __tablename__ = 'experiment_log'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, comment="實驗時間")
    
    # --- 控制變因 ---
    skill_id = db.Column(db.String(64), comment="測試的技能ID")
    ai_provider = db.Column(db.String(20), comment="AI 引擎 (local/gemini)")
    model_name = db.Column(db.String(64), comment="模型版本")
    
    # --- 效能指標 ---
    duration_seconds = db.Column(db.Float, comment="生成耗時 (秒)")
    input_length = db.Column(db.Integer, comment="Prompt 字數")
    output_length = db.Column(db.Integer, comment="總 Code 字數 (含 Utils)")
    raw_output_length = db.Column(db.Integer, default=0, comment="AI 原始字數")
    perfect_utils_length = db.Column(db.Integer, default=0, comment="工具庫字數")
    is_success = db.Column(db.Boolean, default=False, comment="最終是否可用")
    syntax_error_initial = db.Column(db.Text, nullable=True, comment="原始語法錯誤訊息 (若無則空)")
    ast_repair_triggered = db.Column(db.Boolean, default=False, comment="是否觸發 AST 修復")
    


    # --- 系統資源 ---
    cpu_usage = db.Column(db.Float, nullable=True, comment="CPU 使用率 (%)")
    ram_usage = db.Column(db.Float, nullable=True, comment="RAM 使用率 (%)")
    gpu_usage = db.Column(db.Float, default=0.0, comment="GPU 使用率 (%)")
    gpuram_usage = db.Column(db.Float, default=0.0, comment="GPU RAM 使用率 (%)")

    # [v9.0 新增 - 實驗設定]
    experiment_batch = db.Column(db.String(50))    # 批次標籤 (如 'YS_Run_1')
    prompt_strategy = db.Column(db.String(50))     # 使用策略
    prompt_version = db.Column(db.Integer)         # 使用的 Prompt 版本 ID
    
    # [v9.0 新增 - 錯誤分析]
    error_category = db.Column(db.String(100))     # 錯誤分類 (SyntaxError, Timeout, etc.)
    
    # [v9.0 新增 - 自癒機制成效]
    regex_fix_count = db.Column(db.Integer, default=0)   # Regex 修復次數
    logic_fix_count = db.Column(db.Integer, default=0)   # Import 修復次數
    ast_repair_count = db.Column(db.Integer, default=0)  # AST 重構次數
    
    # [v9.0 新增 - 成本與複雜度 - Coder Phase]
    prompt_tokens = db.Column(db.Integer, default=0)      # 輸入 (Cost)
    completion_tokens = db.Column(db.Integer, default=0)  # 輸出 (Richness)
    total_tokens = db.Column(db.Integer, default=0)       # 總計
    code_complexity = db.Column(db.Integer, default=0)    # 生成程式碼的行數

    def __repr__(self):
        return f"<Log {self.model_name}: {self.duration_seconds}s, Success={self.is_success}>"

# [補上缺漏] 練習歷程紀錄相關表格
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String(50), nullable=False)
    content = db.Column(db.JSON, nullable=False)  # 儲存題目內容、選項、答案等
    difficulty_level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯
    attempts = db.relationship('QuizAttempt', backref='question', lazy=True)

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_answer = db.Column(db.String, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    duration_seconds = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯 (方便從 User 反查)
    user = db.relationship('User', backref=db.backref('quiz_attempts', lazy=True))

class StudentUploadedQuestion(db.Model):
    __tablename__ = 'student_uploaded_questions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Changed to Integer to match User.id type, allowed nullable for anonymous uploads if needed, or enforce. Assuming User.id is Int based on line 325
    # 預測的技能 ID (由 AI 初步判斷，可為 null)
    predicted_skill_id = db.Column(db.String(64), db.ForeignKey('skills_info.skill_id'), nullable=True)
    image_path = db.Column(db.String(255))
    ocr_content = db.Column(db.Text)  # 題目文字 (LaTeX)
    ai_solution = db.Column(db.Text)  # 詳解
    predicted_topic = db.Column(db.String(100)) # AI 歸納的主題名稱 (用於模糊比對)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # consistent with other models using utcnow
    
    student = db.relationship('User', backref=db.backref('uploaded_questions', lazy=True))
    skill_info = db.relationship('SkillInfo', backref=db.backref('student_uploads', lazy=True))