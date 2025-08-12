// متغيرات عامة
let departments = [];
let employees = [];
let currentEmployee = null;
let averageChart = null;
let criteriaChart = null;

// تهيئة التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// تهيئة التطبيق
async function initializeApp() {
    try {
        // تهيئة الإدارات
        await initializeDepartments();
        
        // تحميل البيانات الأساسية
        await loadDepartments();
        await loadEmployees();
        
        // تهيئة النماذج
        setupForms();
        
        // تهيئة السنوات
        setupYears();
        
        showAlert('تم تحميل النظام بنجاح', 'success');
    } catch (error) {
        console.error('خطأ في تهيئة التطبيق:', error);
        showAlert('خطأ في تحميل النظام', 'danger');
    }
}

// تهيئة الإدارات الافتراضية
async function initializeDepartments() {
    try {
        const response = await fetch('/api/init-departments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('تهيئة الإدارات:', result.message);
        }
    } catch (error) {
        console.error('خطأ في تهيئة الإدارات:', error);
    }
}

// تحميل الإدارات
async function loadDepartments() {
    try {
        const response = await fetch('/api/departments');
        if (response.ok) {
            departments = await response.json();
            populateDepartmentSelects();
        }
    } catch (error) {
        console.error('خطأ في تحميل الإدارات:', error);
        showAlert('خطأ في تحميل الإدارات', 'danger');
    }
}

// تحميل الموظفين
async function loadEmployees() {
    try {
        const response = await fetch('/api/employees');
        if (response.ok) {
            employees = await response.json();
            populateEmployeeSelects();
            populateEmployeesTable();
        }
    } catch (error) {
        console.error('خطأ في تحميل الموظفين:', error);
        showAlert('خطأ في تحميل الموظفين', 'danger');
    }
}

// ملء قوائم الإدارات
function populateDepartmentSelects() {
    const departmentSelect = document.getElementById('department');
    departmentSelect.innerHTML = '<option value="">اختر الإدارة</option>';
    
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        departmentSelect.appendChild(option);
    });
}

// ملء قوائم الموظفين
function populateEmployeeSelects() {
    const selects = ['eval-employee', 'view-employee'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">اختر الموظف</option>';
        
        employees.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.id;
            option.textContent = `${emp.full_name} (${emp.employee_number})`;
            select.appendChild(option);
        });
    });
}

