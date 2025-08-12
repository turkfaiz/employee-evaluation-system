from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class MonthlyEvaluation(db.Model):
    __tablename__ = 'monthly_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    evaluation_month = db.Column(db.Integer, nullable=False)  # 1-12
    evaluation_year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    scores = db.relationship('EvaluationScore', backref='evaluation', lazy=True, cascade='all, delete-orphan')
    
    # فهرس فريد لضمان عدم تكرار التقييم لنفس الموظف في نفس الشهر والسنة
    __table_args__ = (db.UniqueConstraint('employee_id', 'evaluation_month', 'evaluation_year'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'evaluation_month': self.evaluation_month,
            'evaluation_year': self.evaluation_year,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'scores': [score.to_dict() for score in self.scores]
        }
    
    def get_total_score(self):
        return sum(score.score for score in self.scores)
    
    def get_average_score(self):
        if not self.scores:
            return 0
        return self.get_total_score() / len(self.scores)

class EvaluationScore(db.Model):
    __tablename__ = 'evaluation_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('monthly_evaluations.id'), nullable=False)
    criteria_id = db.Column(db.Integer, db.ForeignKey('evaluation_criteria.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'evaluation_id': self.evaluation_id,
            'criteria_id': self.criteria_id,
            'criteria_name': self.criteria.criteria_name if self.criteria else None,
            'score': self.score,
            'max_score': self.criteria.max_score if self.criteria else 100
        }

