from flask import Blueprint, request, jsonify, render_template_string
from src.models.user import db
from src.models.employee import Employee
from src.models.evaluation import MonthlyEvaluation, EvaluationScore
from src.models.department import Department, EvaluationCriteria
import hashlib
import secrets

share_bp = Blueprint('share', __name__)

def generate_share_token(employee_id):
    """إنشاء رمز مشاركة فريد للموظف"""
    secret = secrets.token_urlsafe(16)
    data = f"{employee_id}_{secret}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def generate_public_token():
    """إنشاء رمز مشاركة عام لجميع الموظفين"""
    secret = secrets.token_urlsafe(16)
    data = f"public_{secret}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]

@share_bp.route('/share/employee/<int:employee_id>', methods=['POST'])
def create_employee_share_link(employee_id):
    """إنشاء رابط مشاركة فردي للموظف"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # إنشاء رمز المشاركة
        share_token = generate_share_token(employee_id)
        
        # حفظ رمز المشاركة في قاعدة البيانات (يمكن إضافة جدول منفصل لاحقاً)
        # للآن سنستخدم نظام بسيط
        
        share_url = f"/share/view/{share_token}"
        
        return jsonify({
            'share_url': share_url,
            'share_token': share_token,
            'employee_name': employee.full_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@share_bp.route('/share/public', methods=['POST'])
def create_public_share_link():
    """إنشاء رابط مشاركة عام لجميع الموظفين"""
    try:
        # إنشاء رمز المشاركة العام
        share_token = generate_public_token()
        
        share_url = f"/share/public/{share_token}"
        
        return jsonify({
            'share_url': share_url,
            'share_token': share_token
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@share_bp.route('/share/view/<share_token>')
def view_employee_share(share_token):
    """عرض تقييم موظف محدد عبر رابط المشاركة"""
    try:
        # البحث عن الموظف بناءً على رمز المشاركة
        # هذا تطبيق مبسط - في التطبيق الحقيقي يجب حفظ الرموز في قاعدة البيانات
        
        # للآن سنعرض صفحة عامة تطلب من المستخدم إدخال معرف الموظف
        return render_template_string(EMPLOYEE_SHARE_TEMPLATE, share_token=share_token)
        
    except Exception as e:
        return f"خطأ في تحميل الصفحة: {str(e)}", 500

@share_bp.route('/share/public/<share_token>')
def view_public_share(share_token):
    """عرض جميع الموظفين عبر رابط المشاركة العام"""
    try:
        return render_template_string(PUBLIC_SHARE_TEMPLATE, share_token=share_token)
        
    except Exception as e:
        return f"خطأ في تحميل الصفحة: {str(e)}", 500

@share_bp.route('/api/share/employee-data/<share_token>/<int:employee_id>')
def get_employee_share_data(share_token, employee_id):
    """الحصول على بيانات الموظف للمشاركة"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # الحصول على تقييمات الموظف
        evaluations = MonthlyEvaluation.query.filter_by(employee_id=employee_id).order_by(
            MonthlyEvaluation.evaluation_year, MonthlyEvaluation.evaluation_month
        ).all()
        
        # تنظيم البيانات
        months_ar = [
            '', 'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ]
        
        evaluation_data = []
        for evaluation in evaluations:
            eval_dict = evaluation.to_dict()
            eval_dict['month_name'] = months_ar[evaluation.evaluation_month]
            evaluation_data.append(eval_dict)
        
        return jsonify({
            'employee': {
                'full_name': employee.full_name,
                'employee_number': employee.employee_number,
                'job_title': employee.job_title,
                'department_name': employee.department.name
            },
            'evaluations': evaluation_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@share_bp.route('/api/share/public-data/<share_token>')
def get_public_share_data(share_token):
    """الحصول على بيانات جميع الموظفين للمشاركة العامة"""
    try:
        employees = Employee.query.all()
        
        employees_data = []
        for employee in employees:
            evaluations = MonthlyEvaluation.query.filter_by(employee_id=employee.id).all()
            
            # حساب المتوسط العام
            total_average = 0
            evaluation_count = len(evaluations)
            
            if evaluation_count > 0:
                for evaluation in evaluations:
                    total_average += evaluation.get_average_score()
                total_average = total_average / evaluation_count
            
            employees_data.append({
                'id': employee.id,
                'full_name': employee.full_name,
                'employee_number': employee.employee_number,
                'job_title': employee.job_title,
                'department_name': employee.department.name,
                'evaluation_count': evaluation_count,
                'overall_average': round(total_average, 2) if evaluation_count > 0 else 0
            })
        
        return jsonify({'employees': employees_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# قوالب HTML للصفحات المشتركة
EMPLOYEE_SHARE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقييم الموظف - نظام تقييم الموظفين</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Tajawal', sans-serif; background-color: #f8f9fa; }
        .navbar-brand { font-weight: 700; }
        .card { box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); border: 1px solid rgba(0, 0, 0, 0.125); }
        .chart-container { position: relative; height: 300px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-chart-line me-2"></i>
                نظام تقييم الموظفين - عرض مشترك
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-user me-2"></i>
                            تقييم الموظف
                        </h5>
                    </div>
                    <div class="card-body">
                        <div id="loading" class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">جاري التحميل...</span>
                            </div>
                            <p class="mt-2">جاري تحميل بيانات التقييم...</p>
                        </div>
                        
                        <div id="content" style="display: none;">
                            <!-- معلومات الموظف -->
                            <div id="employee-info" class="mb-4"></div>
                            
                            <!-- الرسوم البيانية -->
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">متوسط التقييمات الشهرية</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="chart-container">
                                                <canvas id="averageChart"></canvas>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">تفاصيل التقييمات</h6>
                                        </div>
                                        <div class="card-body">
                                            <div id="evaluations-table"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div id="error" style="display: none;" class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <span id="error-message"></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // تحميل بيانات الموظف
        async function loadEmployeeData() {
            try {
                // للتبسيط، سنطلب من المستخدم إدخال معرف الموظف
                const employeeId = prompt('يرجى إدخال معرف الموظف:');
                if (!employeeId) return;
                
                const response = await fetch(`/api/share/employee-data/{{ share_token }}/${employeeId}`);
                
                if (response.ok) {
                    const data = await response.json();
                    displayEmployeeData(data);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                } else {
                    throw new Error('فشل في تحميل البيانات');
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error-message').textContent = error.message;
            }
        }
        
        function displayEmployeeData(data) {
            // عرض معلومات الموظف
            document.getElementById('employee-info').innerHTML = `
                <div class="row">
                    <div class="col-md-3"><strong>الاسم:</strong> ${data.employee.full_name}</div>
                    <div class="col-md-3"><strong>الرقم الوظيفي:</strong> ${data.employee.employee_number}</div>
                    <div class="col-md-3"><strong>المسمى الوظيفي:</strong> ${data.employee.job_title}</div>
                    <div class="col-md-3"><strong>الإدارة:</strong> ${data.employee.department_name}</div>
                </div>
            `;
            
            // إنشاء الرسم البياني
            createChart(data.evaluations);
            
            // عرض جدول التقييمات
            createEvaluationsTable(data.evaluations);
        }
        
        function createChart(evaluations) {
            const ctx = document.getElementById('averageChart').getContext('2d');
            
            const labels = evaluations.map(eval => `${eval.month_name} ${eval.evaluation_year}`);
            const averages = evaluations.map(eval => eval.scores.reduce((sum, score) => sum + score.score, 0) / eval.scores.length);
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'متوسط التقييم',
                        data: averages,
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 5
                        }
                    }
                }
            });
        }
        
        function createEvaluationsTable(evaluations) {
            let tableHTML = `
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>الشهر</th>
                                <th>السنة</th>
                                <th>المتوسط</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            evaluations.forEach(eval => {
                const average = eval.scores.reduce((sum, score) => sum + score.score, 0) / eval.scores.length;
                tableHTML += `
                    <tr>
                        <td>${eval.month_name}</td>
                        <td>${eval.evaluation_year}</td>
                        <td>${average.toFixed(2)}</td>
                    </tr>
                `;
            });
            
            tableHTML += '</tbody></table></div>';
            document.getElementById('evaluations-table').innerHTML = tableHTML;
        }
        
        // تحميل البيانات عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', loadEmployeeData);
    </script>
</body>
</html>
'''

PUBLIC_SHARE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>جميع الموظفين - نظام تقييم الموظفين</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Tajawal', sans-serif; background-color: #f8f9fa; }
        .navbar-brand { font-weight: 700; }
        .card { box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); border: 1px solid rgba(0, 0, 0, 0.125); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-chart-line me-2"></i>
                نظام تقييم الموظفين - عرض عام
            </a>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-users me-2"></i>
                            جميع الموظفين وتقييماتهم
                        </h5>
                    </div>
                    <div class="card-body">
                        <div id="loading" class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">جاري التحميل...</span>
                            </div>
                            <p class="mt-2">جاري تحميل بيانات الموظفين...</p>
                        </div>
                        
                        <div id="content" style="display: none;">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>الاسم الكامل</th>
                                            <th>الرقم الوظيفي</th>
                                            <th>المسمى الوظيفي</th>
                                            <th>الإدارة</th>
                                            <th>عدد التقييمات</th>
                                            <th>المتوسط العام</th>
                                        </tr>
                                    </thead>
                                    <tbody id="employees-table">
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div id="error" style="display: none;" class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <span id="error-message"></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // تحميل بيانات جميع الموظفين
        async function loadEmployeesData() {
            try {
                const response = await fetch(`/api/share/public-data/{{ share_token }}`);
                
                if (response.ok) {
                    const data = await response.json();
                    displayEmployeesData(data.employees);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                } else {
                    throw new Error('فشل في تحميل البيانات');
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error-message').textContent = error.message;
            }
        }
        
        function displayEmployeesData(employees) {
            const tbody = document.getElementById('employees-table');
            tbody.innerHTML = '';
            
            employees.forEach(employee => {
                const row = document.createElement('tr');
                
                // تحديد لون الصف حسب الأداء
                let rowClass = '';
                if (employee.overall_average >= 4) {
                    rowClass = 'table-success';
                } else if (employee.overall_average >= 3) {
                    rowClass = 'table-warning';
                } else if (employee.overall_average > 0) {
                    rowClass = 'table-danger';
                }
                
                row.className = rowClass;
                row.innerHTML = `
                    <td>${employee.full_name}</td>
                    <td>${employee.employee_number}</td>
                    <td>${employee.job_title}</td>
                    <td>${employee.department_name}</td>
                    <td>${employee.evaluation_count}</td>
                    <td>${employee.overall_average > 0 ? employee.overall_average : 'لا توجد تقييمات'}</td>
                `;
                
                tbody.appendChild(row);
            });
        }
        
        // تحميل البيانات عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', loadEmployeesData);
    </script>
</body>
</html>
'''

