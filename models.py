from datetime import datetime
from app import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(200))
    image_url = db.Column(db.String(200))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    tech_stack = db.Column(db.String(200))
    project_url = db.Column(db.String(200))
    files = db.relationship('ProjectFile', backref='project', lazy=True)


class ProjectFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(50))
    file_path = db.Column(db.String(500), nullable=False)
    project_id = db.Column(db.Integer,
                           db.ForeignKey('project.id'),
                           nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
