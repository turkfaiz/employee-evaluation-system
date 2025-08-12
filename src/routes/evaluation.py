from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.evaluation import MonthlyEvaluation, EvaluationScore
from src.models.employee import Employee
from src.models.department import EvaluationCriteria
from datetime import datetime

evaluation_bp = Blueprint('evaluation', __name__)

@evaluation_bp.route('/evaluations', methods=['POST'])
def create_evaluation():
    """إضافة تقييم شهري جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['employee_id', 'evaluation_month', 'evaluation_year', 'scores']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        # التحقق من وجود الموظف
        employee = Employee.query.get(data['employee_id'])
        if not employee:
            return jsonify({'error': 'الموظف غير موجود'}), 400
        
        # التحقق من عدم وجود تقييم مسبق لنفس الشهر والسنة
        existing_evaluation = MonthlyEvaluation.query.filter_by(
            employee_id=data['employee_id'],
            evaluation_month=data['evaluation_month'],
            evaluation_year=data['evaluation_year']
        ).first()
        
        if existing_evaluation:
            return jsonify({'error': 'يوجد تقييم مسبق لهذا الموظف في نفس الشهر والسنة'}), 400
        
        # إنشاء التقييم الشهري
        evaluation = MonthlyEvaluation(
            employee_id=data['employee_id'],
            evaluation_month=data['evaluation_month'],
            evaluation_year=data['evaluation_year']
        )
        
        db.session.add(evaluation)
        db.session.flush()  # للحصول على ID التقييم
        
        # إضافة درجات التقييم
        for score_data in data['scores']:
            if 'criteria_id' not in score_data or 'score' not in score_data:
                return jsonify({'error': 'بيانات الدرجات غير مكتملة'}), 400
            
            # التحقق من وجود المعيار
            criteria = EvaluationCriteria.query.get(score_data['criteria_id'])
            if not criteria:
                return jsonify({'error': f'معيار التقييم {score_data["criteria_id"]} غير موجود'}), 400
            
            # التحقق من أن المعيار ينتمي لنفس إدارة الموظف
            if criteria.department_id != employee.department_id:
                return jsonify({'error': 'معيار التقييم لا ينتمي لإدارة الموظف'}), 400
            
            score = EvaluationScore(
                evaluation_id=evaluation.id,
                criteria_id=score_data['criteria_id'],
                score=score_data['score']
            )
            db.session.add(score)
        
        db.session.commit()
        return jsonify(evaluation.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@evaluation_bp.route('/employees/<int:employee_id>/evaluations', methods=['GET'])
def get_employee_evaluations(employee_id):
    """الحصول على جميع تقييمات موظف معين"""
    try:
        # التحقق من وجود الموظف
        employee = Employee.query.get_or_404(employee_id)
        
        # الحصول على التقييمات مرتبة حسب السنة والشهر
        evaluations = MonthlyEvaluation.query.filter_by(employee_id=employee_id)\
            .order_by(MonthlyEvaluation.evaluation_year.desc(), 
                     MonthlyEvaluation.evaluation_month.desc()).all()
        
        return jsonify([eval.to_dict() for eval in evaluations])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evaluation_bp.route('/employees/<int:employee_id>/evaluations/chart-data', methods=['GET'])
def get_employee_chart_data(employee_id):
    """الحصول على بيانات الرسم البياني لموظف معين"""
    try:
        # التحقق من وجود الموظف
        employee = Employee.query.get_or_404(employee_id)
        
        # الحصول على التقييمات للسنة الحالية أو السنة المحددة
        year = request.args.get('year', datetime.now().year, type=int)
        
        evaluations = MonthlyEvaluation.query.filter_by(
            employee_id=employee_id,
            evaluation_year=year
        ).order_by(MonthlyEvaluation.evaluation_month).all()
        
        # تحضير البيانات للرسم البياني
        months = []
        total_scores = []
        average_scores = []
        criteria_scores = {}
        
        # أسماء الأشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        for evaluation in evaluations:
            month_name = month_names[evaluation.evaluation_month]
            months.append(month_name)
            total_scores.append(evaluation.get_total_score())
            average_scores.append(evaluation.get_average_score())
            
            # تجميع درجات كل معيار
            for score in evaluation.scores:
                criteria_name = score.criteria.criteria_name
                if criteria_name not in criteria_scores:
                    criteria_scores[criteria_name] = []
                criteria_scores[criteria_name].append(score.score)
        
        return jsonify({
            'employee': employee.to_dict(),
            'year': year,
            'months': months,
            'total_scores': total_scores,
            'average_scores': average_scores,
            'criteria_scores': criteria_scores
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@evaluation_bp.route('/evaluations/<int:evaluation_id>', methods=['PUT'])
def update_evaluation(evaluation_id):
    """تحديث تقييم موجود"""
    try:
        evaluation = MonthlyEvaluation.query.get_or_404(evaluation_id)
        data = request.get_json()
        
        if 'scores' in data:
            # حذف الدرجات القديمة
            EvaluationScore.query.filter_by(evaluation_id=evaluation_id).delete()
            
            # إضافة الدرجات الجديدة
            for score_data in data['scores']:
                score = EvaluationScore(
                    evaluation_id=evaluation_id,
                    criteria_id=score_data['criteria_id'],
                    score=score_data['score']
                )
                db.session.add(score)
        
        db.session.commit()
        return jsonify(evaluation.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@evaluation_bp.route('/evaluations/<int:evaluation_id>', methods=['DELETE'])
def delete_evaluation(evaluation_id):
    """حذف تقييم"""
    try:
        evaluation = MonthlyEvaluation.query.get_or_404(evaluation_id)
        db.session.delete(evaluation)
        db.session.commit()
        return jsonify({'message': 'تم حذف التقييم بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

