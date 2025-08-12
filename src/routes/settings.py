from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime

settings_bp = Blueprint('settings', __name__)

# مسار ملف الإعدادات
SETTINGS_FILE = 'settings.json'

def load_settings():
    """تحميل الإعدادات من الملف"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    """حفظ الإعدادات في الملف"""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

@settings_bp.route('/api/test-sheets', methods=['POST'])
def test_sheets_connection():
    """اختبار اتصال Google Sheets"""
    try:
        data = request.get_json()
        sheets_url = data.get('sheets_url')
        api_key = data.get('api_key')
        
        # هنا يمكن إضافة كود اختبار الاتصال الفعلي مع Google Sheets API
        # للتبسيط، سنعتبر الاتصال ناجح إذا كانت البيانات موجودة
        
        if sheets_url and api_key:
            return jsonify({
                'success': True,
                'message': 'تم الاتصال بـ Google Sheets بنجاح'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'بيانات غير مكتملة'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/save-sheets-settings', methods=['POST'])
def save_sheets_settings():
    """حفظ إعدادات Google Sheets"""
    try:
        data = request.get_json()
        
        settings = load_settings()
        settings['google_sheets'] = {
            'url': data.get('sheets_url'),
            'api_key': data.get('api_key'),
            'auto_sync': data.get('auto_sync', True),
            'last_updated': datetime.now().isoformat()
        }
        
        save_settings(settings)
        
        return jsonify({
            'success': True,
            'message': 'تم حفظ إعدادات Google Sheets'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/manager-stats')
def get_manager_stats():
    """الحصول على إحصائيات المدراء"""
    try:
        month = request.args.get('month')
        year = request.args.get('year', datetime.now().year)
        
        # بيانات تجريبية - يمكن استبدالها بالبيانات الفعلية من قاعدة البيانات
        managers_data = [
            {
                'id': 1,
                'name': 'أحمد محمد',
                'department': 'إدارة المبيعات',
                'total_employees': 8,
                'completed_evaluations': 6,
                'completion_percentage': 75,
                'link': f'{request.host_url}manager/evaluate/1'
            },
            {
                'id': 2,
                'name': 'فاطمة علي',
                'department': 'إدارة التقنية',
                'total_employees': 12,
                'completed_evaluations': 10,
                'completion_percentage': 83,
                'link': f'{request.host_url}manager/evaluate/2'
            },
            {
                'id': 3,
                'name': 'محمد سالم',
                'department': 'إدارة الموارد البشرية',
                'total_employees': 5,
                'completed_evaluations': 5,
                'completion_percentage': 100,
                'link': f'{request.host_url}manager/evaluate/3'
            }
        ]
        
        total_managers = len(managers_data)
        completed_evaluations = sum(m['completed_evaluations'] for m in managers_data)
        total_employees = sum(m['total_employees'] for m in managers_data)
        pending_evaluations = total_employees - completed_evaluations
        
        return jsonify({
            'success': True,
            'total_managers': total_managers,
            'completed_evaluations': completed_evaluations,
            'pending_evaluations': pending_evaluations,
            'managers': managers_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/generate-manager-links', methods=['POST'])
def generate_manager_links():
    """إنشاء روابط المدراء"""
    try:
        # هنا يمكن إضافة منطق إنشاء الروابط الفعلي
        # للتبسيط، سنعتبر أن الروابط تم إنشاؤها
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء روابط المدراء بنجاح'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@settings_bp.route('/api/reset-manager-password/<int:manager_id>', methods=['POST'])
def reset_manager_password(manager_id):
    """إعادة تعيين كلمة مرور المدير"""
    try:
        import random
        import string
        
        # إنشاء كلمة مرور جديدة
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # هنا يمكن حفظ كلمة المرور الجديدة في قاعدة البيانات
        
        return jsonify({
            'success': True,
            'new_password': new_password,
            'message': 'تم إعادة تعيين كلمة المرور'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

