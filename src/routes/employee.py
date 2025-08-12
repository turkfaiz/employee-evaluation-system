from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.employee import Employee
from src.models.department import Department

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/employees', methods=['GET'])
def get_employees():
    """الحصول على جميع الموظفين"""
    try:
        employees = Employee.query.all()
        return jsonify([emp.to_dict() for emp in employees])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employee_bp.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """الحصول على موظف محدد"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        return jsonify(employee.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employee_bp.route('/employees', methods=['POST'])
def create_employee():
    """إضافة موظف جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['employee_number', 'full_name', 'job_title', 'department_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        # التحقق من عدم تكرار الرقم الوظيفي
        existing_employee = Employee.query.filter_by(employee_number=data['employee_number']).first()
        if existing_employee:
            return jsonify({'error': 'الرقم الوظيفي موجود مسبقاً'}), 400
        
        # التحقق من وجود الإدارة
        department = Department.query.get(data['department_id'])
        if not department:
            return jsonify({'error': 'الإدارة غير موجودة'}), 400
        
        # إنشاء الموظف الجديد
        employee = Employee(
            employee_number=data['employee_number'],
            full_name=data['full_name'],
            job_title=data['job_title'],
            department_id=data['department_id']
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify(employee.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employee_bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """تحديث بيانات موظف"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        data = request.get_json()
        
        # تحديث البيانات
        if 'employee_number' in data:
            # التحقق من عدم تكرار الرقم الوظيفي
            existing_employee = Employee.query.filter_by(employee_number=data['employee_number']).first()
            if existing_employee and existing_employee.id != employee_id:
                return jsonify({'error': 'الرقم الوظيفي موجود مسبقاً'}), 400
            employee.employee_number = data['employee_number']
        
        if 'full_name' in data:
            employee.full_name = data['full_name']
        
        if 'job_title' in data:
            employee.job_title = data['job_title']
        
        if 'department_id' in data:
            department = Department.query.get(data['department_id'])
            if not department:
                return jsonify({'error': 'الإدارة غير موجودة'}), 400
            employee.department_id = data['department_id']
        
        db.session.commit()
        return jsonify(employee.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employee_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """حذف موظف"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'message': 'تم حذف الموظف بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

