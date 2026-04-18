# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/data_importer.py
功能說明 (Description): 通用資料匯入模組，負責將 Excel 檔案中的資料批量導入 SQLite 資料庫，支援動態模型偵測與資料清洗 (如日期修復)。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
# ==============================================================================
import pandas as pd
import os
import logging
import traceback
from models import db
from datetime import datetime, timedelta
import numpy as np

# 設定 Logger
logger = logging.getLogger(__name__)

def get_model_mapping():
    """
    動態獲取所有 SQLAlchemy Model 的對照表
    不再需要手動維護 {'table_name': ModelClass} 字典
    
    Returns: 
        dict: { 'table_name': ModelClass }
    """
    mapping = {}
    try:
        # 方法 A: 針對 SQLAlchemy 1.4+ / Flask-SQLAlchemy 3.x (較新版本)
        # db.Model.registry.mappers 會包含所有已註冊的模型
        if hasattr(db.Model, 'registry'):
            for mapper in db.Model.registry.mappers:
                cls = mapper.class_
                if hasattr(cls, '__tablename__'):
                    mapping[cls.__tablename__] = cls
        
        # 方法 B: 針對舊版 SQLAlchemy 或特殊情況 (Fallback)
        # 如果方法 A 抓不到，嘗試遞迴抓取 db.Model 的所有子類別
        if not mapping:
            def get_all_subclasses(cls):
                all_subclasses = []
                for subclass in cls.__subclasses__():
                    all_subclasses.append(subclass)
                    all_subclasses.extend(get_all_subclasses(subclass))
                return all_subclasses

            for cls in get_all_subclasses(db.Model):
                if hasattr(cls, '__tablename__'):
                    mapping[cls.__tablename__] = cls
        
        # Debug: 印出偵測到的模型，方便開發者確認
        # print(f"DEBUG: Detected Models: {list(mapping.keys())}")
                    
    except Exception as e:
        logger.error(f"Error generating model mapping: {e}")
        
    return mapping

