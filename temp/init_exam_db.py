"""
初始化資料庫,建立 exam_analysis 資料表
"""
from app import app, db
from models import init_db

with app.app_context():
    # 使用 SQLAlchemy 的 engine 來初始化資料庫
    init_db(db.engine)
    print("資料庫初始化完成!")
    print("exam_analysis 資料表已建立")