// ملء جدول الموظفين
function populateEmployeesTable() {
    const tbody = document.getElementById('employees-table');
    tbody.innerHTML = '';
    
    employees.forEach(emp => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${emp.employee_number}</td>
            <td>${emp.full_name}</td>
            <td>${emp.job_title}</td>
            <td>${emp.department_name || 'غير محدد'}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteEmployee(${emp.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// إعداد السنوات
function setupYears() {
    const currentYear = new Date().getFullYear();
    const yearSelects = ['eval-year', 'view-year'];
    
    yearSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">اختر السنة</option>';
        
        for (let year = currentYear - 2; year <= currentYear + 1; year++) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            if (year === currentYear) {
                option.selected = true;
            }
            select.appendChild(option);
        }
    });
}

// إعداد النماذج
function setupForms() {
    // نموذج إضافة موظف
    document.getElementById('employee-form').addEventListener('submit', handleEmployeeSubmit);
    
    // نموذج إضافة تقييم
    document.getElementById('evaluation-form').addEventListener('submit', handleEvaluationSubmit);
    
    // تغيير الموظف في نموذج التقييم
    document.getElementById('eval-employee').addEventListener('change', handleEmployeeChange);
}

// معالجة إرسال نموذج الموظف
async function handleEmployeeSubmit(event) {
    event.preventDefault();
    
    const formData = {
        employee_number: document.getElementById('employee-number').value,
        full_name: document.getElementById('full-name').value,
        job_title: document.getElementById('job-title').value,
        department_id: parseInt(document.getElementById('department').value)
    };
    
    try {
        const response = await fetch('/api/employees', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('تم إضافة الموظف بنجاح', 'success');
            document.getElementById('employee-form').reset();
            await loadEmployees();
        } else {
            showAlert(result.error || 'خطأ في إضافة الموظف', 'danger');
        }
    } catch (error) {
        console.error('خطأ في إضافة الموظف:', error);
        showAlert('خطأ في إضافة الموظف', 'danger');
    }
}

// معالجة تغيير الموظف في نموذج التقييم
async function handleEmployeeChange() {
    const employeeId = document.getElementById('eval-employee').value;
    const criteriaContainer = document.getElementById('criteria-scores');
    
    if (!employeeId) {
        criteriaContainer.innerHTML = '';
        return;
    }
    
    const employee = employees.find(emp => emp.id == employeeId);
    if (!employee) return;
    
    try {
        const response = await fetch(`/api/departments/${employee.department_id}/criteria`);
        if (response.ok) {
            const criteria = await response.json();
            displayCriteriaInputs(criteria);
        }
    } catch (error) {
        console.error('خطأ في تحميل معايير التقييم:', error);
        showAlert('خطأ في تحميل معايير التقييم', 'danger');
    }
}

// عرض حقول إدخال معايير التقييم
function displayCriteriaInputs(criteria) {
    const container = document.getElementById('criteria-scores');
    container.innerHTML = '<h6 class="mb-3">معايير التقييم:</h6>';
    
    criteria.forEach(criterion => {
        const div = document.createElement('div');
        div.className = 'criteria-item';
        div.innerHTML = `
            <label for="criteria-${criterion.id}" class="form-label">
                ${criterion.criteria_name} (من ${criterion.max_score})
            </label>
            <input type="number" 
                   class="form-control" 
                   id="criteria-${criterion.id}" 
                   name="criteria-${criterion.id}"
                   min="0" 
                   max="${criterion.max_score}" 
                   step="0.1"
                   required>
        `;
        container.appendChild(div);
    });
}

// معالجة إرسال نموذج التقييم
async function handleEvaluationSubmit(event) {
    event.preventDefault();
    
    const employeeId = parseInt(document.getElementById('eval-employee').value);
    const month = parseInt(document.getElementById('eval-month').value);
    const year = parseInt(document.getElementById('eval-year').value);
    
    // جمع درجات المعايير
    const scores = [];
    const criteriaInputs = document.querySelectorAll('#criteria-scores input[type="number"]');
    
    criteriaInputs.forEach(input => {
        const criteriaId = parseInt(input.id.replace('criteria-', ''));
        const score = parseFloat(input.value);
        scores.push({
            criteria_id: criteriaId,
            score: score
        });
    });
    
    const evaluationData = {
        employee_id: employeeId,
        evaluation_month: month,
        evaluation_year: year,
        scores: scores
    };
    
    try {
        const response = await fetch('/api/evaluations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(evaluationData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('تم حفظ التقييم بنجاح', 'success');
            document.getElementById('evaluation-form').reset();
            document.getElementById('criteria-scores').innerHTML = '';
        } else {
            showAlert(result.error || 'خطأ في حفظ التقييم', 'danger');
        }
    } catch (error) {
        console.error('خطأ في حفظ التقييم:', error);
        showAlert('خطأ في حفظ التقييم', 'danger');
    }
}

// حذف موظف
async function deleteEmployee(employeeId) {
    if (!confirm('هل أنت متأكد من حذف هذا الموظف؟')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/employees/${employeeId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('تم حذف الموظف بنجاح', 'success');
            await loadEmployees();
        } else {
            const result = await response.json();
            showAlert(result.error || 'خطأ في حذف الموظف', 'danger');
        }
    } catch (error) {
        console.error('خطأ في حذف الموظف:', error);
        showAlert('خطأ في حذف الموظف', 'danger');
    }
}

// تحميل بيانات الموظف للعرض
async function loadEmployeeData() {
    const employeeId = document.getElementById('view-employee').value;
    const year = document.getElementById('view-year').value || new Date().getFullYear();
    
    if (!employeeId) {
        showAlert('يرجى اختيار موظف', 'warning');
        return;
    }
    
    try {
        // تحميل بيانات الرسم البياني
        const response = await fetch(`/api/employees/${employeeId}/evaluations/chart-data?year=${year}`);
        
        if (response.ok) {
            const data = await response.json();
            displayEmployeeInfo(data.employee);
            displayCharts(data);
            displayDetailsTable(data);
            
            document.getElementById('employee-info').style.display = 'block';
            document.getElementById('charts-container').style.display = 'block';
        } else {
            const result = await response.json();
            showAlert(result.error || 'خطأ في تحميل بيانات الموظف', 'danger');
        }
    } catch (error) {
        console.error('خطأ في تحميل بيانات الموظف:', error);
        showAlert('خطأ في تحميل بيانات الموظف', 'danger');
    }
}

// عرض معلومات الموظف
function displayEmployeeInfo(employee) {
    const container = document.getElementById('employee-details');
    container.innerHTML = `
        <p><strong>الاسم:</strong> ${employee.full_name}</p>
        <p><strong>الرقم الوظيفي:</strong> ${employee.employee_number}</p>
        <p><strong>المسمى الوظيفي:</strong> ${employee.job_title}</p>
        <p><strong>الإدارة:</strong> ${employee.department_name}</p>
    `;
}

// عرض الرسوم البيانية
function displayCharts(data) {
    // رسم بياني للمتوسطات
    displayAverageChart(data);
    
    // رسم بياني للمعايير
    displayCriteriaChart(data);
}

// رسم بياني للمتوسطات الشهرية
function displayAverageChart(data) {
    const ctx = document.getElementById('averageChart').getContext('2d');
    
    if (averageChart) {
        averageChart.destroy();
    }
    
    averageChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months,
            datasets: [{
                label: 'متوسط التقييم',
                data: data.average_scores,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        font: {
                            family: 'Tajawal'
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        font: {
                            family: 'Tajawal'
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            family: 'Tajawal'
                        }
                    }
                }
            }
        }
    });
}

// رسم بياني لمعايير التقييم
function displayCriteriaChart(data) {
    const ctx = document.getElementById('criteriaChart').getContext('2d');
    
    if (criteriaChart) {
        criteriaChart.destroy();
    }
    
    const datasets = [];
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
        '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
    ];
    
    let colorIndex = 0;
    for (const [criteriaName, scores] of Object.entries(data.criteria_scores)) {
        datasets.push({
            label: criteriaName,
            data: scores,
            borderColor: colors[colorIndex % colors.length],
            backgroundColor: colors[colorIndex % colors.length] + '20',
            borderWidth: 2,
            fill: false
        });
        colorIndex++;
    }
    
    criteriaChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        font: {
                            family: 'Tajawal'
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        font: {
                            family: 'Tajawal'
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            family: 'Tajawal'
                        }
                    }
                }
            }
        }
    });
}

