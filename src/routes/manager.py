from flask import Blueprint, request, jsonify, render_template_string
from datetime import datetime, timedelta
import json
import os

manager_bp = Blueprint('manager', __name__)

# مسار ملف بيانات المدراء
MANAGERS_FILE = 'managers.json'

def load_managers():
    """تحميل بيانات المدراء"""
    if os.path.exists(MANAGERS_FILE):
        with open(MANAGERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_managers(managers):
    """حفظ بيانات المدراء"""
    with open(MANAGERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(managers, f, ensure_ascii=False, indent=2)

def get_current_evaluation_month():
    """الحصول على الشهر الحالي للتقييم"""
    now = datetime.now()
    # يمكن تخصيص هذا المنطق حسب احتياجات النظام
    return now.month, now.year

def is_evaluation_period_active(month, year):
    """التحقق من أن فترة التقييم نشطة"""
    current_month, current_year = get_current_evaluation_month()
    return month == current_month and year == current_year

@manager_bp.route('/manager/evaluate/<int:manager_id>')
def manager_evaluation_page(manager_id):
    """صفحة تقييم المدير"""
    
    # صفحة HTML للمدير
    manager_html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>صفحة تقييم المدير - مركز تجربة العميل</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .evaluation-card { transition: transform 0.2s; }
            .evaluation-card:hover { transform: translateY(-2px); }
            .progress-ring { width: 120px; height: 120px; }
            .employee-card { border-left: 4px solid #007bff; }
            .completed { border-left-color: #28a745; }
        </style>
    </head>
    <body class="bg-light">
        <!-- شريط التنقل -->
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <span class="navbar-brand">
                    <i class="fas fa-user-tie me-2"></i>
                    لوحة تقييم المدير - مركز تجربة العميل
                </span>
                <span class="navbar-text" id="manager-info">
                    مرحباً بك
                </span>
            </div>
        </nav>

        <!-- نموذج تسجيل الدخول -->
        <div id="login-section" class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow">
                        <div class="card-header bg-primary text-white text-center">
                            <h4><i class="fas fa-lock me-2"></i>تسجيل الدخول</h4>
                        </div>
                        <div class="card-body">
                            <form id="login-form">
                                <div class="mb-3">
                                    <label for="password" class="form-label">كلمة المرور</label>
                                    <input type="password" class="form-control" id="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">
                                    <i class="fas fa-sign-in-alt me-1"></i>
                                    دخول
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- قسم التقييم -->
        <div id="evaluation-section" class="container mt-4" style="display: none;">
            <!-- إحصائيات سريعة -->
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card text-center bg-primary text-white">
                        <div class="card-body">
                            <i class="fas fa-users fa-2x mb-2"></i>
                            <h5>إجمالي الموظفين</h5>
                            <h3 id="total-employees">0</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center bg-success text-white">
                        <div class="card-body">
                            <i class="fas fa-check-circle fa-2x mb-2"></i>
                            <h5>التقييمات المكتملة</h5>
                            <h3 id="completed-count">0</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center bg-warning text-white">
                        <div class="card-body">
                            <i class="fas fa-clock fa-2x mb-2"></i>
                            <h5>التقييمات المعلقة</h5>
                            <h3 id="pending-count">0</h3>
                        </div>
                    </div>
                </div>
            </div>

            <!-- معلومات فترة التقييم -->
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                <strong>فترة التقييم الحالية:</strong> <span id="current-period"></span>
            </div>

            <!-- قائمة الموظفين -->
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0">
                        <i class="fas fa-list me-2"></i>
                        موظفي الإدارة
                    </h5>
                </div>
                <div class="card-body">
                    <div id="employees-list" class="row">
                        <!-- قائمة الموظفين ستظهر هنا -->
                    </div>
                </div>
            </div>
        </div>

        <!-- نموذج التقييم -->
        <div class="modal fade" id="evaluationModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-star me-2"></i>
                            تقييم الموظف: <span id="employee-name"></span>
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="evaluation-form">
                            <input type="hidden" id="employee-id">
                            <div id="criteria-fields">
                                <!-- معايير التقييم ستظهر هنا -->
                            </div>
                            <div class="mt-3">
                                <label for="evaluation-notes" class="form-label">ملاحظات إضافية</label>
                                <textarea class="form-control" id="evaluation-notes" rows="3" placeholder="أدخل أي ملاحظات إضافية..."></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                        <button type="button" class="btn btn-success" onclick="submitEvaluation()">
                            <i class="fas fa-save me-1"></i>
                            حفظ التقييم
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- رسائل التنبيه -->
        <div id="alert-container" class="position-fixed top-0 end-0 p-3" style="z-index: 1050;"></div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            const managerId = {{ manager_id }};
            let currentEmployees = [];
            let currentDepartmentCriteria = [];

            // تسجيل الدخول
            document.getElementById('login-form').addEventListener('submit', async function(e) {
                e.preventDefault();
                const password = document.getElementById('password').value;
                
                try {
                    const response = await fetch(`/api/manager-login/${managerId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ password })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('login-section').style.display = 'none';
                        document.getElementById('evaluation-section').style.display = 'block';
                        document.getElementById('manager-info').textContent = `مرحباً ${result.manager_name}`;
                        loadEmployees();
                        updateCurrentPeriod();
                    } else {
                        showAlert('كلمة مرور خاطئة', 'danger');
                    }
                } catch (error) {
                    showAlert('خطأ في الاتصال', 'danger');
                }
            });

            // تحميل الموظفين
            async function loadEmployees() {
                try {
                    const response = await fetch(`/api/manager-employees/${managerId}`);
                    const data = await response.json();
                    
                    if (response.ok) {
                        currentEmployees = data.employees;
                        currentDepartmentCriteria = data.criteria;
                        displayEmployees();
                        updateStats();
                    }
                } catch (error) {
                    showAlert('خطأ في تحميل الموظفين', 'danger');
                }
            }

            // عرض الموظفين
            function displayEmployees() {
                const container = document.getElementById('employees-list');
                container.innerHTML = '';
                
                currentEmployees.forEach(employee => {
                    const isEvaluated = employee.is_evaluated;
                    const cardClass = isEvaluated ? 'employee-card completed' : 'employee-card';
                    
                    const employeeCard = document.createElement('div');
                    employeeCard.className = 'col-md-6 mb-3';
                    employeeCard.innerHTML = `
                        <div class="card ${cardClass}">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="card-title mb-1">${employee.name}</h6>
                                        <small class="text-muted">${employee.job_title}</small>
                                        <br>
                                        <small class="text-muted">الرقم الوظيفي: ${employee.employee_number}</small>
                                    </div>
                                    <div class="text-center">
                                        ${isEvaluated ? 
                                            '<span class="badge bg-success"><i class="fas fa-check"></i> مُقيم</span>' :
                                            `<button class="btn btn-primary btn-sm" onclick="openEvaluationModal(${employee.id})">
                                                <i class="fas fa-star"></i> تقييم
                                            </button>`
                                        }
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    container.appendChild(employeeCard);
                });
            }

            // فتح نموذج التقييم
            function openEvaluationModal(employeeId) {
                const employee = currentEmployees.find(e => e.id === employeeId);
                if (!employee) return;
                
                document.getElementById('employee-id').value = employeeId;
                document.getElementById('employee-name').textContent = employee.name;
                
                // إنشاء حقول معايير التقييم
                const criteriaContainer = document.getElementById('criteria-fields');
                criteriaContainer.innerHTML = '';
                
                currentDepartmentCriteria.forEach((criteria, index) => {
                    const field = document.createElement('div');
                    field.className = 'mb-3';
                    field.innerHTML = `
                        <label class="form-label">${criteria}</label>
                        <select class="form-select" name="criteria_${index}" required>
                            <option value="">اختر التقييم</option>
                            <option value="1">1 - ضعيف جداً</option>
                            <option value="2">2 - ضعيف</option>
                            <option value="3">3 - متوسط</option>
                            <option value="4">4 - جيد</option>
                            <option value="5">5 - ممتاز</option>
                        </select>
                    `;
                    criteriaContainer.appendChild(field);
                });
                
                new bootstrap.Modal(document.getElementById('evaluationModal')).show();
            }

            // حفظ التقييم
            async function submitEvaluation() {
                const employeeId = document.getElementById('employee-id').value;
                const notes = document.getElementById('evaluation-notes').value;
                
                // جمع درجات المعايير
                const criteria = {};
                const selects = document.querySelectorAll('#criteria-fields select');
                let allFilled = true;
                
                selects.forEach((select, index) => {
                    if (!select.value) {
                        allFilled = false;
                        return;
                    }
                    criteria[`criteria_${index}`] = parseInt(select.value);
                });
                
                if (!allFilled) {
                    showAlert('يرجى تقييم جميع المعايير', 'warning');
                    return;
                }
                
                try {
                    const response = await fetch('/api/manager-submit-evaluation', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            manager_id: managerId,
                            employee_id: employeeId,
                            criteria: criteria,
                            notes: notes
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showAlert('تم حفظ التقييم بنجاح', 'success');
                        bootstrap.Modal.getInstance(document.getElementById('evaluationModal')).hide();
                        loadEmployees(); // إعادة تحميل القائمة
                    } else {
                        showAlert(result.error || 'خطأ في حفظ التقييم', 'danger');
                    }
                } catch (error) {
                    showAlert('خطأ في الاتصال', 'danger');
                }
            }

            // تحديث الإحصائيات
            function updateStats() {
                const total = currentEmployees.length;
                const completed = currentEmployees.filter(e => e.is_evaluated).length;
                const pending = total - completed;
                
                document.getElementById('total-employees').textContent = total;
                document.getElementById('completed-count').textContent = completed;
                document.getElementById('pending-count').textContent = pending;
            }

            // تحديث فترة التقييم الحالية
            function updateCurrentPeriod() {
                const now = new Date();
                const months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                              'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'];
                const currentMonth = months[now.getMonth()];
                const currentYear = now.getFullYear();
                
                document.getElementById('current-period').textContent = `${currentMonth} ${currentYear}`;
            }

            // عرض التنبيهات
            function showAlert(message, type) {
                const alertContainer = document.getElementById('alert-container');
                const alert = document.createElement('div');
                alert.className = `alert alert-${type} alert-dismissible fade show`;
                alert.innerHTML = `
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                alertContainer.appendChild(alert);
                
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 5000);
            }
        </script>
    </body>
    </html>
    """
    
    return render_template_string(manager_html, manager_id=manager_id)

@manager_bp.route('/api/manager-login/<int:manager_id>', methods=['POST'])
def manager_login(manager_id):
    """تسجيل دخول المدير"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        managers = load_managers()
        manager_key = str(manager_id)
        
        if manager_key not in managers:
            # إنشاء مدير جديد بكلمة مرور افتراضية
            managers[manager_key] = {
                'name': f'مدير {manager_id}',
                'password': '123456',  # كلمة مرور افتراضية
                'department_id': manager_id,
                'created_at': datetime.now().isoformat()
            }
            save_managers(managers)
        
        manager = managers[manager_key]
        
        if manager['password'] == password:
            return jsonify({
                'success': True,
                'manager_name': manager['name']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'كلمة مرور خاطئة'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manager_bp.route('/api/manager-employees/<int:manager_id>')
def get_manager_employees(manager_id):
    """الحصول على موظفي المدير"""
    try:
        # بيانات تجريبية - يمكن استبدالها بالبيانات الفعلية
        employees_data = [
            {
                'id': 1,
                'name': 'أحمد محمد علي',
                'employee_number': 'EMP001',
                'job_title': 'مطور برمجيات',
                'is_evaluated': False
            },
            {
                'id': 2,
                'name': 'فاطمة أحمد محمد',
                'employee_number': 'EMP002',
                'job_title': 'مديرة مبيعات',
                'is_evaluated': False
            }
        ]
        
        # معايير التقييم حسب الإدارة
        criteria_by_department = {
            1: ['الكفاءة التقنية', 'حل المشاكل', 'جودة الكود', 'التعاون مع الفريق', 'التعلم المستمر'],
            2: ['تحقيق الأهداف', 'خدمة العملاء', 'التفاوض', 'إدارة الوقت', 'العمل الجماعي'],
            3: ['الكفاءة التقنية', 'حل المشاكل', 'جودة الكود', 'التعاون مع الفريق', 'التعلم المستمر', 'الابتكار', 'إدارة المشاريع', 'القيادة']
        }
        
        criteria = criteria_by_department.get(manager_id, ['المعيار الأول', 'المعيار الثاني', 'المعيار الثالث'])
        
        return jsonify({
            'success': True,
            'employees': employees_data,
            'criteria': criteria
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manager_bp.route('/api/manager-submit-evaluation', methods=['POST'])
def submit_manager_evaluation():
    """حفظ تقييم المدير"""
    try:
        data = request.get_json()
        manager_id = data.get('manager_id')
        employee_id = data.get('employee_id')
        criteria = data.get('criteria')
        notes = data.get('notes', '')
        
        current_month, current_year = get_current_evaluation_month()
        
        # التحقق من أن فترة التقييم نشطة
        if not is_evaluation_period_active(current_month, current_year):
            return jsonify({
                'success': False,
                'error': 'فترة التقييم غير نشطة حالياً'
            }), 400
        
        # حفظ التقييم (هنا يمكن حفظه في قاعدة البيانات)
        evaluation_data = {
            'manager_id': manager_id,
            'employee_id': employee_id,
            'criteria': criteria,
            'notes': notes,
            'month': current_month,
            'year': current_year,
            'submitted_at': datetime.now().isoformat()
        }
        
        # للتبسيط، سنحفظ في ملف JSON
        evaluations_file = 'manager_evaluations.json'
        evaluations = []
        
        if os.path.exists(evaluations_file):
            with open(evaluations_file, 'r', encoding='utf-8') as f:
                evaluations = json.load(f)
        
        evaluations.append(evaluation_data)
        
        with open(evaluations_file, 'w', encoding='utf-8') as f:
            json.dump(evaluations, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'تم حفظ التقييم بنجاح'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

