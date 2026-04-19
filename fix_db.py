from app import app, db
from core.models.prompt_template import PromptTemplate
from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES

with app.app_context():
    for key, template_data in DEFAULT_PROMPT_TEMPLATES.items():
        prompt = PromptTemplate.query.filter_by(prompt_key=key).first()
        if prompt:
            prompt.required_variables = template_data.get('required_variables', '')
            print(f"Updated {key} required_vars to {prompt.required_variables}")
    
    db.session.commit()
    print("Database successfully synchronized required variables from defaults.")