// عرض جدول التفاصيل
function displayDetailsTable(data) {
    const header = document.getElementById('details-table-header');
    const body = document.getElementById('details-table-body');
    
    // إنشاء رأس الجدول
    header.innerHTML = '<th>الشهر</th>';
    for (const criteriaName of Object.keys(data.criteria_scores)) {
        header.innerHTML += `<th>${criteriaName}</th>`;
    }
    header.innerHTML += '<th>المتوسط</th>';
    
    // إنشاء صفوف الجدول
    body.innerHTML = '';
    for (let i = 0; i < data.months.length; i++) {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${data.months[i]}</td>`;
        
        for (const scores of Object.values(data.criteria_scores)) {
            row.innerHTML += `<td>${scores[i] || '-'}</td>`;
        }
        
        row.innerHTML += `<td><strong>${data.average_scores[i]?.toFixed(1) || '-'}</strong></td>`;
        body.appendChild(row);
    }
}

// التنقل بين الصفحات
function showPage(pageId) {
    // إخفاء جميع الصفحات
    const pages = document.querySelectorAll('.page-content');
    pages.forEach(page => {
        page.style.display = 'none';
    });
    
    // إظهار الصفحة المطلوبة
    document.getElementById(pageId).style.display = 'block';
    
    // تحديث شريط التنقل
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    // إضافة كلاس active للرابط المناسب
    if (pageId === 'input-page') {
        navLinks[0].classList.add('active');
    } else if (pageId === 'view-page') {
        navLinks[1].classList.add('active');
    } else if (pageId === 'overview-page') {
        navLinks[2].classList.add('active');
        // تحميل بيانات الموظفين عند فتح الصفحة
        loadEmployeesOverview();
    } else if (pageId === 'departments-page') {
        navLinks[3].classList.add('active');
        // تحميل بيانات الأقسام عند فتح الصفحة
        loadDepartmentsManagement();
    }
}

// عرض رسائل التنبيه
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // إزالة التنبيه تلقائياً بعد 5 ثوان
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}



// دوال التصدير إلى Excel
async function exportAllEvaluations() {
    try {
        showAlert('جاري تحضير ملف التصدير...', 'info');
        
        const response = await fetch('/api/export/all-evaluations');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `تقييمات_الموظفين_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('تم تصدير الملف بنجاح', 'success');
        } else {
            const result = await response.json();
            showAlert(result.error || 'خطأ في تصدير الملف', 'danger');
        }
    } catch (error) {
        console.error('خطأ في التصدير:', error);
        showAlert('خطأ في تصدير الملف', 'danger');
    }
}

async function exportEmployeeEvaluations() {
    const employeeId = document.getElementById('view-employee').value;
    
    if (!employeeId) {
        showAlert('يرجى اختيار موظف أولاً', 'warning');
        return;
    }
    
    try {
        showAlert('جاري تحضير ملف التصدير...', 'info');
        
        const response = await fetch(`/api/export/employee/${employeeId}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // الحصول على اسم الموظف
            const employee = employees.find(emp => emp.id == employeeId);
            const employeeName = employee ? employee.full_name : 'موظف';
            
            a.download = `تقييم_${employeeName}_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('تم تصدير الملف بنجاح', 'success');
        } else {
            const result = await response.json();
            showAlert(result.error || 'خطأ في تصدير الملف', 'danger');
        }
    } catch (error) {
        console.error('خطأ في التصدير:', error);
        showAlert('خطأ في تصدير الملف', 'danger');
    }
}

// تحديث دالة loadEmployeeData لإظهار زر التصدير الفردي
const originalLoadEmployeeData = loadEmployeeData;
loadEmployeeData = async function() {
    await originalLoadEmployeeData();
    
    // إظهار زر تصدير الموظف إذا تم اختيار موظف
    const employeeId = document.getElementById('view-employee').value;
    const exportBtn = document.getElementById('export-employee-btn');
    
    if (employeeId && exportBtn) {
        exportBtn.style.display = 'block';
    }
};



// دوال صفحة استعراض الموظفين
async function loadEmployeesOverview() {
    try {
        showAlert('جاري تحميل بيانات الموظفين...', 'info');
        
        // تحميل جميع الموظفين
        await loadEmployees();
        
        // تحميل الإدارات للفلترة
        await loadDepartmentsFilter();
        
        // تحميل السنوات للفلترة
        setupOverviewYears();
        
        // عرض بطاقات الموظفين
        await displayEmployeesCards();
        
        // إعداد البحث والفلترة
        setupFilters();
        
        showAlert('تم تحميل البيانات بنجاح', 'success');
    } catch (error) {
        console.error('خطأ في تحميل بيانات الموظفين:', error);
        showAlert('خطأ في تحميل البيانات', 'danger');
    }
}

async function loadDepartmentsFilter() {
    const select = document.getElementById('filter-department');
    if (!select) return;
    
    // مسح الخيارات الحالية (عدا الخيار الأول)
    while (select.children.length > 1) {
        select.removeChild(select.lastChild);
    }
    
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        select.appendChild(option);
    });
}

