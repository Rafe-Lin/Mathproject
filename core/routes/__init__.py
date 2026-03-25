# -*- coding: utf-8 -*-
"""
=============================================================================
璅∠??迂 (Module Name): core/routes/__init__.py
?隤芣? (Description): 頝舐璅∠?????鞎痊摰儔 Flask Blueprints (core_bp, practice_bp) 銝血?交???頝舐璅∠???
?瑁?隤? (Usage): ?梁頂蝯梯矽??
?鞈? (Version): V2.0
?湔?交? (Date): 2026-01-13
蝬剛風?? (Maintainer): Math AI Project Team
=============================================================================
"""
from flask import Blueprint
core_bp = Blueprint('core', __name__, template_folder='../../templates')
practice_bp = Blueprint('practice', __name__)
live_show_bp = Blueprint('live_show', __name__)

# ??銵??餉?????admin.py
from . import auth, admin, practice, classroom, analysis, exam, knowledge_graph, live_show, adaptive_api
