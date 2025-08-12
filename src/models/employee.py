from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(50), nullable=False, unique=True)
    full_name = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    evaluations = db.relationship('MonthlyEvaluation', backref='employee', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_number': self.employee_number,
            'full_name': self.full_name,
            'job_title': self.job_title,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