function setupOverviewYears() {
    const select = document.getElementById('filter-year');
    if (!select) return;
    
    // مسح الخيارات الحالية (عدا الخيار الأول)
    while (select.children.length > 1) {
        select.removeChild(select.lastChild);
    }
    
    const currentYear = new Date().getFullYear();
    for (let year = currentYear; year >= currentYear - 5; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        select.appendChild(option);
    }
    
    // تحديد السنة الحالية كافتراضي
    select.value = currentYear;
}

async function displayEmployeesCards() {
    const container = document.getElementById('employees-cards');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (employees.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <i class="fas fa-info-circle me-2"></i>
                    لا توجد بيانات موظفين لعرضها
                </div>
            </div>
        `;
        return;
    }
    
    for (const employee of employees) {
        const card = await createEmployeeCard(employee);
        container.appendChild(card);
    }
}

async function createEmployeeCard(employee) {
    const col = document.createElement('div');
    col.className = 'col-lg-6 col-xl-4 mb-4';
    
    // الحصول على تقييمات الموظف
    const year = document.getElementById('filter-year')?.value || new Date().getFullYear();
    let evaluationData = null;
    
    try {
        const response = await fetch(`/api/employees/${employee.id}/evaluations?year=${year}`);
        if (response.ok) {
            evaluationData = await response.json();
        }
    } catch (error) {
        console.error('خطأ في تحميل تقييمات الموظف:', error);
    }
    
    // حساب المتوسط العام
    let overallAverage = 0;
    let evaluationCount = 0;
    
    if (evaluationData && evaluationData.evaluations) {
        evaluationCount = evaluationData.evaluations.length;
        if (evaluationCount > 0) {
            const totalSum = evaluationData.average_scores.reduce((sum, score) => sum + (score || 0), 0);
            overallAverage = totalSum / evaluationData.average_scores.filter(score => score > 0).length;
        }
    }
    
    // تحديد لون البطاقة حسب الأداء
    let cardClass = 'border-secondary';
    let badgeClass = 'bg-secondary';
    
    if (overallAverage >= 4) {
        cardClass = 'border-success';
        badgeClass = 'bg-success';
    } else if (overallAverage >= 3) {
        cardClass = 'border-warning';
        badgeClass = 'bg-warning';
    } else if (overallAverage > 0) {
        cardClass = 'border-danger';
        badgeClass = 'bg-danger';
    }
    
    col.innerHTML = `
        <div class="card h-100 ${cardClass}">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">${employee.full_name}</h6>
                <span class="badge ${badgeClass}">${overallAverage > 0 ? overallAverage.toFixed(1) : 'لا توجد تقييمات'}</span>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-6">
                        <small class="text-muted">الرقم الوظيفي:</small>
                        <div class="fw-bold">${employee.employee_number}</div>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">المسمى الوظيفي:</small>
                        <div class="fw-bold">${employee.job_title}</div>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-6">
                        <small class="text-muted">الإدارة:</small>
                        <div class="fw-bold">${employee.department_name}</div>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">عدد التقييمات:</small>
                        <div class="fw-bold">${evaluationCount}</div>
                    </div>
                </div>
                
                <!-- رسم بياني صغير -->
                <div class="chart-container" style="height: 200px;">
                    <canvas id="chart-${employee.id}"></canvas>
                </div>
            </div>
            <div class="card-footer">
                <button class="btn btn-primary btn-sm" onclick="viewEmployeeDetails(${employee.id})">
                    <i class="fas fa-eye me-1"></i>
                    عرض التفاصيل
                </button>
                <button class="btn btn-outline-success btn-sm" onclick="exportEmployeeEvaluationsFromCard(${employee.id})">
                    <i class="fas fa-download me-1"></i>
                    تصدير
                </button>
            </div>
        </div>
    `;
    
    // إنشاء الرسم البياني بعد إضافة العنصر للصفحة
    setTimeout(() => {
        createEmployeeChart(employee.id, evaluationData);
    }, 100);
    
    return col;
}

function createEmployeeChart(employeeId, evaluationData) {
    const ctx = document.getElementById(`chart-${employeeId}`);
    if (!ctx) return;
    
    if (!evaluationData || !evaluationData.average_scores) {
        ctx.getContext('2d').fillText('لا توجد بيانات', 50, 100);
        return;
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: evaluationData.months || [],
            datasets: [{
                label: 'متوسط التقييم',
                data: evaluationData.average_scores || [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    display: false
                },
                x: {
                    display: false
                }
            },
            elements: {
                point: {
                    hoverRadius: 5
                }
            }
        }
    });
}

function setupFilters() {
    // فلترة حسب الإدارة
    document.getElementById('filter-department')?.addEventListener('change', filterEmployees);
    
    // فلترة حسب السنة
    document.getElementById('filter-year')?.addEventListener('change', () => {
        displayEmployeesCards();
    });
    
    // البحث في الموظفين
    document.getElementById('search-employee')?.addEventListener('input', filterEmployees);
}

function filterEmployees() {
    const departmentFilter = document.getElementById('filter-department')?.value;
    const searchTerm = document.getElementById('search-employee')?.value.toLowerCase();
    
    const cards = document.querySelectorAll('#employees-cards .col-lg-6');
    
    cards.forEach(card => {
        const employeeCard = card.querySelector('.card');
        const employeeName = employeeCard.querySelector('h6').textContent.toLowerCase();
        const employeeNumber = employeeCard.querySelector('.fw-bold').textContent;
        const departmentName = employeeCard.querySelectorAll('.fw-bold')[2].textContent;
        
        let showCard = true;
        
        // فلترة حسب الإدارة
        if (departmentFilter) {
            const department = departments.find(d => d.id == departmentFilter);
            if (department && departmentName !== department.name) {
                showCard = false;
            }
        }
        
        // فلترة حسب البحث
        if (searchTerm) {
            if (!employeeName.includes(searchTerm) && !employeeNumber.includes(searchTerm)) {
                showCard = false;
            }
        }
        
        card.style.display = showCard ? 'block' : 'none';
    });
}

function viewEmployeeDetails(employeeId) {
    // تحديد الموظف في صفحة عرض التقييمات والانتقال إليها
    document.getElementById('view-employee').value = employeeId;
    showPage('view-page');
    loadEmployeeData();
}

async function exportEmployeeEvaluationsFromCard(employeeId) {
    try {
        showAlert('جاري تحضير ملف التصدير...', 'info');
        
        const response = await fetch(`/api/export/employee/${employeeId}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // الحصول على اسم الموظف
            const employee = employees.find(emp => emp.id == employeeId);
            const employeeName = employee ? employee.full_name : 'موظف';
            
            a.download = `تقييم_${employeeName}_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('تم تصدير الملف بنجاح', 'success');
        } else {
            const result = await response.json();
            showAlert(result.error || 'خطأ في تصدير الملف', 'danger');
        }
    } catch (error) {
        console.error('خطأ في التصدير:', error);
        showAlert('خطأ في تصدير الملف', 'danger');
    }
}


// دوال إدارة الأقسام
let editingDepartmentId = null;

async function loadDepartmentsManagement() {
    try {
        await loadDepartments();
        displayDepartmentsList();
        resetDepartmentForm();
        showAlert('تم تحميل الأقسام بنجاح', 'success');
    } catch (error) {
        console.error('خطأ في تحميل الأقسام:', error);
        showAlert('خطأ في تحميل الأقسام', 'danger');
    }
}

function displayDepartmentsList() {
    const container = document.getElementById('departments-list');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (departments.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                لا توجد أقسام مضافة بعد
            </div>
        `;
        return;
    }
    
    departments.forEach(dept => {
        const deptCard = document.createElement('div');
        deptCard.className = 'card mb-3';
        deptCard.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="card-title">${dept.name}</h6>
                        <p class="card-text text-muted">
                            <small>${dept.criteria_count} معايير تقييم</small>
                        </p>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="editDepartment(${dept.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="deleteDepartment(${dept.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(deptCard);
    });
}

function addCriteria() {
    const criteriaList = document.getElementById('criteria-list');
    const criteriaItem = document.createElement('div');
    criteriaItem.className = 'criteria-item mb-2';
    criteriaItem.innerHTML = `
        <div class="input-group">
            <input type="text" class="form-control" placeholder="اسم المعيار" required>
            <button type="button" class="btn btn-outline-danger" onclick="removeCriteria(this)">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    criteriaList.appendChild(criteriaItem);
}

function removeCriteria(button) {
    const criteriaList = document.getElementById('criteria-list');
    if (criteriaList.children.length > 1) {
        button.closest('.criteria-item').remove();
    } else {
        showAlert('يجب أن يكون هناك معيار واحد على الأقل', 'warning');
    }
}

function resetDepartmentForm() {
    editingDepartmentId = null;
    document.getElementById('department-form').reset();
    
    // إعادة تعيين معايير التقييم
    const criteriaList = document.getElementById('criteria-list');
    criteriaList.innerHTML = `
        <div class="criteria-item mb-2">
            <div class="input-group">
                <input type="text" class="form-control" placeholder="اسم المعيار" required>
                <button type="button" class="btn btn-outline-danger" onclick="removeCriteria(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    // تحديث نص الزر
    const submitBtn = document.querySelector('#department-form button[type="submit"]');
    submitBtn.innerHTML = '<i class="fas fa-save me-1"></i> حفظ القسم';
}

async function editDepartment(departmentId) {
    try {
        const response = await fetch(`/api/departments/${departmentId}`);
        if (response.ok) {
            const department = await response.json();
            
            editingDepartmentId = departmentId;
            
            // ملء النموذج بالبيانات
            document.getElementById('dept-name').value = department.name;
            
            // ملء معايير التقييم
            const criteriaList = document.getElementById('criteria-list');
            criteriaList.innerHTML = '';
            
            department.criteria.forEach(criterion => {
                const criteriaItem = document.createElement('div');
                criteriaItem.className = 'criteria-item mb-2';
                criteriaItem.innerHTML = `
                    <div class="input-group">
                        <input type="text" class="form-control" placeholder="اسم المعيار" value="${criterion.criteria_name}" required>
                        <button type="button" class="btn btn-outline-danger" onclick="removeCriteria(this)">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;
                criteriaList.appendChild(criteriaItem);
            });
            
            // تحديث نص الزر
            const submitBtn = document.querySelector('#department-form button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-save me-1"></i> تحديث القسم';
            
            showAlert('تم تحميل بيانات القسم للتعديل', 'info');
        } else {
            const result = await response.json();
            showAlert(result.error || 'خطأ في تحميل بيانات القسم', 'danger');
        }
    } catch (error) {
        console.error('خطأ في تحميل بيانات القسم:', error);
        showAlert('خطأ في تحميل بيانات القسم', 'danger');
    }
}

async function deleteDepartment(departmentId) {
    if (!confirm('هل أنت متأكد من حذف هذا القسم؟ سيتم حذف جميع معايير التقييم المرتبطة به.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/departments/${departmentId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('تم حذف القسم بنجاح', 'success');
            await loadDepartmentsManagement();
            await loadDepartments(); // تحديث قائمة الأقسام في باقي الصفحات
        } else {
            showAlert(result.error || 'خطأ في حذف القسم', 'danger');
        }
    } catch (error) {
        console.error('خطأ في حذف القسم:', error);
        showAlert('خطأ في حذف القسم', 'danger');
    }
}

// معالجة إرسال نموذج القسم
document.addEventListener('DOMContentLoaded', function() {
    const departmentForm = document.getElementById('department-form');
    if (departmentForm) {
        departmentForm.addEventListener('submit', handleDepartmentSubmit);
    }
});

async function handleDepartmentSubmit(event) {
    event.preventDefault();
    
    const name = document.getElementById('dept-name').value.trim();
    const criteriaInputs = document.querySelectorAll('#criteria-list input[type="text"]');
    
    if (!name) {
        showAlert('يرجى إدخال اسم القسم', 'warning');
        return;
    }
    
    const criteria = [];
    criteriaInputs.forEach(input => {
        const criteriaName = input.value.trim();
        if (criteriaName) {
            criteria.push({ name: criteriaName });
        }
    });
    
    if (criteria.length === 0) {
        showAlert('يرجى إضافة معيار واحد على الأقل', 'warning');
        return;
    }
    
    const data = {
        name: name,
        criteria: criteria
    };
    
    try {
        let url = '/api/departments';
        let method = 'POST';
        
        if (editingDepartmentId) {
            url = `/api/departments/${editingDepartmentId}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(result.message, 'success');
            await loadDepartmentsManagement();
            await loadDepartments(); // تحديث قائمة الأقسام في باقي الصفحات
        } else {
            showAlert(result.error || 'خطأ في حفظ القسم', 'danger');
        }
    } catch (error) {
        console.error('خطأ في حفظ القسم:', error);
        showAlert('خطأ في حفظ القسم', 'danger');
    }
}


// دوال المشاركة
async function createEmployeeShareLink() {
    const employeeId = document.getElementById('view-employee').value;
    
    if (!employeeId) {
        showAlert('يرجى اختيار موظف أولاً', 'warning');
        return;
    }
    
    try {
        showAlert('جاري إنشاء رابط المشاركة...', 'info');
        
        const response = await fetch(`/api/share/employee/${employeeId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // عرض الرابط في نافذة منبثقة
            const fullUrl = window.location.origin + result.share_url;
            
            // إنشاء modal لعرض الرابط
            showShareModal('رابط مشاركة تقييم الموظف', fullUrl, result.employee_name);
            
            showAlert('تم إنشاء رابط المشاركة بنجاح', 'success');
        } else {
            const result = await response.json();
            showAlert(result.error || 'خطأ في إنشاء رابط المشاركة', 'danger');
        }
    } catch (error) {
        console.error('خطأ في إنشاء رابط المشاركة:', error);
        showAlert('خطأ في إنشاء رابط المشاركة', 'danger');
    }
}

async function createPublicShareLink() {
    try {
        showAlert('جاري إنشاء رابط المشاركة العام...', 'info');
        
        const response = await fetch('/api/share/public', {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // عرض الرابط في نافذة منبثقة
            const fullUrl = window.location.origin + result.share_url;
            
            // إنشاء modal لعرض الرابط
            showShareModal('رابط مشاركة جميع الموظفين', fullUrl, 'جميع الموظفين');
            
            showAlert('تم إنشاء رابط المشاركة العام بنجاح', 'success');
        } else {
            const result = await response.json();
            showAlert(result.error || 'خطأ في إنشاء رابط المشاركة', 'danger');
        }
    } catch (error) {
        console.error('خطأ في إنشاء رابط المشاركة:', error);
        showAlert('خطأ في إنشاء رابط المشاركة', 'danger');
    }
}

function showShareModal(title, shareUrl, description) {
    // إنشاء modal إذا لم يكن موجوداً
    let modal = document.getElementById('shareModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'shareModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="shareModalTitle"></h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p id="shareModalDescription"></p>
                        <div class="input-group">
                            <input type="text" class="form-control" id="shareUrlInput" readonly>
                            <button class="btn btn-outline-secondary" type="button" onclick="copyShareUrl()">
                                <i class="fas fa-copy"></i> نسخ
                            </button>
                        </div>
                        <div class="mt-3">
                            <a id="shareUrlLink" href="#" target="_blank" class="btn btn-primary">
                                <i class="fas fa-external-link-alt me-1"></i>
                                فتح الرابط
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    // تحديث محتوى المودال
    document.getElementById('shareModalTitle').textContent = title;
    document.getElementById('shareModalDescription').textContent = `رابط مشاركة: ${description}`;
    document.getElementById('shareUrlInput').value = shareUrl;
    document.getElementById('shareUrlLink').href = shareUrl;
    
    // عرض المودال
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

function copyShareUrl() {
    const input = document.getElementById('shareUrlInput');
    input.select();
    input.setSelectionRange(0, 99999); // للهواتف المحمولة
    
    try {
        document.execCommand('copy');
        showAlert('تم نسخ الرابط بنجاح', 'success');
    } catch (err) {
        console.error('خطأ في نسخ الرابط:', err);
        showAlert('خطأ في نسخ الرابط', 'danger');
    }
}

// تحديث دالة loadEmployeeData لإظهار أزرار المشاركة
const originalLoadEmployeeDataForShare = loadEmployeeData;
loadEmployeeData = async function() {
    await originalLoadEmployeeDataForShare();
    
    // إظهار أزرار التصدير والمشاركة إذا تم اختيار موظف
    const employeeId = document.getElementById('view-employee').value;
    const exportBtn = document.getElementById('export-employee-btn');
    const shareBtn = document.getElementById('share-employee-btn');
    
    if (employeeId) {
        if (exportBtn) exportBtn.style.display = 'block';
        if (shareBtn) shareBtn.style.display = 'block';
    }
};



// ===== دوال الإعدادات والتخصيص =====

// تطبيق موضوع الألوان
function applyColorTheme() {
    const primaryColor = document.getElementById('primary-color').value;
    
    // تطبيق اللون على العناصر المختلفة
    const root = document.documentElement;
    root.style.setProperty('--bs-primary', primaryColor);
    
    // تحديث الألوان في CSS
    const style = document.createElement('style');
    style.textContent = `
        .bg-primary { background-color: ${primaryColor} !important; }
        .btn-primary { background-color: ${primaryColor}; border-color: ${primaryColor}; }
        .btn-primary:hover { background-color: ${adjustBrightness(primaryColor, -20)}; border-color: ${adjustBrightness(primaryColor, -20)}; }
        .text-primary { color: ${primaryColor} !important; }
        .navbar-dark.bg-primary { background-color: ${primaryColor} !important; }
        .card-header.bg-primary { background-color: ${primaryColor} !important; }
    `;
    
    // إزالة الستايل القديم إن وجد
    const oldStyle = document.getElementById('custom-theme');
    if (oldStyle) {
        oldStyle.remove();
    }
    
    style.id = 'custom-theme';
    document.head.appendChild(style);
    
    // حفظ اللون في التخزين المحلي
    localStorage.setItem('primaryColor', primaryColor);
    
    showAlert('تم تطبيق الألوان بنجاح', 'success');
}

// إعادة تعيين الألوان
function resetColors() {
    document.getElementById('primary-color').value = '#0d6efd';
    
    // إزالة الستايل المخصص
    const customStyle = document.getElementById('custom-theme');
    if (customStyle) {
        customStyle.remove();
    }
    
    // إزالة من التخزين المحلي
    localStorage.removeItem('primaryColor');
    
    showAlert('تم إعادة تعيين الألوان', 'info');
}

// تعديل سطوع اللون
function adjustBrightness(hex, percent) {
    const num = parseInt(hex.replace("#", ""), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) + amt;
    const G = (num >> 8 & 0x00FF) + amt;
    const B = (num & 0x0000FF) + amt;
    return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
        (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
        (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
}

// تحديث العلامة التجارية للنظام
function updateSystemBranding() {
    const systemName = document.getElementById('system-name').value;
    const logoFile = document.getElementById('logo-upload').files[0];
    
    // تحديث اسم النظام
    if (systemName) {
        document.getElementById('system-title').innerHTML = `
            <i class="fas fa-chart-line me-2"></i>
            ${systemName}
        `;
        document.title = systemName;
        localStorage.setItem('systemName', systemName);
    }
    
    // تحديث الشعار
    if (logoFile) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const logoUrl = e.target.result;
            document.getElementById('system-title').innerHTML = `
                <img src="${logoUrl}" alt="شعار النظام" style="height: 30px; margin-left: 10px;">
                ${systemName}
            `;
            localStorage.setItem('logoUrl', logoUrl);
        };
        reader.readAsDataURL(logoFile);
    }
    
    showAlert('تم حفظ التغييرات بنجاح', 'success');
}

// ===== دوال Google Sheets =====

// اختبار اتصال Google Sheets
async function testSheetsConnection() {
    const sheetsUrl = document.getElementById('sheets-url').value;
    const apiKey = document.getElementById('sheets-api-key').value;
    
    if (!sheetsUrl || !apiKey) {
        showAlert('يرجى إدخال رابط Google Sheets ومفتاح API', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/test-sheets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sheets_url: sheetsUrl,
                api_key: apiKey
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('تم الاتصال بـ Google Sheets بنجاح', 'success');
        } else {
            showAlert('فشل في الاتصال: ' + result.error, 'danger');
        }
    } catch (error) {
        showAlert('خطأ في الاتصال بـ Google Sheets', 'danger');
    }
}

// حفظ إعدادات Google Sheets
async function saveSheetsSettings() {
    const sheetsUrl = document.getElementById('sheets-url').value;
    const apiKey = document.getElementById('sheets-api-key').value;
    const autoSync = document.getElementById('auto-sync').checked;
    
    try {
        const response = await fetch('/api/save-sheets-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sheets_url: sheetsUrl,
                api_key: apiKey,
                auto_sync: autoSync
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('تم حفظ إعدادات Google Sheets', 'success');
        } else {
            showAlert('خطأ في حفظ الإعدادات: ' + result.error, 'danger');
        }
    } catch (error) {
        showAlert('خطأ في حفظ إعدادات Google Sheets', 'danger');
    }
}

// ===== دوال لوحة المدراء =====

// تحميل إحصائيات المدراء
async function loadManagerStats() {
    const month = document.getElementById('admin-month').value;
    const year = document.getElementById('admin-year').value;
    
    try {
        const response = await fetch(`/api/manager-stats?month=${month}&year=${year}`);
        const data = await response.json();
        
        if (response.ok) {
            // تحديث الإحصائيات
            document.getElementById('total-managers').textContent = data.total_managers;
            document.getElementById('completed-evaluations').textContent = data.completed_evaluations;
            document.getElementById('pending-evaluations').textContent = data.pending_evaluations;
            
            // تحديث جدول المدراء
            updateManagersTable(data.managers);
            
            showAlert('تم تحميل إحصائيات المدراء', 'success');
        } else {
            showAlert('خطأ في تحميل الإحصائيات', 'danger');
        }
    } catch (error) {
        showAlert('خطأ في الاتصال بالخادم', 'danger');
    }
}

// تحديث جدول المدراء
function updateManagersTable(managers) {
    const tbody = document.querySelector('#managers-table tbody');
    tbody.innerHTML = '';
    
    managers.forEach(manager => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${manager.name}</td>
            <td>${manager.department}</td>
            <td>${manager.total_employees}</td>
            <td>${manager.completed_evaluations}</td>
            <td>
                <div class="progress">
                    <div class="progress-bar" role="progressbar" style="width: ${manager.completion_percentage}%">
                        ${manager.completion_percentage}%
                    </div>
                </div>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="copyManagerLink('${manager.link}')">
                    <i class="fas fa-copy"></i> نسخ الرابط
                </button>
            </td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="resetManagerPassword('${manager.id}')">
                    <i class="fas fa-key"></i> إعادة تعيين كلمة المرور
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// إنشاء روابط المدراء
async function generateManagerLinks() {
    try {
        const response = await fetch('/api/generate-manager-links', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('تم إنشاء روابط المدراء بنجاح', 'success');
            loadManagerStats(); // إعادة تحميل الإحصائيات
        } else {
            showAlert('خطأ في إنشاء الروابط: ' + result.error, 'danger');
        }
    } catch (error) {
        showAlert('خطأ في إنشاء روابط المدراء', 'danger');
    }
}

// نسخ رابط المدير
function copyManagerLink(link) {
    navigator.clipboard.writeText(link).then(() => {
        showAlert('تم نسخ الرابط', 'success');
    }).catch(() => {
        showAlert('فشل في نسخ الرابط', 'danger');
    });
}

// إعادة تعيين كلمة مرور المدير
async function resetManagerPassword(managerId) {
    if (!confirm('هل أنت متأكد من إعادة تعيين كلمة مرور هذا المدير؟')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/reset-manager-password/${managerId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(`تم إعادة تعيين كلمة المرور الجديدة: ${result.new_password}`, 'success');
        } else {
            showAlert('خطأ في إعادة تعيين كلمة المرور', 'danger');
        }
    } catch (error) {
        showAlert('خطأ في إعادة تعيين كلمة المرور', 'danger');
    }
}

// تحميل الإعدادات المحفوظة عند بدء التطبيق
function loadSavedSettings() {
    // تحميل اللون المحفوظ
    const savedColor = localStorage.getItem('primaryColor');
    if (savedColor) {
        document.getElementById('primary-color').value = savedColor;
        applyColorTheme();
    }
    
    // تحميل اسم النظام المحفوظ
    const savedName = localStorage.getItem('systemName');
    if (savedName) {
        document.getElementById('system-name').value = savedName;
        document.getElementById('system-title').innerHTML = `
            <i class="fas fa-chart-line me-2"></i>
            ${savedName}
        `;
        document.title = savedName;
    }
    
    // تحميل الشعار المحفوظ
    const savedLogo = localStorage.getItem('logoUrl');
    if (savedLogo) {
        const systemName = savedName || 'مركز تجربة العميل';
        document.getElementById('system-title').innerHTML = `
            <img src="${savedLogo}" alt="شعار النظام" style="height: 30px; margin-left: 10px;">
            ${systemName}
        `;
    }
}

// تحديث دالة showPage لدعم الصفحات الجديدة
const originalShowPage = showPage;
showPage = function(pageId) {
    // إخفاء جميع الصفحات
    const pages = document.querySelectorAll('.page-content');
    pages.forEach(page => page.style.display = 'none');
    
    // إظهار الصفحة المطلوبة
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.style.display = 'block';
        
        // تحميل البيانات حسب الصفحة
        if (pageId === 'admin-dashboard') {
            loadManagerStats();
        } else if (pageId === 'settings-page') {
            loadSavedSettings();
        }
    }
    
    // استدعاء الدالة الأصلية للصفحات الأخرى
    if (typeof originalShowPage === 'function') {
        originalShowPage(pageId);
    }
};

// تحميل الإعدادات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    loadSavedSettings();
});

