# -*- coding: utf-8 -*-
"""Prompt template ORM model."""

from datetime import datetime

from models import db


class PromptTemplate(db.Model):
    __tablename__ = "prompt_templates"

    id = db.Column(db.Integer, primary_key=True)
    prompt_key = db.Column(db.String(100), unique=True, index=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    default_content = db.Column(db.Text, nullable=False)
    required_variables = db.Column(db.String(500), default="")
    usage_context = db.Column(db.String(500), default="")
    used_in = db.Column(db.String(200), default="")
    example_trigger = db.Column(db.Text, default="")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return f"<PromptTemplate {self.prompt_key}>"

