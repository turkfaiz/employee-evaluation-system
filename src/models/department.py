from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    criteria_count = db.Column(db.Integer, nullable=False)
    
    # العلاقات
    employees = db.relationship('Employee', backref='department', lazy=True)
    criteria = db.relationship('EvaluationCriteria', backref='department', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'criteria_count': self.criteria_count
        }

class EvaluationCriteria(db.Model):
    __tablename__ = 'evaluation_criteria'
    
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    criteria_name = db.Column(db.String(200), nullable=False)
    max_score = db.Column(db.Integer, nullable=False, default=5)
    
    # العلاقات
    scores = db.relationship('EvaluationScore', backref='criteria', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'department_id': self.department_id,
            'criteria_name': self.criteria_name,
            'max_score': self.max_score
        }

