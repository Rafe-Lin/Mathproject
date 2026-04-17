# -*- coding: utf-8 -*-
"""Bootstrap default prompt templates into database."""

from core.models.prompt_template import PromptTemplate
from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES
from models import db
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

def bootstrap_prompt_templates() -> int:
    # 安全防呆：如果 prompt_templates 尚未存在，不要讓 bootstrap 直接崩潰
    try:
        inspector = inspect(db.engine)
        if not inspector.has_table("prompt_templates"):
            print("table not ready")
            print("skipping bootstrap")
            return 0
    except Exception as e:
        print(f"Error checking table existence: {e}")
        return 0

    created_count = 0

    for prompt_key, template in DEFAULT_PROMPT_TEMPLATES.items():
        try:
            existing = (
                db.session.query(PromptTemplate)
                .filter(PromptTemplate.prompt_key == prompt_key)
                .first()
            )
            if existing:
                continue

            default_content = template["content"]
            record = PromptTemplate(
                prompt_key=prompt_key,
                title=template["title"],
                category=template["category"],
                description=template.get("description"),
                usage_context=template.get("usage_context", ""),
                used_in=template.get("used_in", ""),
                example_trigger=template.get("example_trigger", ""),
                content=default_content,
                default_content=default_content,
                required_variables=template.get("required_variables", ""),
                is_active=bool(template.get("is_active", True)),
            )
            db.session.add(record)
            created_count += 1
        except OperationalError:
            print("table not ready: OperationalError during query")
            print("skipping bootstrap")
            break
        except Exception as e:
            print(f"Skipping bootstrap due to error: {e}")
            break

    if created_count > 0:
        db.session.commit()

    return created_count

