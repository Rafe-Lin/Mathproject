import os
import sys

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from models import db
from core.models.prompt_template import PromptTemplate
from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES

def run_migration():
    app = create_app()
    with app.app_context():
        for key, data in DEFAULT_PROMPT_TEMPLATES.items():
            existing = PromptTemplate.query.filter_by(prompt_key=key).first()
            if not existing:
                pt = PromptTemplate(
                    prompt_key=key,
                    title=data.get("title", key),
                    category=data.get("category", "uncategorized"),
                    description=data.get("description", ""),
                    usage_context=data.get("usage_context", ""),
                    used_in=data.get("used_in", ""),
                    example_trigger=data.get("example_trigger", ""),
                    content=data.get("content", ""),
                    default_content=data.get("content", ""),
                    required_variables=",".join(data.get("required_variables", [])),
                    is_active=True
                )
                db.session.add(pt)
                print(f"Added new template: {key}")
            else:
                print(f"Template {key} already exists.")
        db.session.commit()
        print("Migration complete.")

if __name__ == "__main__":
    run_migration()
