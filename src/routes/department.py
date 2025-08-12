from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.department import Department, EvaluationCriteria

department_bp = Blueprint('department', __name__)

@department_bp.route('/departments', methods=['GET'])
def get_departments():
    """الحصول على جميع الإدارات"""
    try:
        departments = Department.query.all()
        return jsonify([dept.to_dict() for dept in departments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@department_bp.route('/departments/<int:department_id>/criteria', methods=['GET'])
def get_department_criteria(department_id):
    """الحصول على معايير التقييم لإدارة معينة"""
    try:
        criteria = EvaluationCriteria.query.filter_by(department_id=department_id).all()
        return jsonify([criterion.to_dict() for criterion in criteria])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@department_bp.route('/init-departments', methods=['POST'])
def initialize_departments():
    """تهيئة الإدارات الافتراضية ومعايير التقييم"""
    try:
        # التحقق من وجود إدارات مسبقاً
        if Department.query.first():
            return jsonify({'message': 'الإدارات موجودة مسبقاً'})
        
        # إدارة الموارد البشرية (5 معايير)
        hr_dept = Department(name='إدارة الموارد البشرية', criteria_count=5)
        db.session.add(hr_dept)
        db.session.flush()
        
        hr_criteria = [
            EvaluationCriteria(department_id=hr_dept.id, criteria_name='الحضور والانضباط', max_score=5),
            EvaluationCriteria(department_id=hr_dept.id, criteria_name='جودة العمل', max_score=5),
            EvaluationCriteria(department_id=hr_dept.id, criteria_name='التعاون مع الفريق', max_score=5),
            EvaluationCriteria(department_id=hr_dept.id, criteria_name='المبادرة والإبداع', max_score=5),
            EvaluationCriteria(department_id=hr_dept.id, criteria_name='الالتزام بالمواعيد', max_score=5)
        ]
        
        # إدارة المبيعات (8 معايير)
        sales_dept = Department(name='إدارة المبيعات', criteria_count=8)
        db.session.add(sales_dept)
        db.session.flush()
        
        sales_criteria = [
            EvaluationCriteria(department_id=sales_dept.id, criteria_name='تحقيق الأهداف البيعية', max_score=5),
            EvaluationCriteria(department_id=sales_dept.id, criteria_name='خدمة العملاء', max_score=5),
            EvaluationCriteria(department_id=sales_dept.id, criteria_name='الحضور والانضباط', max_score=5),
            EvaluationCriteria(department_id=sales_dept.id, criteria_name='التعاون مع الفريق', max_score=5),
            EvaluationCriteria(department_id=sales_dept.id, criteria_name='المبادرة والإبداع', max_score=5),
            EvaluationCriteria(department_id=sales_dept.id, criteria_name='مهارات التواصل', max_score=5),
            EvaluationCriteria(department_id=sales_dept.id, criteria_name='إدارة الوقت', max_score=5),
            EvaluationCriteria(department_id=sales_dept.id, criteria_name='التطوير المهني', max_score=5)
        ]
        
        # إدارة التقنية (8 معايير)
        tech_dept = Department(name='إدارة التقنية', criteria_count=8)
        db.session.add(tech_dept)
        db.session.flush()
        
        tech_criteria = [
            EvaluationCriteria(department_id=tech_dept.id, criteria_name='الكفاءة التقنية', max_score=5),
            EvaluationCriteria(department_id=tech_dept.id, criteria_name='حل المشاكل', max_score=5),
            EvaluationCriteria(department_id=tech_dept.id, criteria_name='جودة الكود', max_score=5),
            EvaluationCriteria(department_id=tech_dept.id, criteria_name='الحضور والانضباط', max_score=5),
            EvaluationCriteria(department_id=tech_dept.id, criteria_name='التعاون مع الفريق', max_score=5),
            EvaluationCriteria(department_id=tech_dept.id, criteria_name='التعلم المستمر', max_score=5),
            EvaluationCriteria(department_id=tech_dept.id, criteria_name='الابتكار', max_score=5),
            EvaluationCriteria(department_id=tech_dept.id, criteria_name='إدارة المشاريع', max_score=5)
        ]
        
        # إدارة المالية (5 معايير)
        finance_dept = Department(name='إدارة المالية', criteria_count=5)
        db.session.add(finance_dept)
        db.session.flush()
        
        finance_criteria = [
            EvaluationCriteria(department_id=finance_dept.id, criteria_name='دقة البيانات المالية', max_score=5),
            EvaluationCriteria(department_id=finance_dept.id, criteria_name='الالتزام بالمواعيد', max_score=5),
            EvaluationCriteria(department_id=finance_dept.id, criteria_name='الحضور والانضباط', max_score=5),
            EvaluationCriteria(department_id=finance_dept.id, criteria_name='التعاون مع الفريق', max_score=5),
            EvaluationCriteria(department_id=finance_dept.id, criteria_name='التحليل المالي', max_score=5)
        ]
        
        # إضافة جميع المعايير
        for criteria_list in [hr_criteria, sales_criteria, tech_criteria, finance_criteria]:
            for criterion in criteria_list:
                db.session.add(criterion)
        
        db.session.commit()
        return jsonify({'message': 'تم تهيئة الإدارات ومعايير التقييم بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@department_bp.route('/departments', methods=['POST'])
def create_department():
    """إنشاء إدارة جديدة"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('name'):
            return jsonify({'error': 'اسم الإدارة مطلوب'}), 400
        
        if not data.get('criteria') or len(data['criteria']) == 0:
            return jsonify({'error': 'يجب إضافة معيار واحد على الأقل'}), 400
        
        # التحقق من عدم تكرار اسم الإدارة
        existing_dept = Department.query.filter_by(name=data['name']).first()
        if existing_dept:
            return jsonify({'error': 'اسم الإدارة موجود مسبقاً'}), 400
        
        # إنشاء الإدارة الجديدة
        department = Department(
            name=data['name'],
            criteria_count=len(data['criteria'])
        )
        
        db.session.add(department)
        db.session.flush()  # للحصول على ID الإدارة
        
        # إضافة معايير التقييم
        for criterion_data in data['criteria']:
            if not criterion_data.get('name'):
                continue
                
            criterion = EvaluationCriteria(
                department_id=department.id,
                criteria_name=criterion_data['name'],
                max_score=5  # النظام الجديد من 5 درجات
            )
            db.session.add(criterion)
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم إنشاء الإدارة بنجاح',
            'department': department.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@department_bp.route('/departments/<int:department_id>', methods=['PUT'])
def update_department(department_id):
    """تحديث إدارة موجودة"""
    try:
        department = Department.query.get_or_404(department_id)
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('name'):
            return jsonify({'error': 'اسم الإدارة مطلوب'}), 400
        
        if not data.get('criteria') or len(data['criteria']) == 0:
            return jsonify({'error': 'يجب إضافة معيار واحد على الأقل'}), 400
        
        # التحقق من عدم تكرار اسم الإدارة (عدا الإدارة الحالية)
        existing_dept = Department.query.filter(
            Department.name == data['name'],
            Department.id != department_id
        ).first()
        if existing_dept:
            return jsonify({'error': 'اسم الإدارة موجود مسبقاً'}), 400
        
        # تحديث اسم الإدارة
        department.name = data['name']
        department.criteria_count = len(data['criteria'])
        
        # حذف المعايير القديمة
        EvaluationCriteria.query.filter_by(department_id=department_id).delete()
        
        # إضافة المعايير الجديدة
        for criterion_data in data['criteria']:
            if not criterion_data.get('name'):
                continue
                
            criterion = EvaluationCriteria(
                department_id=department.id,
                criteria_name=criterion_data['name'],
                max_score=5  # النظام الجديد من 5 درجات
            )
            db.session.add(criterion)
        
        db.session.commit()
        
        return jsonify({
            'message': 'تم تحديث الإدارة بنجاح',
            'department': department.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@department_bp.route('/departments/<int:department_id>', methods=['DELETE'])
def delete_department(department_id):
    """حذف إدارة"""
    try:
        department = Department.query.get_or_404(department_id)
        
        # التحقق من عدم وجود موظفين في هذه الإدارة
        from src.models.employee import Employee
        employees_count = Employee.query.filter_by(department_id=department_id).count()
        
        if employees_count > 0:
            return jsonify({
                'error': f'لا يمكن حذف الإدارة لأنها تحتوي على {employees_count} موظف/موظفين'
            }), 400
        
        # حذف معايير التقييم أولاً
        EvaluationCriteria.query.filter_by(department_id=department_id).delete()
        
        # حذف الإدارة
        db.session.delete(department)
        db.session.commit()
        
        return jsonify({'message': 'تم حذف الإدارة بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@department_bp.route('/departments/<int:department_id>', methods=['GET'])
def get_department(department_id):
    """الحصول على تفاصيل إدارة محددة"""
    try:
        department = Department.query.get_or_404(department_id)
        criteria = EvaluationCriteria.query.filter_by(department_id=department_id).all()
        
        result = department.to_dict()
        result['criteria'] = [criterion.to_dict() for criterion in criteria]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

