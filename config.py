# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): config.py
功能說明 (Description): 全域配置檔案，集中管理資料庫連線字串、檔案上傳路徑、密鑰設定、以及 AI 模型的角色指派與參數配置。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
import os

# 取得目前檔案所在的目錄 (絕對路徑)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    全域設定檔 (Global Configuration)
    包含：資料庫、檔案上傳、以及科展專用的 AI 雙模組設定
    """

    # ==========================================
    # 1. 資料庫設定 (SQLite)
    # ==========================================
    # 建立 instance 資料夾 (如果不存在)
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # 構建資料庫檔案的絕對路徑
    db_path = os.path.join(instance_path, 'kumon_math.db')
    
    # 設定連線 URI
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==========================================
    # 2. 檔案系統設定
    # ==========================================
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
    # 確保上傳目錄存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ==========================================
    # 3. 安全設定
    # ==========================================
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'

    # ==========================================
    # 4. ★★★ AI 雙模組設定 (科展實驗核心) ★★★
    # ==========================================
    
    # AI 模型調度中心
    
    # 預設供應商 (預設用 local 比較省錢)
    DEFAULT_PROVIDER = 'local' 

    # ★ 關鍵修改：角色與模型的對照表
    # 格式：'角色': {'provider': '供應商', 'model': '模型名稱'}
    MODEL_ROLES = {
        # [新增] 架構師角色：負責讀題、設計邏輯 (使用 Phi-4-mini 3.8B)
        'architect': {
            #'provider': 'local',
            #'model': 'phi4-mini', 
            'provider': 'google',
            'model': 'gemini-2.5-flash',
            'temperature': 0.7 # 稍微高一點，讓它能歸納出不同的題型變化
            #'max_tokens': 2000  # 足夠寫出詳細的設計圖
        },        
        # 1. 工程師：專門寫 Code (精準、強迫症)
        'coder': {
            #'provider': 'local',
            #'model': 'qwen2.5-coder:7b',
            #'model': 'deepseek-coder-v2:lite',
            #'temperature': 0.1,
            #'num_ctx': 8192     # [建議新增] 確保它讀得懂長長的教案  
            'provider': 'google',
            'model': 'gemini-2.5-flash'

            #'model': 'qwen3-coder:30b'
            #'model': 'qwen2.5-coder:14b'
            #'model': 'freehuntx/qwen3-coder:14b' # rtx2060 跑不動     
            #'model': 'freehuntx/qwen3-coder:8b'
            
        },
        
        # 2. 助教：專門解釋觀念 (溫柔、話多)
        'tutor': {
            'provider': 'local',
            'model': 'phi3.5'
        },
        
        # 3. 教授：專門解析課本與圖片 (聰明、視力好)
        'vision_analyzer': {
            'provider': 'gemini', 
            'model': 'gemini-1.5-flash' 
        },

        # 4. 預設值 (Default)
        'default': {
            'provider': 'local',
            'model': 'qwen2.5-coder:7b'
        }
    }

    # --- [Cloud] Google Gemini API Key ---
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # --- [Local] Ollama API URL ---
    LOCAL_API_URL = "http://localhost:11434/api/generate"
    
    # (舊變數保留以防其他檔案引用報錯，但建議盡快遷移)
    AI_PROVIDER = DEFAULT_PROVIDER
    GEMINI_MODEL_NAME = "gemini-2.5-flash"
    #LOCAL_MODEL_NAME = "qwen2.5-coder:3b"
    LOCAL_MODEL_NAME = "qwen2.5-coder:7b"
    
    # [V2.5 Data Enhancement] Experiment Batch Tag
    EXPERIMENT_BATCH = 'Run_V2.5_Elite'

    # [AST Pipeline] 單元-題型架構 feature flag
    # USE_AST_PIPELINE=1: code_generator 優先從 agent_skills/<id>/SKILL.md 讀取規格
    # 預設 0 不影響舊行為（SKILL.md 存在時仍會優先使用）
    USE_AST_PIPELINE = os.environ.get('USE_AST_PIPELINE', '0') == '1'