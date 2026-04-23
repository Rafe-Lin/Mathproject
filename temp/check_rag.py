import sys
sys.path.insert(0, '.')
from app import app, db
from sqlalchemy import text

with app.app_context():
    tables = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")).fetchall()
    tables = [r[0] for r in tables]
    print("Tables with skill/bridge/catalog:")
    for t in tables:
        if any(k in t.lower() for k in ('skill', 'bridge', 'catalog')):
            cnt = db.session.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"  {t}: {cnt} rows")

    from core.advanced_rag_engine import _adv_collection, _documents, HAS_ADV_LIBS
    print(f"\nHAS_ADV_LIBS: {HAS_ADV_LIBS}")
    print(f"_adv_collection is None: {_adv_collection is None}")
    print(f"_documents count: {len(_documents)}")

    from core.rag_engine import _collection as naive_col
    print(f"naive _collection is None: {naive_col is None}")
