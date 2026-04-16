# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): config.py
功能說明 (Description): 全域系統設定檔，集中管理資料庫、上傳路徑、模型角色、RAG 閾值與實驗參數。
執行語法 (Usage): 由系統自動載入
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
import os

# 專案根目錄絕對路徑（目前檔案所在資料夾）
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    全域設定類別（Global Configuration）
    包含資料庫、上傳、角色模型映射、RAG 與實驗控制參數。
    """

    # ==========================================
    # 1. 資料庫設定（SQLite）
    # ==========================================
    # 建立 instance 資料夾（若不存在）
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # 組合資料庫檔案絕對路徑
    db_path = os.path.join(instance_path, 'kumon_math.db')
    
    # 資料庫連線 URI
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==========================================
    # 2. 上傳資料夾設定
    # ==========================================
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
    # 確保上傳資料夾存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ==========================================
    # 3. 安全性設定
    # ==========================================
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'

    # ==========================================
    # 3.5. RAG 配置
    # ==========================================
    # 控制混合 RAG 中，Naive RAG (快速通道) 與 Advanced RAG (救援通道) 的分流閾值
    # 若 Naive RAG 的首筆距離分數小於或等於此閾值，將直接採用快速通道。
    # 數值越小，越嚴格（越常走 Advanced RAG 救援）；數值越大，越寬鬆（常走 Naive）。
    # 管理者可以根據實驗調整此分流比例
    ADVANCED_RAG_NAIVE_THRESHOLD = 0.35

    # ==========================================
    # 4. 各種 AI 模型群配置 (本地與雲端端點) 各群組
    # ==========================================
    
    # AI 預設提供者設定
    DEFAULT_PROVIDER = 'local' 

    # [實驗與開發] 模型預設集合（Coder Presets）
    # 可在 scripts/run_experiment.py 透過 key 參照並切換設定
    # 格式：dictionary { 'safe-name': { config } }
    CODER_PRESETS = {
        # 1. Google Gemini (Cloud)
        'gemini-3-flash': {
            'provider': 'google',
            'model': 'gemini-3-flash-preview',
            'temperature': 0.1,
            'max_tokens': 65536,
            'description': 'Gemini 3.0 Flash Preview (SOTA Cloud)',

            # [NEW] Gemini 安全性設定：全部門檻設為 BLOCK_NONE
            # 用於避免題目中正常數學內容被安全機制誤擋
            'safety_settings': [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]            
        },

        # 2. Qwen 3 14B (Local) [Thinking Disabled via Modelfile]
        'qwen3-14b': {
            'provider': 'local',
            'model': 'qwen3-14b-nothink:latest', # [Updated] User specific custom model
            'temperature': 0.1,                  # [Note] Keep slight creativity to avoid logic loops
            'max_tokens': 2048,                  # User requested 2048 to prevent truncation
            'extra_body': {
                'num_ctx': 32768,
                'num_gpu': -1,            
                'num_batch': 512,         
                'num_thread': 8,
                'keep_alive': "30m",
                'top_k': 40,
                'top_p': 0.9,
                'repeat_penalty': 1.1,
            },
            'description': 'Qwen3-14B (No-Think Custom)'
        },

        # 3. Qwen 2.5 14B (Local) - Legacy
        'qwen2.5-coder-14b': {
            'provider': 'local',
            'model': 'qwen2.5-coder:14b', 
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 16384,
                'num_gpu': -1,
                'num_batch': 1024,
                'num_thread': 8,
                'num_predict': 2048,
                'keep_alive': "30m",
                'top_k': 10,
                'top_p': 0.9,
                'repeat_penalty': 1.15,
            },
            'description': 'Qwen 2.5 Coder 14B (Local)'
        },

        # 4. Qwen 3 8B (Local) [Thinking Allowed]
        'qwen3-8b': {
            'provider': 'local',
            'model': 'qwen3:8b',          
            'temperature': 0.1,           
            'max_tokens': 2048,           
            'extra_body': {
                'num_ctx': 4096,          # [X Elite Optimization] Reduced from 8192 to 4096 for RAM stability
                'num_gpu': -1,
                'num_batch': 512,        
                'num_thread': 8,
                'keep_alive': "30m",
                'top_k': 40,
                'top_p': 0.95,
                'repeat_penalty': 1.1,
            },
            'description': 'Qwen3-8B (Memory Tuned)'
        },

        # 5. Qwen 2.5 1.5B (Local) [Ultra Lightweight Fallback]
        'qwen2.5-1.5b': {
            'provider': 'local',
            'model': 'qwen2.5-coder:1.5b', 
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 4096,
                'num_gpu': -1,
                'num_batch': 512,
                'keep_alive': "30m",
            },
            'description': 'Qwen 2.5 Coder 1.5B (Ultra-Stable Fallback)'
        },
        'qwen2.5-3b': {
            'provider': 'local',
            'model': 'qwen2.5:3b',
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 4096,
                'num_gpu': -1,
                'num_thread': 8,
                'keep_alive': "30m",
            },
            'description': 'Qwen 2.5 3B (User Local Model)'
        },
        'qwen3-vl-8b': {
            'provider': 'local',
            'model': 'qwen3-vl:8b-instruct-q4_k_m', 
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 4096,          # 從 8192 調整為 4096，降低記憶體壓力
                'num_gpu': -1,            # 使用可用 GPU 層數（自動）
                'num_thread': 8,
                'keep_alive': "60m",      # 延長模型常駐時間，減少冷啟動
                'top_k': 20,
                'top_p': 0.9,
            },
            'description': 'Qwen3-VL 8B (Visual Reasoning Engine)'
        },

        # 6.5. Qwen3-VL 4B (Local) [Lightweight Vision Engine]
        'qwen3-vl-4b': {
            'provider': 'local',
            'model': 'qwen3-vl:4b', 
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 4096,          # 輕量配置，降低延遲並穩定執行
                'num_gpu': -1,            # 盡量使用 GPU
                'num_thread': 8,
                'keep_alive': "60m",
                'top_k': 20,
                'top_p': 0.9,
            },
            'description': 'Qwen3-VL 4B (Visual Reasoning Engine)'
        },

        # 7. Qwen3.5 9B (Local) [Text-Only, 2026-03-11 新增測試]
        'qwen3.5-9b': {
            'provider': 'local',
            'model': 'qwen3.5:9b',
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 8192,
                'num_gpu': -1,
                'num_thread': 8,
                'keep_alive': "30m",
                'top_k': 20,
                'top_p': 0.9,
                'repeat_penalty': 1.1,
            },
            'description': 'Qwen3.5-9B (Text-Only, Trial)'
        },
        
        # 8. Qwen3.5 4B (Local) [Text-Only, Lightweight Trial]
        'qwen3.5-4b': {
            'provider': 'local',
            'model': 'qwen3.5:4b',
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 4096,
                'num_gpu': -1,
                'num_thread': 8,
                'keep_alive': "30m",
                'top_k': 20,
                'top_p': 0.9,
                'repeat_penalty': 1.1,
            },
            'description': 'Qwen3.5-4B (Text-Only, Lightweight)'
        },

        # 9. Gemma 4 e4b IT (Local) [2026-04 unified single-model integration test]
        'gemma4-e4b': {
            'provider': 'local',
            'model': 'gemma4:e4b-it-q4_K_M',
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 4096,
                'num_gpu': -1,
                'num_thread': 8,
                'keep_alive': "30m",
                'top_k': 20,
                'top_p': 0.9,
                'repeat_penalty': 1.1,
            },
            'description': 'Gemma 4 e4b IT q4_K_M (Local Unified Test)'
        },
    }

    # 設定目前啟用的預設模型鍵值（對應 CODER_PRESETS）
    # [rollback] 原本：DEFAULT_CODER_PRESET = 'gemma4-e4b'
    DEFAULT_CODER_PRESET = 'qwen2.5-3b'

    # Preserve Mathproject's original model options so they remain easy to
    # toggle by commenting/uncommenting during manual testing.
    CODER_PRESETS.update({
        'qwen2.5-coder-7b-legacy': {
            'provider': 'local',
            'model': 'qwen2.5-coder:7b',
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 8192,
                'num_gpu': -1,
                'num_batch': 1024,
                'num_thread': 8,
                'keep_alive': "30m",
            },
            'description': 'Legacy Mathproject coder preset',
        },
        'gemini-1.5-flash-legacy': {
            'provider': 'google',
            'model': 'gemini-1.5-flash',
            'temperature': 0.3,
            'max_tokens': 2048,
            'description': 'Legacy Mathproject vision preset',
        },
    })

    # 模型角色對應設定
    # 供 Web 路由依角色選擇模型使用
    # 若在 run_experiment.py 另有指定，將以實驗設定優先

    # coder / tutor / classifier / default / vision_analyzer 統一為 CODER_PRESETS['qwen3-vl-8b']（各 role 有 gemma4-e4b rollback 註解）。
    MODEL_ROLES = {
        'architect': {
            'provider': 'google',
            'model': 'gemini-2.5-flash', 
            'temperature': 0.7,
            'max_tokens': 1500,
        },
        
        # 可切回文字模型（Qwen 3，記憶體優化）
        # 'coder': CODER_PRESETS['qwen3-8b'], 

        # 目前 coder 使用本地模型；下方保留回滾與替代選項
        # [rollback] coder 原本：CODER_PRESETS['qwen3-vl-8b']  # [2026-03-11] 曾改為 VL 路線
        # [rollback] 原本：CODER_PRESETS['gemma4-e4b']
        'coder': CODER_PRESETS['qwen2.5-3b'],
        # 'coder': CODER_PRESETS['gemma4-e4b'],
        # 'coder': CODER_PRESETS['qwen3-vl-4b'],
        # 'coder': CODER_PRESETS['qwen3.5-4b'],
                
        # Practice AI 助教測試切換：
        # 原本本地 tutor：
        # 'tutor': {
        #     'provider': 'local',
        #     'model': 'phi3.5'
        # },
        # 若要切回 Gemini 可用：
        # 'tutor': {
        #     'provider': 'google',
        #     'model': 'gemini-2.5-flash',
        #     'temperature': 0.3,
        #     'max_tokens': 2048,
        # },
        # [rollback] tutor 原本：CODER_PRESETS['qwen3-vl-8b']
        # [rollback] 原本：CODER_PRESETS['gemma4-e4b']
        'tutor': CODER_PRESETS['qwen3-vl-8b'],
        
        # 視覺分析器：目前以 Qwen3-VL 為主，Gemini 為備選
        # [rollback] vision_analyzer 原本：CODER_PRESETS['qwen3-vl-8b']
        # [rollback] vision_analyzer 改回 qwen3-vl-8b（Gemma 在手寫 OCR 不穩）
        # [rollback] 原本：CODER_PRESETS['gemma4-e4b']
        'vision_analyzer': CODER_PRESETS['qwen3-vl-8b'],
        # 'vision_analyzer': CODER_PRESETS['gemma4-e4b'],

        # 'vision_analyzer': {
        #     'provider': 'gemini', 
        #     'model': 'gemini-2.5-flash' 
        # },

        # [rollback] classifier 原本：provider 'google', model 'gemini-2.5-flash', temperature 0.3, max_tokens 500
        # [rollback] 原本：CODER_PRESETS['gemma4-e4b']
        'classifier': CODER_PRESETS['qwen2.5-3b'],

        # [rollback] default 原本：provider 'local', model 'qwen3-14b-nothink:latest'
        # [rollback] 原本：CODER_PRESETS['gemma4-e4b']
        'default': CODER_PRESETS['qwen2.5-3b'],
    }

    LEGACY_MODEL_ROLES = {
        'architect': {
            'provider': 'google',
            'model': 'gemini-2.5-flash',
            'temperature': 0.7,
            'max_tokens': 2000,
        },
        'coder': CODER_PRESETS['qwen2.5-coder-7b-legacy'],
        'tutor': {
            'provider': 'local',
            'model': 'phi3.5',
        },
        'vision_analyzer': CODER_PRESETS['gemini-1.5-flash-legacy'],
        'default': CODER_PRESETS['qwen2.5-coder-7b-legacy'],
    }

    # --- [Cloud] Google Gemini API Key ---
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # --- [Local] Ollama API URL ---
    LOCAL_API_URL = "http://localhost:11434/api/generate"
    
    # （相容舊版變數）保留給舊流程與工具讀取
    AI_PROVIDER = DEFAULT_PROVIDER
    GEMINI_MODEL_NAME = "gemini-2.5-flash"
    #LOCAL_MODEL_NAME = "qwen2.5-coder:3b"
    LOCAL_MODEL_NAME = "qwen2.5-coder:7b"
    
    # [V2.5 Data Enhancement] Experiment Batch Tag
    EXPERIMENT_BATCH = 'Run_V2.5_Elite'

    # ==========================================
    # [NEW] 實驗執行設定 (Experiment Configuration)
    # ==========================================
    # 可於實驗流程中調整逾時與穩定性重試次數，避免長流程中斷
    # 若本機資源較低，可提高 timeout 或降低 reps 以減少失敗率
    
    EXECUTION_TIMEOUT = 10      # 單次程式執行逾時秒數（由 5s 提高為 10s）
    OLLAMA_TIMEOUT = 600        # 本地模型請求逾時秒數（由 300s 提高為 600s）
    STABILITY_REPS = 3          # L1.2 穩定性測試重複次數
