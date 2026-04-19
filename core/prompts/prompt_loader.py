# -*- coding: utf-8 -*-
"""YAML-based Prompt Source of Truth Loader"""

import os
import yaml
import json
import logging
from flask import current_app
from models import db
from core.models.prompt_template import PromptTemplate

logger = logging.getLogger(__name__)

def load_prompt_yaml():
    """Loads the prompt registry YAML file robustly."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    yaml_path = os.path.join(base_dir, 'configs', 'prompts', 'prompt_registry.yaml')
    
    if not os.path.exists(yaml_path):
        logger.error(f"[Prompt Bootstrap] YAML config not found: {yaml_path}")
        raise FileNotFoundError(f"YAML config not found: {yaml_path}")
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            registry_data = yaml.safe_load(f)
        return registry_data
    except Exception as e:
        logger.error(f"[Prompt Bootstrap] YAML parsing error: {e}")
        raise

def bootstrap_prompt_registry(update_existing=False):
    """Reads YAML and conditionally inserts or updates missing prompts into the database."""
    try:
        registry_data = load_prompt_yaml()
        prompts = registry_data.get('prompts', {})
        created = 0
        skipped = 0
        updated = 0
        
        for key, details in prompts.items():
            existing = PromptTemplate.query.filter_by(prompt_key=key).first()
            
            req_vars = details.get('required_variables', [])
            req_vars_json = json.dumps(req_vars, ensure_ascii=False) if isinstance(req_vars, list) else json.dumps([], ensure_ascii=False)
            content = details.get('content', '').strip()
            role = details.get('role', 'tutor')
            
            if not existing:
                template = PromptTemplate(
                    prompt_key=key,
                    title=key,
                    category=role,
                    description="Bootstrapped from YAML registry",
                    content=content,
                    default_content=content,
                    required_variables=req_vars_json,
                    usage_context="yaml_bootstrap",
                    used_in="yaml_bootstrap",
                    example_trigger="yaml_bootstrap",
                    is_active=True
                )
                db.session.add(template)
                created += 1
            else:
                if update_existing:
                    existing.content = content
                    existing.default_content = content
                    existing.required_variables = req_vars_json
                    existing.category = role
                    updated += 1
                else:
                    skipped += 1
        
        db.session.commit()
        log_msg = f"created={created} updated={updated} skipped={skipped}"
        if current_app:
            current_app.logger.info("[Prompt Bootstrap] source=YAML")
            current_app.logger.info(f"[Prompt Bootstrap] {log_msg}")
        else:
            print("[Prompt Bootstrap] source=YAML")
            print(f"[Prompt Bootstrap] {log_msg}")
        return created, updated, skipped
        
    except Exception as e:
        if current_app:
            current_app.logger.error(f"[Prompt Bootstrap] Error during bootstrapping: {e}")
        else:
            print(f"[Prompt Bootstrap] Error during bootstrapping: {e}")
        db.session.rollback()
        raise
