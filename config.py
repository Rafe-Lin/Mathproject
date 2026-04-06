# -*- coding: utf-8 -*-
"""
=============================================================================
璅∠??迂 (Module Name): config.py
?隤芣? (Description): ?典??蔭瑼?嚗?銝剔恣???澈???摮葡??獢??唾楝敺??啗身摰誑??AI 璅∪????脫?瘣曇???蔭??
?瑁?隤? (Usage): ?梁頂蝯梯矽??
?鞈? (Version): V2.0
?湔?交? (Date): 2026-01-13
蝬剛風?? (Maintainer): Math AI Project Team
=============================================================================
"""
import os

# ???桀?瑼???函??桅? (蝯?頝臬?)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    ?典?閮剖?瑼?(Global Configuration)
    ?嚗??澈??獢??喋誑??撅??函? AI ?芋蝯身摰?
    """

    # ==========================================
    # 1. 鞈?摨怨身摰?(SQLite)
    # ==========================================
    # 撱箇? instance 鞈?憭?(憒?銝???
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # 瑽遣鞈?摨急?獢?蝯?頝臬?
    db_path = os.path.join(instance_path, 'kumon_math.db')
    
    # 閮剖???? URI
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==========================================
    # 2. 瑼?蝟餌絞閮剖?
    # ==========================================
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
    # 蝣箔?銝?桅?摮
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ==========================================
    # 3. 摰閮剖?
    # ==========================================
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'

    # ==========================================
    # 4. ????AI ?芋蝯身摰?(蝘?撖阡??詨?) ????
    # ==========================================
    
    # AI 璅∪?隤踹漲銝剖?
    DEFAULT_PROVIDER = 'local' 

    # [撖阡?撠] 璅∪???澈 (Coder Presets)
    # ?券?靘?scripts/run_experiment.py ?? Key ?湔霈?蒂????
    # 蝯?嚗ictionary { 'safe-name': { config } }
    CODER_PRESETS = {
        # 1. Google Gemini (Cloud)
        'gemini-3-flash': {
            'provider': 'google',
            'model': 'gemini-3-flash-preview',
            'temperature': 0.1,
            'max_tokens': 65536,
            'description': 'Gemini 3.0 Flash Preview (SOTA Cloud)',

            # ????[NEW] 摰閮剖?嚗?券???(BLOCK_NONE) ????
            # ??脫迫璅∪??隤文 "?梢?批捆" ??蝯??摮賊???
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
        'qwen3-vl-8b': {
            'provider': 'local',
            'model': 'qwen3-vl:8b-instruct-q4_k_m', 
            'temperature': 0.1,
            'max_tokens': 2048,
            'extra_body': {
                'num_ctx': 4096,          # ?? 敺?8192 ? 4096嚗?撠楊憿臬??憤皞?
                'num_gpu': -1,            # 撘瑕雿輻憿臬?券?銵?
                'num_thread': 8,
                'keep_alive': "60m",      # 瞍內?遣霅唬??芋?虜擏?
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
                'num_ctx': 4096,          # 閮擃?嚗隞乩??偌皞?
                'num_gpu': -1,            # 100% VRAM ??
                'num_thread': 8,
                'keep_alive': "60m",
                'top_k': 20,
                'top_p': 0.9,
            },
            'description': 'Qwen3-VL 4B (Visual Reasoning Engine)'
        },

        # 7. Qwen3.5 9B (Local) [Text-Only, 2026-03-11 ?啣?皜祈岫]
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

    # ???身隞?Ⅳ??璅∪? Preset Key嚗耨?寞迨??臬????
    # [rollback] 原本：DEFAULT_CODER_PRESET = 'gemma4-e4b'
    DEFAULT_CODER_PRESET = 'qwen3-vl-8b'

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

    # ??蝟餌絞閫?晷
    # ? Web 隞?身雿輻?身摰?
    # 瘜冽?嚗un_experiment.py ?瑁????撥?嗉??ㄐ??'coder'

    # coder / tutor / classifier / default / vision_analyzer 統一為 CODER_PRESETS['qwen3-vl-8b']（各 role 有 gemma4-e4b rollback 註解）。
    MODEL_ROLES = {
        'architect': {
            'provider': 'google',
            'model': 'gemini-2.5-flash', 
            'temperature': 0.7,
            'max_tokens': 1500,
        },
        
        # ?身撌亦?撣?(Qwen 3 Tuned for RAM)
        # 'coder': CODER_PRESETS['qwen3-8b'], 

        # ?身撌亦?撣思??臭誑?湔?郊?? VL ?嚗???閫隞?Ⅳ??
        # [rollback] coder 原本：CODER_PRESETS['qwen3-vl-8b']  # [2026-03-11] ?Ｗ儔雿輻蝯曹? VL ?嗆?
        # [rollback] 原本：CODER_PRESETS['gemma4-e4b']
        'coder': CODER_PRESETS['qwen3-vl-8b'],
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
        
        # 撠?閬箏??敺?Gemini ???典?? Qwen3-VL
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
        'classifier': CODER_PRESETS['qwen3-vl-8b'],

        # [rollback] default 原本：provider 'local', model 'qwen3-14b-nothink:latest'
        # [rollback] 原本：CODER_PRESETS['gemma4-e4b']
        'default': CODER_PRESETS['qwen3-vl-8b'],
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
    
    # (???訾??誑?脣隞?獢??典?荔?雿遣霅啁敹恍蝘?
    AI_PROVIDER = DEFAULT_PROVIDER
    GEMINI_MODEL_NAME = "gemini-2.5-flash"
    #LOCAL_MODEL_NAME = "qwen2.5-coder:3b"
    LOCAL_MODEL_NAME = "qwen2.5-coder:7b"
    
    # [V2.5 Data Enhancement] Experiment Batch Tag
    EXPERIMENT_BATCH = 'Run_V2.5_Elite'

    # ==========================================
    # [NEW] 撖阡??閮剖? (Experiment Configuration)
    # ==========================================
    # ?券?蝯曹?蝞∠?閰?????撖阡???銝剔?頞??帘摰批???
    # ?芷?嚗?甈⊿?蝵殷??函頂蝯勗??剁???行?璅∪????寥ㄐ嚗??寧?撘Ⅳ
    
    EXECUTION_TIMEOUT = 10      # 閰??誨蝣澆銵?蝘? (??5s -> 撱箄降 10s)
    OLLAMA_TIMEOUT = 600        # ?砍璅∪??函?頞?? (??300s -> 撱箄降 600s)
    STABILITY_REPS = 3          # L1.2 蝛拙??扳葫閰阡?銴活?