def clean_excel_row(row_dict):
    """
    [V9.8.2 Fix] 強力清洗 Excel 匯入資料：
    1. 修正日期欄位變成 True/False 或數字的問題。
    2. 將 NaN/NaT 轉為 None。
    3. [Fix] 支援微秒格式 (.%f) 的時間字串。
    4. [Fix] 加入 last_practiced, review_date 等所有時間欄位檢查。
    """
    cleaned = {}
    
    # 定義所有需要被視為時間的欄位名稱
    date_columns = [
        'timestamp', 'created_at', 'updated_at', 
        'last_practiced', 'review_date', 'login_time'
    ]

    for key, value in row_dict.items():
        # 1. 處理空值
        if pd.isna(value) or value == "":
            cleaned[key] = None
            continue

        # 2. 針對日期欄位 (包含 last_practiced 等) 的特殊處理
        if key in date_columns:
            # [Fix] 如果原本是 None，保持 None
            if value is None:
                cleaned[key] = None
                continue
            
            # [Fix] 攔截布林值 (兇手就是它！created_at: True)
            if isinstance(value, bool):
                # print(f"⚠️ [Data Fix] 欄位 {key} 異常 (值為 {value})，已自動修正為當前時間。")
                cleaned[key] = datetime.now()
                continue
                
            try:
                # 情況 A: Excel 序列數字 (float/int)，例如 46034.08
                if isinstance(value, (float, int)):
                    base_date = datetime(1899, 12, 30)
                    cleaned[key] = base_date + timedelta(days=value)
                # 情況 B: 已經是 datetime 物件
                elif isinstance(value, datetime):
                    cleaned[key] = value
                # 情況 C: 字串格式 (最容易出錯的地方)
                elif isinstance(value, str):
                    value = value.strip()
                    try:
                        # 嘗試格式 1: 含微秒 (2025-12-30 06:44:49.532000)
                        cleaned[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            # 嘗試格式 2: 一般時間 (2025-12-30 06:44:49)
                            cleaned[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                # 嘗試格式 3: 只有日期 (2025-12-30)
                                cleaned[key] = datetime.strptime(value, '%Y-%m-%d')
                            except:
                                # 真的沒救了，設為 None
                                print(f"⚠️ 無法解析的時間字串 [{key}]: {value}")
                                cleaned[key] = None
                else:
                    # 其他怪異格式，給當下時間或 None
                    cleaned[key] = datetime.now()
            except Exception as e:
                print(f"⚠️ 日期轉換失敗 [{key}]: {value} -> {e}")
                cleaned[key] = None 
        else:
            # 非日期欄位
            cleaned[key] = value
            
    return cleaned

def import_excel_to_db(filepath):
    """
    讀取 Excel 檔案，將每個 Sheet 的資料匯入對應的資料庫 Table (支援 Upsert)
    """
    if not os.path.exists(filepath):
        return False, "❌ 檔案不存在"

    try:
        # 1. 讀取 Excel 檔案 (取得所有 Sheet 的資料)
        xls = pd.read_excel(filepath, sheet_name=None, engine='openpyxl')
        
        # 動態取得對照表
        mapping = get_model_mapping()
        
        if not mapping:
            return False, "❌ 系統無法偵測到任何資料庫模型 (Model Mapping is empty)。"

        results = []
        results.append(f"ℹ️ 系統動態偵測到 {len(mapping)} 個資料庫模型。")
        
        # 2. 遍歷每一個 Sheet
        for sheet_name, df in xls.items():
            sheet_name_clean = sheet_name.strip()
            
            # 尋找對應的 Model
            model = None
            table_name = None

            # 2.1 精確比對
            if sheet_name_clean in mapping:
                model = mapping[sheet_name_clean]
                table_name = sheet_name_clean
            else:
                # 2.2 模糊比對 (忽略大小寫)
                # 例如 Excel Sheet 是 "Users"，但資料庫 Table 是 "users"
                for tbl_name, model_cls in mapping.items():
                    if tbl_name.lower() == sheet_name_clean.lower():
                        model = model_cls
                        table_name = tbl_name
                        break
            
            if not model:
                results.append(f"⚠️ 跳過 Sheet '{sheet_name}': 資料庫中無此 Table。")
                continue
            
            # 3. 資料處理 (Data Cleaning)
            # 將 pandas 的 NaN (空值) 轉為 Python 的 None
            df = df.where(pd.notnull(df), None)
            
            # 取得該 Model 的所有欄位名稱
            model_columns = model.__table__.columns.keys()
            
            imported_count = 0
            skipped_count = 0
            
            # 4. 逐列寫入資料庫
            for index, row in df.iterrows():
                try:
                    data = {}
                    # 只讀取 Model 裡有的欄位，忽略 Excel 裡多餘的欄位
                    for col in model_columns:
                        if col in row:
                            val = row[col]
                            
                            # 特殊處理：布林值字串轉換
                            if isinstance(val, str):
                                if val.lower() == 'true': val = True
                                elif val.lower() == 'false': val = False
                            
                            data[col] = val
                    
                    if not data:
                        skipped_count += 1
                        continue

                    # 🔥 [關鍵修改] 呼叫清洗函式，把 Excel 格式轉為 Python 格式
                    data = clean_excel_row(data)

                    # 使用 merge (UPSERT): 有 Primary Key 就更新，沒有就新增
                    instance = model(**data)
                    db.session.merge(instance)
                    imported_count += 1
                    
                except Exception as e:
                    print(f"❌ Error inserting row {index} in {sheet_name}: {e}")
                    continue
            
            results.append(f"✅ Table '{table_name}': 成功匯入/更新 {imported_count} 筆。")

        # 5. 提交變更
        db.session.commit()
        return True, "\n".join(results)

    except Exception as e:
        db.session.rollback()
        error_msg = f"❌ 匯入失敗: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return False, f"匯入發生錯誤: {str(e)}"