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
import csv
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# 建立 SQLAlchemy 實例
db = SQLAlchemy()

PROJECT_ROOT = Path(__file__).resolve().parent
BRIDGE_CATALOG_PATH = PROJECT_ROOT / "docs" / "自適應實作" / "skill_breakpoint_catalog.csv"
LINEAR_SKILL_ID = "jh_數學1上_OperationsOnLinearExpressions"



def _read_bridge_catalog_rows() -> list[dict[str, str]]:
    if not BRIDGE_CATALOG_PATH.exists():
        return []
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp950"): 
        try:
            with BRIDGE_CATALOG_PATH.open("r", encoding=encoding, newline="") as fh:
                reader = csv.DictReader(fh)
                rows = [dict(row) for row in reader]
                skill_ids = sorted(
                    {
                        str(row.get("skill_id", "") or "").strip()
                        for row in rows
                        if str(row.get("skill_id", "") or "").strip()
                    }
                )
                linear_rows = [
                    row for row in rows
                    if str(row.get("skill_id", "") or "").strip() == LINEAR_SKILL_ID
                ]
                print(
                    "[RAG SOURCE] "
                    f"catalog={BRIDGE_CATALOG_PATH.name} total_rows={len(rows)} "
                    f"skill_count={len(skill_ids)} contains_linear_skill={bool(linear_rows)} "
                    f"linear_rows={len(linear_rows)}"
                )
                if linear_rows:
                    preview = [
                        {
                            "family_id": str(row.get("family_id", "") or "").strip(),
                            "subskill_nodes": str(row.get("subskill_nodes", "") or "").strip(),
                        }
                        for row in linear_rows[:5]
                    ]
                    print(f"[RAG SOURCE] linear_preview={preview}")
                return rows
        except Exception as exc:  # pragma: no cover
            last_error = exc
    raise RuntimeError(f"Failed to read bridge catalog {BRIDGE_CATALOG_PATH}: {last_error}")


def _sync_skill_family_bridge(conn):
    """
    ? skill_breakpoint_catalog.csv ????????????
    ?????????????????????
    """
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS skill_family_bridge (
            bridge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id TEXT NOT NULL,
            family_id TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            skill_ch_name TEXT,
            skill_en_name TEXT,
            family_name TEXT NOT NULL,
            theme TEXT,
            subskill_nodes TEXT NOT NULL,
            notes TEXT,
            curriculum TEXT,
            grade INTEGER,
            volume TEXT,
            chapter TEXT,
            section TEXT,
            paragraph TEXT,
            hint_scope TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            source TEXT NOT NULL DEFAULT 'skill_breakpoint_catalog.csv',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(skill_id, family_id)
        )
    """)
    c.execute('CREATE INDEX IF NOT EXISTS idx_skill_family_bridge_skill_id ON skill_family_bridge(skill_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_skill_family_bridge_family_id ON skill_family_bridge(family_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_skill_family_bridge_curriculum ON skill_family_bridge(curriculum)')
    c.execute("DELETE FROM skill_family_bridge WHERE source = 'skill_breakpoint_catalog.csv'")

    rows = _read_bridge_catalog_rows()
    if not rows:
        conn.commit()
        return

    curriculum_rows = c.execute("""
        SELECT skill_id, curriculum, grade, volume, chapter, section, paragraph
        FROM skill_curriculum
        ORDER BY display_order ASC, difficulty_level ASC, id ASC
    """).fetchall()
    curriculum_map: dict[str, tuple] = {}
    for row in curriculum_rows:
        curriculum_map.setdefault(row[0], row)

    for row in rows:
        skill_id = str(row.get("skill_id", "") or "").strip()
        family_id = str(row.get("family_id", "") or "").strip()
        skill_name = str(row.get("skill_name", "") or "").strip()
        family_name = str(row.get("family_name", "") or "").strip()
        theme = str(row.get("theme", "") or "").strip()
        notes = str(row.get("notes", "") or "").strip()
        subskill_nodes = [item.strip() for item in str(row.get("subskill_nodes", "") or "").split(";") if item.strip()]
        if not skill_id or not family_id or not skill_name or not family_name or not subskill_nodes:
            continue

        curriculum_row = curriculum_map.get(skill_id)
        curriculum = curriculum_row[1] if curriculum_row else None
        grade = curriculum_row[2] if curriculum_row else None
        volume = curriculum_row[3] if curriculum_row else None
        chapter = curriculum_row[4] if curriculum_row else None
        section = curriculum_row[5] if curriculum_row else None
        paragraph = curriculum_row[6] if curriculum_row else None

        skill_row = c.execute("""
            SELECT skill_ch_name, skill_en_name
            FROM skills_info
            WHERE skill_id = ?
        """, (skill_id,)).fetchone()
        skill_ch_name = skill_row[0] if skill_row and skill_row[0] else skill_name
        skill_en_name = skill_row[1] if skill_row and skill_row[1] else None

        c.execute("""
            INSERT INTO skill_family_bridge (
                skill_id, family_id, skill_name, skill_ch_name, skill_en_name,
                family_name, theme, subskill_nodes, notes,
                curriculum, grade, volume, chapter, section, paragraph,
                hint_scope, version, source, created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, 1, 'skill_breakpoint_catalog.csv', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT(skill_id, family_id) DO UPDATE SET
                skill_name = excluded.skill_name,
                skill_ch_name = excluded.skill_ch_name,
                skill_en_name = excluded.skill_en_name,
                family_name = excluded.family_name,
                theme = excluded.theme,
                subskill_nodes = excluded.subskill_nodes,
                notes = excluded.notes,
                curriculum = excluded.curriculum,
                grade = excluded.grade,
                volume = excluded.volume,
                chapter = excluded.chapter,
                section = excluded.section,
                paragraph = excluded.paragraph,
                hint_scope = excluded.hint_scope,
                version = excluded.version,
                source = excluded.source,
                updated_at = CURRENT_TIMESTAMP
        """, (
            skill_id, family_id, skill_name, skill_ch_name, skill_en_name,
            family_name, theme, json.dumps(subskill_nodes, ensure_ascii=False), notes,
            curriculum, grade, volume, chapter, section, paragraph,
            ";".join(subskill_nodes)
        ))

    conn.commit()

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
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_uploaded_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            image_path TEXT,
            ocr_content TEXT,
            ai_solution TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id)
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
    add_column_if_not_exists('skills_info', 'importance', 'FLOAT NOT NULL DEFAULT 1.0')

    # Experiment Log (v9.0 補丁)
    new_log_cols = [
        ('experiment_batch', 'TEXT'), ('prompt_strategy', 'TEXT'), ('prompt_version', 'INTEGER'),
        ('error_category', 'TEXT'),
        ('regex_fix_count', 'INTEGER DEFAULT 0'), ('logic_fix_count', 'INTEGER DEFAULT 0'), ('ast_repair_count', 'INTEGER DEFAULT 0'),
        ('prompt_tokens', 'INTEGER DEFAULT 0'), ('completion_tokens', 'INTEGER DEFAULT 0'), ('total_tokens', 'INTEGER DEFAULT 0'),
        ('code_complexity', 'INTEGER DEFAULT 0'),
        ('gpu_usage', 'REAL DEFAULT 0'), ('gpuram_usage', 'REAL DEFAULT 0'),
        ('raw_output_length', 'INTEGER DEFAULT 0'), ('perfect_utils_length', 'INTEGER DEFAULT 0'),
        # [科研新增欄位]
        ('start_time', 'REAL'), ('prompt_len', 'INTEGER'), ('code_len', 'INTEGER'),
        ('error_msg', 'TEXT'), ('repaired', 'BOOLEAN DEFAULT 0'),
        ('model_size_class', 'TEXT'), ('prompt_level', 'TEXT'),
        ('raw_response', 'TEXT'), ('final_code', 'TEXT'),
        ('score_syntax', 'REAL DEFAULT 0.0'), ('score_math', 'REAL DEFAULT 0.0'), ('score_visual', 'REAL DEFAULT 0.0'),
        ('healing_duration', 'REAL'), ('is_executable', 'BOOLEAN'),
        ('ablation_id', 'INTEGER'), ('missing_imports_fixed', 'TEXT'), ('resource_cleanup_flag', 'BOOLEAN'),
        # [旺宏科學獎 3×3 設計專用欄位]
        ('experiment_group', 'TEXT'),  # 'A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'
        ('garbage_cleaner_count', 'INTEGER DEFAULT 0'),  # Garbage Cleaner 修復次數
        ('eval_eliminator_count', 'INTEGER DEFAULT 0'),  # Eval Eliminator 修復次數
        ('sampling_success_count', 'INTEGER DEFAULT 0'),  # Dynamic Sampling 成功次數
        ('sampling_total_count', 'INTEGER DEFAULT 0'),  # Dynamic Sampling 總次數
        ('spec_prompt_id', 'INTEGER'),  # 關聯到 skill_gencode_prompt.id
        ('use_master_spec', 'BOOLEAN DEFAULT 0')  # 是否使用 MASTER_SPEC
    ]
    for col, definition in new_log_cols:
        add_column_if_not_exists('experiment_log', col, definition)

    # [v9.0 補丁] Skill GenCode Prompt 新增 architect_model 和 experiment_group
    add_column_if_not_exists('skill_gencode_prompt', 'architect_model', "TEXT DEFAULT 'human'")
    add_column_if_not_exists('skill_gencode_prompt', 'experiment_group', 'TEXT')
    add_column_if_not_exists('skill_gencode_prompt', 'generation_duration', 'REAL')
    add_column_if_not_exists('textbook_examples', 'difficulty_h', 'FLOAT NOT NULL DEFAULT 1.0')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ablation_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            use_regex BOOLEAN DEFAULT 0,
            use_ast BOOLEAN DEFAULT 0,
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_id TEXT NOT NULL,
            ability_a REAL DEFAULT 1.0,
            concept_u REAL DEFAULT 1.0,
            calculation_c REAL DEFAULT 1.0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id),
            UNIQUE(user_id, skill_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS adaptive_learning_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            step_number INTEGER NOT NULL,
            target_family_id TEXT NOT NULL,
            target_subskills TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            current_apr REAL NOT NULL,
            ppo_strategy INTEGER NOT NULL,
            frustration_index INTEGER NOT NULL DEFAULT 0,
            execution_latency INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')

    _sync_skill_family_bridge(conn)

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
    importance = db.Column(db.Float, nullable=False, default=1.0)

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
            'suggested_prompt_3': self.suggested_prompt_3,
            'importance': self.importance,
        }

class SkillGenCodePrompt(db.Model):
    __tablename__ = 'skill_gencode_prompt'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String(50), db.ForeignKey('skills_info.skill_id'), nullable=False)
    
    # [新增] 記錄這段 Prompt 是由誰設計的 (例如: 'human', 'gpt-4o', 'gemini-1.5-pro')
    architect_model = db.Column(db.String(50), default='human', nullable=False)

    # [模型分級策略]
    # 值範例: 'category:teacher', 'category:cloud_tutor', 'category:local_edge'
    # 這裡也作為 MASTER_SPEC 的標籤存放處 (V15.3 Research)
    model_tag = db.Column(db.String(50), default='default', nullable=False)
    
    # [提示策略] & 標籤系統
    # 值範例: 'Architect-Engineer', 'CoT_Decomposed', 'MASTER_SPEC'
    prompt_type = db.Column(db.String(50), default='standard')
    prompt_strategy = db.Column(db.String(50), default='standard')
    
    # [內容核心]
    system_prompt = db.Column(db.Text)          # 系統角色設定
    user_prompt_template = db.Column(db.Text)   # 使用者指令模板 (舊版)
    prompt_content = db.Column(db.Text)         # [MASTER_SPEC] 統一存放完整 Spec 內容
    
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
            'prompt_type': self.prompt_type,
            'prompt_content': self.prompt_content,
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


class SkillFamilyBridge(db.Model):
    __tablename__ = 'skill_family_bridge'

    bridge_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False, index=True)
    family_id = db.Column(db.String(64), nullable=False, index=True)
    skill_name = db.Column(db.String, nullable=False)
    skill_ch_name = db.Column(db.String, nullable=True)
    skill_en_name = db.Column(db.String, nullable=True)
    family_name = db.Column(db.String, nullable=False)
    theme = db.Column(db.String, nullable=True)
    subskill_nodes = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    curriculum = db.Column(db.String, nullable=True, index=True)
    grade = db.Column(db.Integer, nullable=True)
    volume = db.Column(db.String, nullable=True)
    chapter = db.Column(db.String, nullable=True)
    section = db.Column(db.String, nullable=True)
    paragraph = db.Column(db.String, nullable=True)
    hint_scope = db.Column(db.Text, nullable=True)
    version = db.Column(db.Integer, nullable=False, default=1)
    source = db.Column(db.String, nullable=False, default='skill_breakpoint_catalog.csv')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('skill_id', 'family_id', name='_skill_family_bridge_uc'),
    )

    skill = db.relationship('SkillInfo', backref=db.backref('family_bridges', lazy=True, cascade="all, delete-orphan"))

    def to_dict(self):
        try:
            nodes = json.loads(self.subskill_nodes) if self.subskill_nodes else []
        except Exception:
            nodes = [item.strip() for item in str(self.subskill_nodes or '').split(';') if item.strip()]
        return {
            'bridge_id': self.bridge_id,
            'skill_id': self.skill_id,
            'family_id': self.family_id,
            'skill_name': self.skill_name,
            'skill_ch_name': self.skill_ch_name,
            'skill_en_name': self.skill_en_name,
            'family_name': self.family_name,
            'theme': self.theme,
            'subskill_nodes': nodes,
            'notes': self.notes,
            'curriculum': self.curriculum,
            'grade': self.grade,
            'volume': self.volume,
            'chapter': self.chapter,
            'section': self.section,
            'paragraph': self.paragraph,
            'hint_scope': self.hint_scope,
            'version': self.version,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class SkillPrerequisites(db.Model):
    __tablename__ = 'skill_prerequisites'
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)
    prerequisite_id = db.Column(db.String, db.ForeignKey('skills_info.skill_id', ondelete='CASCADE'), nullable=False)
    __table_args__ = (db.UniqueConstraint('skill_id', 'prerequisite_id', name='_skill_prerequisite_uc'),)

class AblationSetting(db.Model):
    """
    [Research Edition] Ablation Study 實驗設定
    控制不同實驗組的 Healer 開關
    """
    __tablename__ = 'ablation_settings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 'Bare', 'Regex_Only', 'Full_Healing'
    use_regex = db.Column(db.Boolean, default=False)  # 是否啟用 Regex Healer
    use_ast = db.Column(db.Boolean, default=False)    # 是否啟用 AST Healer
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f"<AblationSetting(id={self.id}, name='{self.name}', regex={self.use_regex}, ast={self.use_ast})>"

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
    difficulty_h = db.Column(db.Float, nullable=False, default=1.0)
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
            'difficulty_level': self.difficulty_level,
            'difficulty_h': self.difficulty_h
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

# =============================================================================
# MCRI V4.2 實驗資料模型（2026-02-02）
# =============================================================================

class AblationSummary(db.Model):
    """
    [MCRI V4.2] 彙總統計表 - 記錄每個技能在不同配置下的統計彙總
    
    一個 summary 代表「一個技能 × 一個配置 × 5 個 sample 的統計結果」
    包含：平均分、標準差、95% 信賴區間、顯著性檢定
    """
    __tablename__ = 'ablation_summary'
    
    # ========== 主鍵與識別 ==========
    summary_id = db.Column(db.String(36), primary_key=True)  # UUID
    skill_name = db.Column(db.String(100), nullable=False)  # gh_ApplicationsOfDerivatives
    ablation_id = db.Column(db.Integer, nullable=False)  # 1=Bare, 2=Eng, 3=Healer
    model_name = db.Column(db.String(50), nullable=False)  # qwen2.5-coder:14b
    
    # ========== 統計數據 ==========
    sample_count = db.Column(db.Integer, nullable=False, default=5)  # 樣本數（固定 5）
    total_runs = db.Column(db.Integer, nullable=False, default=100)  # 總執行次數（5 × 20）
    
    # ========== MCRI 總分統計 ==========
    mean_mcri_total = db.Column(db.Float, nullable=False)  # 5 個 sample 的 avg_mcri_total 平均
    std_mcri_total = db.Column(db.Float, nullable=False)  # 標準差
    ci95_lower = db.Column(db.Float, nullable=False)  # 95% 信賴區間下界
    ci95_upper = db.Column(db.Float, nullable=False)  # 95% 信賴區間上界
    
    # ========== 關鍵維度統計 ==========
    mean_l3_external = db.Column(db.Float)  # L3.2 外在強健性平均（跨 5 sample）
    mean_l4_numeric = db.Column(db.Float)  # L4.1 數值友善性平均（跨 5 sample）
    
    # ========== 顯著性檢定 ==========
    p_value_vs_ab1 = db.Column(db.Float)  # 與 Ab1 的 t-test p-value
    notes = db.Column(db.Text)  # 備註（如「Ab3 顯著優於 Ab1, p<0.001」）
    
    # 唯一約束（每個技能 × 配置 × 模型只能有一筆）
    __table_args__ = (
        db.UniqueConstraint('skill_name', 'ablation_id', 'model_name', name='_summary_unique'),
    )
    
    def __repr__(self):
        return f"<AblationSummary {self.skill_name} Ab{self.ablation_id} | μ={self.mean_mcri_total:.1f}±{self.std_mcri_total:.1f}>"
    
    def to_dict(self):
        """轉換為字典（用於 JSON/CSV 序列化）"""
        return {
            'summary_id': self.summary_id,
            'skill_name': self.skill_name,
            'ablation_id': self.ablation_id,
            'model_name': self.model_name,
            'sample_count': self.sample_count,
            'total_runs': self.total_runs,
            'mean_mcri_total': self.mean_mcri_total,
            'std_mcri_total': self.std_mcri_total,
            'ci95_lower': self.ci95_lower,
            'ci95_upper': self.ci95_upper,
            'mean_l3_external': self.mean_l3_external,
            'mean_l4_numeric': self.mean_l4_numeric,
            'p_value_vs_ab1': self.p_value_vs_ab1,
            'notes': self.notes
        }

# [新增] ExperimentLog 模型 (科展實驗數據記錄)
class ExperimentLog(db.Model):
    __tablename__ = 'experiment_log'
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Float)
    duration_seconds = db.Column(db.Float)
    prompt_len = db.Column(db.Integer)
    code_len = db.Column(db.Integer)
    is_success = db.Column(db.Boolean)
    error_msg = db.Column(db.Text)
    repaired = db.Column(db.Boolean, default=False)
    model_name = db.Column(db.String(50))
    
    # --- [科研新增欄位] ---
    model_size_class = db.Column(db.String(20))     # '7B', '14B', 'Cloud'
    prompt_level = db.Column(db.String(20))          # 'Bare', 'Engineered', 'Self-Healing'
    raw_response = db.Column(db.Text)               # LLM 原始輸出
    final_code = db.Column(db.Text)                 # 最終修復代碼
    score_syntax = db.Column(db.Float, default=0.0) # 語法分
    score_math = db.Column(db.Float, default=0.0)   # 邏輯分
    score_visual = db.Column(db.Float, default=0.0) # 視覺分
    healing_duration = db.Column(db.Float)          # 自癒耗時
    is_executable = db.Column(db.Boolean)           # 是否可執行成功
    ablation_id = db.Column(db.Integer)             # 對應實驗組 ID
    missing_imports_fixed = db.Column(db.Text)      # 紀錄補上的庫
    resource_cleanup_flag = db.Column(db.Boolean)    # 資源釋放標記
    # ----------------------

    # 原有 Token 欄位
    prompt_tokens = db.Column(db.Integer, default=0)
    completion_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    code_complexity = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<ExperimentLog {self.model_name}: {self.duration_seconds}s>"


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


class StudentAbility(db.Model):
    __tablename__ = 'student_abilities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_id = db.Column(db.String(64), db.ForeignKey('skills_info.skill_id'), nullable=False)
    ability_a = db.Column(db.Float, nullable=False, default=1.0)
    concept_u = db.Column(db.Float, nullable=False, default=1.0)
    calculation_c = db.Column(db.Float, nullable=False, default=1.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'skill_id', name='_student_ability_uc'),
    )

    user = db.relationship('User', backref=db.backref('student_abilities', lazy=True))
    skill = db.relationship('SkillInfo', backref=db.backref('student_abilities', lazy=True))


class AdaptiveLearningLog(db.Model):
    __tablename__ = 'adaptive_learning_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_id = db.Column(db.String(64), nullable=False, index=True)
    step_number = db.Column(db.Integer, nullable=False)
    target_family_id = db.Column(db.String(64), nullable=False, index=True)
    target_subskills = db.Column(db.Text, nullable=False)  # JSON serialized list
    is_correct = db.Column(db.Boolean, nullable=False)
    current_apr = db.Column(db.Float, nullable=False)
    ppo_strategy = db.Column(db.Integer, nullable=False)  # 0/1/2/3
    frustration_index = db.Column(db.Integer, nullable=False, default=0)
    execution_latency = db.Column(db.Integer, nullable=False, default=0)  # milliseconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship('User', backref=db.backref('adaptive_learning_logs', lazy=True))

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'student_id': self.student_id,
            'session_id': self.session_id,
            'step_number': self.step_number,
            'target_family_id': self.target_family_id,
            'target_subskills': json.loads(self.target_subskills) if self.target_subskills else [],
            'is_correct': bool(self.is_correct),
            'current_apr': float(self.current_apr),
            'ppo_strategy': int(self.ppo_strategy),
            'frustration_index': int(self.frustration_index),
            'execution_latency': int(self.execution_latency),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }


class StudentUploadedQuestion(db.Model):
    __tablename__ = 'student_uploaded_questions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    ocr_content = db.Column(db.Text, nullable=True)
    ai_solution = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref=db.backref('student_uploaded_questions', lazy=True))


class ExecutionSample(db.Model):
    """
    [V1.3 Research Edition] 
    紀錄程式產出的「題目樣本」。用於分析 14B 模型的出題品質與穩定性。
    """
    __tablename__ = 'execution_samples'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.String(100), nullable=False)
    
    # 實驗變因
    mode = db.Column(db.Integer)                  # 模式 (1-6)
    ablation_id = db.Column(db.Integer)           # 自癒等級 (1-3)
    sample_index = db.Column(db.Integer)          # 採樣序號 (1-20)
    
    # 生成內容
    question_text = db.Column(db.Text)            # 題目文字
    correct_answer = db.Column(db.Text)           # 正確答案
    image_base64 = db.Column(db.Text)             # 圖片編碼
    
    # 品質指標
    is_crash = db.Column(db.Integer, default=0)         # 是否執行崩潰
    is_logic_correct = db.Column(db.Integer, default=0)  # 閱卷自檢是否通過
    score_complexity = db.Column(db.Integer, default=0)  # 題目難度分數
    duration_seconds = db.Column(db.Float)               # 生成耗時
    
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<ExecutionSample {self.skill_id} Mode {self.mode} #{self.sample_index}>"


# =============================================================================
# MCRI V4.2 實驗資料模型（2026-02-02 新增）
# =============================================================================

class ExperimentRun(db.Model):
    """
    [MCRI V4.2] 實驗主表 - 記錄每次完整的實驗執行
    
    一個 run 代表「一個技能 × 一個配置 × 一次完整測試（20次採樣）」
    包含：L1/L2 固定分數 + L3/L4 平均分 + 執行統計
    """
    __tablename__ = 'experiment_runs'
    
    # ========== 主鍵與識別 ==========
    run_id = db.Column(db.String(36), primary_key=True)  # UUID
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # ========== 實驗配置 ==========
    model_name = db.Column(db.String(50), nullable=False)  # qwen-14b / gemini-flash
    skill_name = db.Column(db.String(100), nullable=False)  # gh_ApplicationsOfDerivatives
    ablation_id = db.Column(db.Integer, nullable=False)  # 1=Bare, 2=Eng, 3=Healer
    sample_index = db.Column(db.Integer, nullable=False)  # 1~5
    
    # ========== 版本資訊 ==========
    code_commit_hash = db.Column(db.String(40), nullable=False)  # git commit hash
    python_version = db.Column(db.String(20), nullable=False)  # 3.9.13
    mcri_version = db.Column(db.String(20), nullable=False, default='V4.2')
    
    # ========== 生成參數 ==========
    model_temperature = db.Column(db.Float, nullable=False, default=0.7)
    
    # ========== 執行統計 ==========
    repetitions_planned = db.Column(db.Integer, nullable=False, default=20)
    repetitions_completed = db.Column(db.Integer, nullable=False)
    fail_count = db.Column(db.Integer, nullable=False, default=0)
    pass_rate = db.Column(db.Float)  # 0.0~1.0
    avg_exec_time = db.Column(db.Float)  # 秒
    
    # ========== L1. 工程基石（20分）- 固定值 ==========
    score_l1_total = db.Column(db.Integer)  # 0~20
    score_l1_1_syntax = db.Column(db.Integer)  # 0~10
    score_l1_2_runtime = db.Column(db.Integer)  # 0~10
    
    # ========== L2. 資料衛生（20分）- 固定值 ==========
    score_l2_total = db.Column(db.Integer)  # 0~20
    score_l2_1_contract = db.Column(db.Integer)  # 0~10
    score_l2_2_purity = db.Column(db.Integer)  # 0~10
    
    # ========== L3. 評測公平（30分）- 平均值 ==========
    avg_l3_total = db.Column(db.Float)  # 0.0~30.0
    avg_l3_1_internal = db.Column(db.Float)  # 0.0~15.0
    avg_l3_2_external = db.Column(db.Float)  # 0.0~15.0
    
    # ========== L4. 教學有效（30分）- 平均值 ==========
    avg_l4_total = db.Column(db.Float)  # 0.0~30.0
    avg_l4_1_numeric = db.Column(db.Float)  # 0.0~15.0
    avg_l4_2_visual = db.Column(db.Float)  # 0.0~15.0
    
    # ========== 總分（100分）==========
    avg_mcri_total = db.Column(db.Float)  # 0.0~100.0
    
    # ========== 檔案與備註 ==========
    source_code_path = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    
    # ========== 新增：批次管理 (Batch Management) ==========
    batch_id = db.Column(db.String(50))  # 批次 ID (e.g., 'exp_20260205_001')
    
    # ========== 新增：Golden Prompt 變因控制 (Control Variables) ==========
    golden_prompt_path = db.Column(db.String(255))  # Golden Prompt 文件路徑
    prompt_hash = db.Column(db.String(64))  # Prompt SHA256 雜湊值（驗證一致性）
    
    # ========== 新增：成本與效能指標 (Cost & Performance) ==========
    prompt_tokens = db.Column(db.Integer)           # Prompt Token 數
    completion_tokens = db.Column(db.Integer)       # 完成 Token 數
    total_tokens = db.Column(db.Integer)            # 總 Token 數
    latency_ms = db.Column(db.Integer)              # 延遲（毫秒）
    
    # ========== 新增：Healer 介入統計 (Healer Metrics) ==========
    healer_applied = db.Column(db.Boolean, default=False)  # 是否啟用 Healer (0=Ab2, 1=Ab3)
    healer_fix_count = db.Column(db.Integer, default=0)    # Healer 修復次數
    
    # 關聯 (一對多：一個 run 有多個 evaluation_items)
    evaluation_items = db.relationship('EvaluationItem', backref='run', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ExperimentRun {self.skill_name} Ab{self.ablation_id} #{self.sample_index} | MCRI={self.avg_mcri_total:.1f}>"
    
    def to_dict(self):
        """轉換為字典（用於 JSON 序列化）"""
        return {
            'run_id': self.run_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'model_name': self.model_name,
            'skill_name': self.skill_name,
            'ablation_id': self.ablation_id,
            'sample_index': self.sample_index,
            'code_commit_hash': self.code_commit_hash,
            'python_version': self.python_version,
            'mcri_version': self.mcri_version,
            'model_temperature': self.model_temperature,
            'repetitions_planned': self.repetitions_planned,
            'repetitions_completed': self.repetitions_completed,
            'fail_count': self.fail_count,
            'pass_rate': self.pass_rate,
            'avg_exec_time': self.avg_exec_time,
            'score_l1_total': self.score_l1_total,
            'score_l1_1_syntax': self.score_l1_1_syntax,
            'score_l1_2_runtime': self.score_l1_2_runtime,
            'score_l2_total': self.score_l2_total,
            'score_l2_1_contract': self.score_l2_1_contract,
            'score_l2_2_purity': self.score_l2_2_purity,
            'avg_l3_total': self.avg_l3_total,
            'avg_l3_1_internal': self.avg_l3_1_internal,
            'avg_l3_2_external': self.avg_l3_2_external,
            'avg_l4_total': self.avg_l4_total,
            'avg_l4_1_numeric': self.avg_l4_1_numeric,
            'avg_l4_2_visual': self.avg_l4_2_visual,
            'avg_mcri_total': self.avg_mcri_total,
            'source_code_path': self.source_code_path,
            'notes': self.notes,
            # 新增欄位
            'batch_id': self.batch_id,
            'golden_prompt_path': self.golden_prompt_path,
            'prompt_hash': self.prompt_hash,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'latency_ms': self.latency_ms,
            'healer_applied': self.healer_applied,
            'healer_fix_count': self.healer_fix_count
        }


class EvaluationItem(db.Model):
    """
    [MCRI V4.2] 評估明細表 - 記錄每次採樣的詳細結果
    
    包含：L3/L4 單次分數 + 產出內容 + 執行狀態
    用於分析失敗模式與保留原始資料
    """
    __tablename__ = 'evaluation_items'
    
    # ========== 主鍵與關聯 ==========
    item_id = db.Column(db.String(36), primary_key=True)  # UUID
    run_id = db.Column(db.String(36), db.ForeignKey('experiment_runs.run_id'), nullable=False)
    repetition_index = db.Column(db.Integer, nullable=False)  # 1~20
    
    # ========== 產出內容 ==========
    generated_question = db.Column(db.Text)  # question_text
    generated_answer = db.Column(db.Text)  # answer（通常空白）
    generated_correct_answer = db.Column(db.Text)  # correct_answer（比對用）
    
    # ========== 執行狀態 ==========
    status = db.Column(db.String(20), nullable=False)  # Success / Fail / Timeout
    error_log = db.Column(db.Text)  # 錯誤訊息（截斷至 1000 字元）
    exec_time_ms = db.Column(db.Float)  # 執行時間（毫秒）
    
    # ========== 統計控制 ==========
    included_in_avg = db.Column(db.Boolean, nullable=False, default=True)  # 是否計入平均
    
    # ========== L3. 評測公平（30分）- 單次分數 ==========
    score_l3_total = db.Column(db.Integer)  # 0~30
    score_l3_1_internal = db.Column(db.Integer)  # 0~15
    score_l3_2_external = db.Column(db.Integer)  # 0~15
    
    # ========== L4. 教學有效（30分）- 單次分數 ==========
    score_l4_total = db.Column(db.Integer)  # 0~30
    score_l4_1_numeric = db.Column(db.Integer)  # 0~15
    score_l4_2_visual = db.Column(db.Integer)  # 0~15
    
    # ========== L3.2 外在強健性測試細節 ==========
    student_input_test = db.Column(db.Text)  # JSON：["2x", "f'(x)=2x", "2*x"]
    student_input_result = db.Column(db.Text)  # JSON：[true, true, false]
    
    def __repr__(self):
        return f"<EvaluationItem Run={self.run_id[:8]}... Rep={self.repetition_index} Status={self.status}>"
    
    def to_dict(self):
        """轉換為字典（用於 JSON 序列化）"""
        return {
            'item_id': self.item_id,
            'run_id': self.run_id,
            'repetition_index': self.repetition_index,
            'generated_question': self.generated_question,
            'generated_answer': self.generated_answer,
            'generated_correct_answer': self.generated_correct_answer,
            'status': self.status,
            'error_log': self.error_log,
            'exec_time_ms': self.exec_time_ms,
            'included_in_avg': self.included_in_avg,
            'score_l3_total': self.score_l3_total,
            'score_l3_1_internal': self.score_l3_1_internal,
            'score_l3_2_external': self.score_l3_2_external,
            'score_l4_total': self.score_l4_total,
            'score_l4_1_numeric': self.score_l4_1_numeric,
            'score_l4_2_visual': self.score_l4_2_visual,
            'student_input_test': self.student_input_test,
            'student_input_result': self.student_input_result
        }


# ==============================================================================
# 7. HealerEvent 類 (Healer 修復事件追蹤表)
# ==============================================================================

class HealerEvent(db.Model):
    """
    Healer 修復事件表
    
    記錄每次 Healer 修復的詳細信息，包括：
    - 修復階段 (stage): Pre-Process, Regex_Healer, AST_Healer 等
    - 修復模式 (pattern_id): 具體的修復類型
    - 修復前後的代碼片段 (Evidence)
    - 修復耗時 (效能分析)
    """
    
    __tablename__ = 'healer_events'
    
    # ========== 識別欄位 ==========
    event_id = db.Column(db.String(36), primary_key=True)              # UUID
    run_id = db.Column(db.String(36), db.ForeignKey('experiment_runs.run_id'), nullable=False)
    
    # ========== 介入階段與類型 ==========
    stage = db.Column(db.String(50), nullable=False)                   # 例如 'Pre-Process', 'Regex_Healer', 'AST_Healer'
    pattern_id = db.Column(db.String(100))                             # 例如 'fix_infinite_loop', 'fix_latex_dollar_sign'
    
    # ========== 手術前後對比 (Evidence) ==========
    original_snippet = db.Column(db.Text)                              # 修改前片段 (限制 500 字)
    healed_snippet = db.Column(db.Text)                                # 修改後片段
    
    # ========== 結果與追蹤 ==========
    is_success = db.Column(db.Boolean, default=True)                   # 修復是否成功應用
    fix_duration_ms = db.Column(db.Integer, default=0)                 # 修復耗時（毫秒）
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)        # 記錄時間戳
    
    # ========== 關聯 ==========
    experiment_run = db.relationship('ExperimentRun', backref=db.backref('healer_events', lazy=True, cascade='all, delete-orphan'))
    
    def __init__(self, event_id, run_id, stage, pattern_id=None, original_snippet=None, 
                 healed_snippet=None, is_success=True, fix_duration_ms=0):
        self.event_id = event_id
        self.run_id = run_id
        self.stage = stage
        self.pattern_id = pattern_id
        self.original_snippet = original_snippet
        self.healed_snippet = healed_snippet
        self.is_success = is_success
        self.fix_duration_ms = fix_duration_ms
    
    def __repr__(self):
        return f"<HealerEvent Event={self.event_id[:8]}... Run={self.run_id[:8]}... Stage={self.stage}>"
    
    def to_dict(self):
        """轉換為字典（用於 JSON 序列化）"""
        return {
            'event_id': self.event_id,
            'run_id': self.run_id,
            'stage': self.stage,
            'pattern_id': self.pattern_id,
            'original_snippet': self.original_snippet,
            'healed_snippet': self.healed_snippet,
            'is_success': self.is_success,
            'fix_duration_ms': self.fix_duration_ms,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
